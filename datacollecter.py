import time
import csv
import os
import threading
from pynput.keyboard import Listener, Key

OUTPUT_FILE = "keypresses.csv"
START_KEY = Key.enter  # Key to start logging

# Current time in milliseconds
def now_ms():
    return int(time.time() * 1000)

# Format milliseconds to HH:MM:SS.mmm
def format_elapsed(ms):
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"

# Clear console output
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Global state
logging_started = False
start_time_ms = None
key_counts = {}
lock = threading.Lock()

# Continuously updates
def redraw_screen():
    while logging_started:
        time.sleep(0.1)
        with lock:
            clear_console()
            print("=== Key Logger ===\n")
            for key in sorted(key_counts.keys()):
                print(f"Key: {key}({key_counts[key]})")
            elapsed = now_ms() - start_time_ms
            print("\nElapsed Time:", format_elapsed(elapsed))

# When a key is pressed
def on_press(key):
    global logging_started, start_time_ms

    # Stop
    if key == Key.esc:
        with lock:
            logging_started = False
        clear_console()
        print("[ESC] pressed. Stopping logger...")
        return False  # Stop listener

    # Start
    if not logging_started:
        if key == START_KEY:
            with lock:
                start_time_ms = now_ms()
                logging_started = True
                threading.Thread(target=redraw_screen, daemon=True).start()
        return

    try:
        key_name = key.char.upper() if key.char and len(key.char) == 1 else str(key).replace("'", "").upper()
    except AttributeError:
        key_name = str(key).replace("'", "").upper()

    with lock:
        key_counts[key_name] = key_counts.get(key_name, 0) + 1
        elapsed = now_ms() - start_time_ms
        formatted_time = format_elapsed(elapsed)
        writer.writerow([formatted_time, key_name])

def main():
    global writer

    first_time = not os.path.exists(OUTPUT_FILE)
    csv_file = open(OUTPUT_FILE, "a", newline="", buffering=1)
    writer = csv.writer(csv_file)
    if first_time:
        writer.writerow(["elapsed_time", "key"])

    print("=== Key Logger ===")
    print(f"Press [{START_KEY}] to start logging.")
    print("Press [ESC] to stop.\n")

    # Start listening
    with Listener(on_press=on_press) as listener:
        listener.join()

    # Close CSV file
    csv_file.close()
    print(f"\nSaved log to: {os.path.abspath(OUTPUT_FILE)}")

if __name__ == "__main__":
    main()