# main.py
from modules.device_detector import DeviceDetector

def main():
    detector = DeviceDetector()
    devices = detector.detect_devices()
    print(f"Detected devices: {devices}")
if __name__ == "__main__":
    main()
