import os
import time
import subprocess
import platform
import logging

# Set up logging
logging.basicConfig(
    filename='devices.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Device:
    def __init__(self, name, size, type):
        self.name = name
        self.size = size
        self.type = type
        self.last_accessed = time.time()
        self.last_modified = time.time()

    @staticmethod
    def format_size(size_str):
        """Convert size from string to a more readable format (e.g., GB)."""
        try:
            size = int(size_str)
            if size >= 1 << 30:  # 1 GB
                return f"{size / (1 << 30):.2f} GB"
            elif size >= 1 << 20:  # 1 MB
                return f"{size / (1 << 20):.2f} MB"
            else:
                return f"{size} bytes"
        except ValueError:
            return size_str  # Return original if conversion fails

    def list_removable_devices(self):
        """
        Lists all connected removable devices based on the OS platform.
        """
        removable_devices = []

        if platform.system() == "Windows":
            # Windows: Use PowerShell command to get removable devices
            try:
                output = subprocess.check_output(
                    ['powershell', '-Command',
                     'Get-WmiObject Win32_LogicalDisk | Where-Object { $_.DriveType -eq 2 } | Select-Object DeviceID, VolumeName, Size, DriveType'],
                    text=True
                )
                for line in output.splitlines():
                    if line.strip():  # Ignore empty lines
                        parts = line.split()
                        if len(parts) >= 4:
                            name = parts[1]
                            size = self.format_size(parts[2])  # Format size
                            type = parts[3]
                            removable_devices.append(Device(name, size, type))
            except subprocess.CalledProcessError as e:
                logging.error(f"Error while listing devices: {e}")

        elif platform.system() == "Linux":
            # Linux: Use 'lsblk' command
            try:
                output = subprocess.check_output(['lsblk', '-o', 'NAME,SIZE,TYPE,RM'], text=True)
                for line in output.splitlines()[1:]:  # Skip the header line
                    parts = line.split()
                    if len(parts) >= 4 and parts[3] == '1':  # Check if the device is removable
                        name = parts[0]
                        size = self.format_size(parts[1])  # Format size
                        type = parts[2]
                        removable_devices.append(Device(name, size, type))
            except subprocess.CalledProcessError as e:
                logging.error(f"Error while listing devices: {e}")

        else:
            logging.warning("Unsupported platform.")

        return removable_devices

    def monitor_removable_devices(self, interval=5):
        """
        Monitors connected removable devices at a specified interval.
        """
        known_devices = set()  # Set to keep track of known devices
        print("Monitoring removable devices... Press Ctrl+C to stop.")

        try:
            while True:
                current_devices = set(self.list_removable_devices())
                # Check for new devices
                new_devices = current_devices - known_devices
                # Check for removed devices
                removed_devices = known_devices - current_devices

                if new_devices:
                    for device in new_devices:
                        logging.info(f"New device connected: {device.name} (Size: {device.size}, Type: {device.type})")
                        self.save_device_data(device)

                if removed_devices:
                    for device in removed_devices:
                        logging.info(f"Device removed: {device.name} (Size: {device.size}, Type: {device.type})")
                        self.save_device_data(device)

                known_devices = current_devices  # Update known devices
                time.sleep(interval)  # Wait for the specified interval

        except KeyboardInterrupt:
            print("\nMonitoring stopped.")

    def save_device_data(self, device):
        """
        Saves device data to a file in real-time.
        """
        logging.info(f"Saving device data: {device.name} (Size: {device.size}, Type: {device.type})")

if __name__ == "__main__":
    device_monitor = Device("", "", "")
    device_monitor.monitor_removable_devices(interval=5)  # Check every 5 seconds
