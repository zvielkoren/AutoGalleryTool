# main.py
import time

from modules.device_detector import DeviceDetector

def main():

    detector = DeviceDetector()
    while True:
        devices = detector.detect_devices()
        print(f"Detected devices: {devices}")
        time.sleep(5)  # Check every 5 seconds
if __name__ == "__main__":
    main()
