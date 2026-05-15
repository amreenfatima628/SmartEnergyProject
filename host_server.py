import sys
import os
import threading
import io # Added for PDF memory handling
from datetime import datetime
from fpdf import FPDF 
from flask import Flask, jsonify, request, send_file # send_file added for PDF export
from flask_cors import CORS

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Property, QTimer, Slot, QMetaObject, Qt, Q_ARG

from backend.energy_logic import SmartAppliance
from backend.db_manager import (
    get_all_devices, get_forced_off_list, set_force_off, 
    get_system_value, save_system_value, init_db, verify_user,
    save_daily_log, get_all_history
)

# --- FLASK SERVER SETUP ---
server = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(server)
bridge = None  

@server.route('/')
def serve_index():
    return server.send_static_file('index.html')

class EnergyBridge(QObject):
    dataUpdated = Signal()
    notificationRequested = Signal(str)
    loginSuccess = Signal()
    logoutTriggered = Signal()

    def __init__(self, name="Main System"):
        super().__init__()
        self.appliance = SmartAppliance("name")
        
        # Safe database hydration properties fallbacks
        saved_kwh = get_system_value("total_kwh", 0.0)
        self.appliance.total_kwh = saved_kwh
        
        self._unit_rate = get_system_value("unit_rate", 35.0)
        self._overload_limit = get_system_value("overload_limit", 3000.0)
        self._peak_start = int(get_system_value("peak_start", 19))
        self._peak_end = int(get_system_value("peak_end", 23))
        self._last_archive_date = get_system_value("last_archive_date", datetime.now().strftime("%Y-%m-%d"))
        self._alert_buffer = ""

        # Master clock execution loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(1000)

    @Property(float, notify=dataUpdated)
    def totalWatts(self): 
        return getattr(self.appliance, 'total_watts', 0.0)

    @Property(float, notify=dataUpdated)
    def totalCost(self): 
        return getattr(self.appliance, 'total_kwh', 0.0) * self._unit_rate

    @Property(list, notify=dataUpdated)
    def deviceNames(self):
        # Defends against plural structural mismatches dynamically
        if hasattr(self.appliance, 'devices'):
            return list(self.appliance.devices.keys())
        elif hasattr(self.appliance, 'names') and isinstance(self.appliance.names, dict):
            return list(self.appliance.names.keys())
        return []

    @Property(list, notify=dataUpdated)
    def historyLogs(self):
        # Exposes persistent data rows directly to QML ListView
        return get_all_history()

    @Slot(str)
    def toggleDevice(self, name):
        forced_off = get_forced_off_list()
        new_state = 0 if name in forced_off else 1
        set_force_off(name, new_state)
        self.refresh_data()

    def refresh_data(self):
        if hasattr(self.appliance, 'update_usage'):
            self.appliance.update_usage(self.appliance.total_kwh)
        save_system_value("total_kwh", self.appliance.total_kwh)
        
        if datetime.now().strftime("%Y-%m-%d") != self._last_archive_date:
            date_str = datetime.now().strftime("%Y-%m-%d")
            save_daily_log(date_str, self.appliance.total_kwh, self.totalCost)
            self._last_archive_date = date_str
            save_system_value("last_archive_date", date_str)
            
        if self.totalWatts > self._overload_limit:
            self._alert_buffer = "⚠️ OVERLOAD DETECTED!"
            self.notificationRequested.emit(self._alert_buffer)
        else:
            self._alert_buffer = ""
            
        self.dataUpdated.emit()

# --- FLASK API ROUTES ---
@server.route('/api/status', methods=['GET'])
def get_status():
    global bridge
    if bridge:
        dev_map = {}
        forced_off = get_forced_off_list()
        for name in bridge.deviceNames:
            wattage = 0.0
            if hasattr(bridge.appliance, 'devices') and name in bridge.appliance.devices:
                wattage = bridge.appliance.devices[name].watts
            
            dev_map[name] = {
                "watts": wattage,
                "status": "OFF" if name in forced_off else "ON"
            }
        return jsonify({
            "currentWatts": bridge.totalWatts,
            "currentCost": bridge.totalCost,       
            "deviceNames": bridge.deviceNames,
            "deviceData": dev_map,
            "alertMessage": bridge._alert_buffer
        })
    return jsonify({"error": "System engine initializing..."}), 500

@server.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    if verify_user(data.get("username"), data.get("password")):
        return jsonify({"status": "Success"})
    return jsonify({"status": "Denied"}), 401

@server.route('/api/toggle', methods=['POST'])
def api_toggle():
    data = request.json or {}
    if bridge and data.get("device"):
        QMetaObject.invokeMethod(bridge, "toggleDevice", Qt.QueuedConnection, Q_ARG(str, data["device"]))
        return jsonify({"status": "Success"})
    return jsonify({"status": "Failed"}), 400

@server.route('/api/history', methods=['GET'])
def api_history():
    return jsonify(get_all_history())

# --- NEW: PDF Export Route ---
@server.route('/api/export_pdf', methods=['GET'])
def api_export_pdf():
    history = get_all_history()
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="Smart Energy Pro - Lifetime History Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    
    # Table Header
    pdf.cell(60, 10, "Date", border=1, align='C')
    pdf.cell(60, 10, "Energy (kWh)", border=1, align='C')
    pdf.cell(60, 10, "Cost (PKR)", border=1, ln=True, align='C')
    
    # Table Content
    for row in history:
        pdf.cell(60, 10, str(row['date']), border=1, align='C')
        pdf.cell(60, 10, f"{row['kwh']:.2f}", border=1, align='C')
        pdf.cell(60, 10, f"{row['cost']:.2f}", border=1, ln=True, align='C')
        
    try:
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
    except AttributeError:
        # Fallback for newer fpdf2 versions
        pdf_bytes = bytes(pdf.output())
        
    pdf_output = io.BytesIO(pdf_bytes)
    
    return send_file(
        pdf_output, 
        download_name="smart_energy_report.pdf", 
        as_attachment=True, 
        mimetype='application/pdf'
    )

def run_hosting():
    server.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# --- STARTUP RUNTIME ASYNC HANDSHAKE ---
if __name__ == "__main__":
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
    qt_app = QGuiApplication(sys.argv)
    
    init_db()
    
    bridge = EnergyBridge("Smart Home")
    
    threading.Thread(target=run_hosting, daemon=True).start()

    print("\n" + "="*50)
    print("🚀 SMART ENERGY PRO AUTOMATION CORE RUNNING")
    print("📡 Local Desktop Client and API Endpoints Mapped Successfully")
    print("="*50 + "\n")

    sys.exit(qt_app.exec())

def start_app():
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
    app = QGuiApplication(sys.argv)
    bridge = EnergyBridge()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", bridge)
    
    qml_path = os.path.join(os.path.dirname(__file__), "frontend/dashboard.qml")
    engine.load(qml_path)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

# This allows main.py to still run by itself if needed
if __name__ == "__main__":
    start_app()