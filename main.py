import sys
import os
from datetime import datetime
from fpdf import FPDF 
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Property, QTimer, Slot
from backend.energy_logic import SmartAppliance
from backend.db_manager import (
    get_all_devices, get_forced_off_list, set_force_off, 
    get_system_value, save_system_value, init_db, verify_user,
    save_daily_log, get_all_history
)

class EnergyBridge(QObject):
    dataUpdated = Signal()
    notificationRequested = Signal(str)
    loginSuccess = Signal()
    logoutTriggered = Signal()

    def __init__(self):
        super().__init__()
        init_db()
        
        saved_kwh = get_system_value("total_kwh", 0.0)
        self._unit_rate = get_system_value("unit_rate", 35.0)
        self._overload_limit = get_system_value("overload_limit", 3000.0)
        # --- NEW: Peak Hour Settings ---
        self._peak_start = int(get_system_value("peak_start", 19))
        self._peak_end = int(get_system_value("peak_end", 23))
        
        self._last_archive_date = get_system_value("last_archive_date", datetime.now().strftime("%Y-%m-%d"))
        
        self.appliance = SmartAppliance("Home", initial_kwh=saved_kwh)
        self.appliance.rate = self._unit_rate 
        
        self._device_list = {}
        self._watts = 0.0
        self._peak_notified = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(1000)

    def refresh_data(self):
        try:
            self._device_list = get_all_devices()
            self._watts = sum(d['watts'] for d in self._device_list.values())
            self.appliance.update_usage(self._watts)
            save_system_value("total_kwh", self.appliance.total_kwh)
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            if current_date != self._last_archive_date:
                self.auto_archive_daily()
            
            self.check_peak_logic()
            if self._watts > self._overload_limit: 
                self.auto_shed_logic("OVERLOAD")
            
            self.dataUpdated.emit()
        except Exception as e:
            print(f"Main App SQL Error: {e}")

    def check_peak_logic(self):
        current_hour = datetime.now().hour
        # Logic now uses dynamic start/end
        is_peak = self._peak_start <= current_hour < self._peak_end
        if is_peak:
            if not self._peak_notified:
                self.notificationRequested.emit(f"🌙 PEAK HOURS ACTIVE ({self._peak_start}:00 - {self._peak_end}:00)")
                self._peak_notified = True
            self.auto_shed_logic("PEAK HOURS")
        else:
            self._peak_notified = False

    @Slot(int)
    def setPeakStart(self, val):
        self._peak_start = val
        save_system_value("peak_start", val)
        self.dataUpdated.emit()

    @Slot(int)
    def setPeakEnd(self, val):
        self._peak_end = val
        save_system_value("peak_end", val)
        self.dataUpdated.emit()

    @Property(int, notify=dataUpdated)
    def peakStart(self): return self._peak_start

    @Property(int, notify=dataUpdated)
    def peakEnd(self): return self._peak_end

    @Property(str, notify=dataUpdated)
    def peakCountdown(self):
        now = datetime.now()
        h_now = now.hour
        if h_now < self._peak_start:
            target = now.replace(hour=self._peak_start, minute=0, second=0, microsecond=0)
        elif self._peak_start <= h_now < self._peak_end:
            target = now.replace(hour=self._peak_end, minute=0, second=0, microsecond=0)
        else: 
            return "OFF PEAK"
        diff = target - now
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @Property(bool, notify=dataUpdated)
    def isPeakMode(self): 
        return self._peak_start <= datetime.now().hour < self._peak_end

    # ... [Rest of the slots/properties from previous code remain the same] ...
    
    @Slot()
    def logout(self): self.logoutTriggered.emit()

    @Slot()
    def exportPDF(self):
        try:
            history = get_all_history()
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Smart Home Energy Report", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
            pdf.ln(10)
            pdf.set_fill_color(30, 30, 30); pdf.set_text_color(255, 255, 255)
            pdf.cell(60, 10, "Date", 1, 0, 'C', True)
            pdf.cell(60, 10, "Usage (kWh)", 1, 0, 'C', True)
            pdf.cell(60, 10, "Cost (PKR)", 1, 1, 'C', True)
            pdf.set_text_color(0, 0, 0)
            for entry in history:
                pdf.cell(60, 10, str(entry['date']), 1)
                pdf.cell(60, 10, str(entry['kwh']), 1)
                pdf.cell(60, 10, str(entry['cost']), 1, 1)
            path = f"Energy_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(path)
            self.notificationRequested.emit(f"✅ Report Exported: {path}")
        except Exception as e:
            self.notificationRequested.emit(f"❌ Export Failed: {str(e)}")

    @Slot(float)
    def setUnitRate(self, val):
        self._unit_rate = val; self.appliance.rate = val
        save_system_value("unit_rate", val); self.dataUpdated.emit()

    @Slot(float)
    def setOverloadLimit(self, val):
        self._overload_limit = val
        save_system_value("overload_limit", val); self.dataUpdated.emit()

    @Property(float, notify=dataUpdated)
    def unitRate(self): return self._unit_rate
    @Property(float, notify=dataUpdated)
    def overloadLimit(self): return self._overload_limit
    @Property(float, notify=dataUpdated)
    def currentWatts(self): return self._watts
    @Property(float, notify=dataUpdated)
    def currentCost(self): return self.appliance.total_kwh * self._unit_rate
    @Property(bool, notify=dataUpdated)
    def isOverload(self): return self._watts > self._overload_limit
    @Property(list, notify=dataUpdated)
    def deviceNames(self): return list(self._device_list.keys())
    @Property(dict, notify=dataUpdated)
    def deviceData(self): return self._device_list
    @Property(list, notify=dataUpdated)
    def historyLogs(self): return get_all_history()

    def auto_shed_logic(self, reason):
        forced_off = get_forced_off_list()
        changed = False
        for name, info in self._device_list.items():
            if not info.get("essential") and info.get("status") == "ON":
                if name not in forced_off:
                    set_force_off(name, True)
                    changed = True
        if changed and reason == "OVERLOAD":
            self.notificationRequested.emit("⚠️ OVERLOAD: Heavy devices automatically disabled!")

    @Slot(str)
    def toggleDevice(self, name):
        forced_off = get_forced_off_list()
        new_state = 0 if name in forced_off else 1
        set_force_off(name, new_state); self.refresh_data()

    @Slot(str, str)
    def login(self, username, password):
        if verify_user(username, password): self.loginSuccess.emit()
        else: self.notificationRequested.emit("❌ Invalid Username or Password")

    def auto_archive_daily(self):
        total_now = self.appliance.total_kwh
        last_total = get_system_value("last_total_at_archive", 0.0)
        daily_usage = total_now - last_total
        if daily_usage > 0:
            save_daily_log(self._last_archive_date, round(daily_usage, 2), round(daily_usage * self._unit_rate, 2))
        self._last_archive_date = datetime.now().strftime("%Y-%m-%d")
        save_system_value("last_archive_date", self._last_archive_date)
        save_system_value("last_total_at_archive", total_now)

if __name__ == "__main__":
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
    app = QGuiApplication(sys.argv)
    bridge = EnergyBridge()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", bridge)
    qml_path = os.path.join(os.path.dirname(__file__), "frontend/dashboard.qml")
    engine.load(qml_path)
    if not engine.rootObjects(): sys.exit(-1)
    sys.exit(app.exec())