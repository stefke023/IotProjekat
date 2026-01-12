import os
import subprocess
import sys

def usage():
    print("Usage: python launcher.py [host|publisher|subscriber]")
    sys.exit(1)

def main():
    if len(sys.argv) != 2:
        usage()

    mode = sys.argv[1].lower()
    if mode not in ("host", "publisher", "subscriber"):
        usage()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    scripts_by_mode = {
        "host": [
            "CentralController/central_control.py",
        ],
        "publisher": [
            "Publisher/lightning_sensor.py",
            "Publisher/moisture_sensor.py",
            "Publisher/rain_sensor.py",
        ],

        "subscriber" : [
            "Subscriber/alarm_actuator.py", 
            "Subscriber/gui_aplication.py",
            "Subscriber/ventilation_actuator.py",
            "Subscriber/lock_actuator.py"
        ]
    }

    scripts = scripts_by_mode[mode]
    processes = []

    for script in scripts:
        script_path = os.path.join(base_dir, script)

        if not os.path.isfile(script_path):
            print(f"[WARN] {script} not found, skipping")
            continue

        print(f"[START] {script}")
        p = subprocess.Popen(
            [sys.executable, script_path],
            cwd=base_dir
        )
        processes.append(p)

    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\n[INFO] Ctrl+C received, terminating children...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait()

    print("[INFO] Launcher exiting")

if __name__ == "__main__":
    main()
