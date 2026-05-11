import time
import random
from db_manager import init_db, update_device_live, get_forced_off_list

def run_generator():
    init_db()
    print("--- ⚡ SQL-Powered Hardware Simulator Started ⚡ ---")
    print("🚀 Press Ctrl+C to stop the generator safely.")

    device_configs = {
        "Air Conditioner": {"base": 2200, "essential": False},
        "Refrigerator": {"base": 250, "essential": True},
        "TV": {"base": 180, "essential": False},
        "Lights": {"base": 80, "essential": True},
        "Fan": {"base": 70, "essential": True},
        "Gaming PC": {"base": 650, "essential": False},
        "Microwave": {"base": 1300, "essential": False},
        "Washing Machine": {"base": 500, "essential": False}
    }

    try:
        while True:
            try:
                # 1. Get manual overrides from SQL
                forced_off = get_forced_off_list()
                total_load = 0

                for name, config in device_configs.items():
                    # If device name is in the 'forced_off' list, it must stay OFF
                    is_on = (name not in forced_off)
                    
                    watts = round(config["base"] * random.uniform(0.98, 1.02), 1) if is_on else 0.0
                    status = "ON" if is_on else "OFF"
                    
                    # 2. Update device in SQL
                    update_device_live(name, watts, status, config["essential"])
                    total_load += watts

                print(f"SQL Updated | Total Load: {total_load:.1f} W")
                time.sleep(1)
                
            except Exception as e:
                print(f"Generator SQL Error: {e}")
                time.sleep(1)
                
    except KeyboardInterrupt:
        # This block catches Ctrl+C and prevents the Traceback error
        print("\n🛑 Generator stopped by user. Cleaning up...")
    finally:
        print("✅ Goodbye!")

if __name__ == "__main__":
    run_generator()