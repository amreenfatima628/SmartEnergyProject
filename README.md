Smart Energy Dashboard Pro ⚡
An automated real-time monitoring and load control system for modern smart homes. This application bridges Python backend logic with a high-performance QML interface to provide live energy insights and automated safety controls.

🚀 Key Features
Real-Time Tracking: Live visualization of Voltage, Current, and Wattage for multiple appliances.

Automated Load Shedding: Automatically turns off high-power, non-essential devices if consumption exceeds a safety limit (e.g., 3000W).

Peak Hour Management: Dynamic alerts and power restrictions during high-tariff periods (e.g., 7:00 PM – 11:00 PM).

Cost Estimation: Real-time billing calculation in PKR based on dynamic unit rates.

Usage History & Reports: Persistent data logging with the ability to export professional PDF reports.

Secure Authentication: Integrated login system and password management utility.

📂 Project Structure
Plaintext

SmartEnergyProject/
├── host_server.py          # Flask backend & QObject bridge logic(web app)
├── main.py                 # Core application & Bridge logic
├── change_pass.py          # Utility for updating login credentials
├── requirements.txt        # Required Python libraries
├── energy_system.db        # SQLite database (Stores history and settings)(created automatically when main.py runs)
├── backend/                # Logic Layer
│   ├── data_generator.py   # Simulates live sensor data
│   ├── db_manager.py       # Database operations (SQL)
│   └── energy_logic.py     # Energy math and billing logic
└── frontend/               # View Layer
    ├── dashboard.qml       # QML User Interface design
    └── index.html          # Dashboard User Interface(web app)
🛠️ Installation & Setup
Clone/Download the project folder.

Create a Virtual Environment:
python -m venv venv

Activate the Environment:
Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate

Install Dependencies:
pip install -r requirements.txt

🚦 Running the Application
To experience the full live simulation, you must run two processes:
Start the Data Simulator:
Open a terminal and run:
python backend/data_generator.py

Launch the Dashboard:
Open a second terminal and run:
python main.py
🔐 Default Credentials
Username: admin
Password: admin123
(Use change_pass.py to update these for security).


->Locall Host
🛠️ Installation & Setup
Clone/Download the project folder.

Create a Virtual Environment:
python -m venv venv
Activate the Environment:
Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate

Install Dependencies:
pip install -r requirements.txt

🚦 Running the WEB Application
To run the system on your local machine and access the interface via a web browser, follow these steps:

1. Initialize the System
The application requires two components to run simultaneously:

Step A: Start the Server
Open a terminal and run the host script. This initializes the database and starts the Flask web server.
python host_server.py
The server will be hosted at http://localhost:5000.

Step B: Start the Data Simulator
Open a second terminal window, activate the virtual environment, and run the simulator to begin generating live energy data.
python backend/data_generator.py

2. Access the Dashboard
Once both scripts are active, open a web browser and navigate to:
http://localhost:5000.
NOTE:(keep in mind that your desktop(on which you install it) and the device(on which you acess it by browser) both must be connected to same WIFI/Internet)

3. Default Credentials
Login to the dashboard using these default settings:
Username: admin
Password: password123
(Use change_pass.py to update these for security).