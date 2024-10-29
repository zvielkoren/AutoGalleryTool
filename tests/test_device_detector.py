import subprocess
import unittest
from unittest.mock import patch
from src.modules.device_detector import DeviceDetector


class TestDeviceDetectorOperations(unittest.TestCase):
    def setUp(self):
        self.device_detector = DeviceDetector()

    @patch('src.modules.device_detector.os.path.exists')
    @patch('src.modules.device_detector.subprocess.run')
    def test_detect_devices_with_multiple_removable_drives(self, mock_run, mock_exists):
        mock_exists.side_effect = lambda x: x in ['A:\\', 'B:\\', 'C:\\']
        mock_process = unittest.mock.Mock()
        mock_process.returncode = 0
        mock_process.stdout = "DriveType=2"
        mock_run.return_value = mock_process

        result = self.device_detector.detect_devices()
        self.assertEqual(result, ['A:\\', 'B:\\', 'C:\\'])

    @patch('src.modules.device_detector.os.path.exists')
    @patch('src.modules.device_detector.subprocess.run')
    def test_detect_devices_with_no_drives(self, mock_run, mock_exists):
        mock_exists.return_value = False
        result = self.device_detector.detect_devices()
        self.assertEqual(result, [])

    @patch('src.modules.device_detector.os.path.exists')
    @patch('src.modules.device_detector.subprocess.run')
    def test_is_removable_with_non_removable_drive(self, mock_run, mock_exists):
        mock_exists.return_value = True
        mock_process = unittest.mock.Mock()
        mock_process.returncode = 0
        mock_process.stdout = "DriveType=3"
        mock_run.return_value = mock_process

        result = self.device_detector.is_removable("D:\\")
        self.assertFalse(result)

    @patch('src.modules.device_detector.os.path.exists')
    @patch('src.modules.device_detector.subprocess.run')
    def test_is_removable_with_command_failure(self, mock_run, mock_exists):
        mock_exists.return_value = True
        mock_process = unittest.mock.Mock()
        mock_process.returncode = 1
        mock_run.return_value = mock_process

        result = self.device_detector.is_removable("E:\\")
        self.assertFalse(result)

    @patch('src.modules.device_detector.os.path.exists')
    @patch('src.modules.device_detector.subprocess.run')
    def test_is_removable_with_invalid_output(self, mock_run, mock_exists):
        mock_exists.return_value = True
        mock_process = unittest.mock.Mock()
        mock_process.returncode = 0
        mock_process.stdout = "InvalidOutput"
        mock_run.return_value = mock_process

        result = self.device_detector.is_removable("F:\\")
        self.assertFalse(result)

    @patch('src.modules.device_detector.os.path.exists')
    def test_get_available_drives_with_exception(self, mock_exists):
        mock_exists.side_effect = Exception("Test exception")
        result = self.device_detector.get_available_drives()
        self.assertEqual(result, [])

    @patch('src.modules.device_detector.subprocess.run')
    def test_is_removable_with_subprocess_exception(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
        result = self.device_detector.is_removable("G:\\")
        self.assertFalse(result)

    @patch('src.modules.device_detector.logger')
    def test_detect_devices_logs_results(self, mock_logger):
        with patch('src.modules.device_detector.os.path.exists') as mock_exists:
            with patch('src.modules.device_detector.subprocess.run') as mock_run:
                mock_exists.return_value = True
                mock_process = unittest.mock.Mock()
                mock_process.returncode = 0
                mock_process.stdout = "DriveType=2"
                mock_run.return_value = mock_process

                self.device_detector.detect_devices()
                mock_logger.info.assert_any_call("Starting device detection")
                self.assertTrue(any("Detected" in str(call) for call in mock_logger.info.call_args_list))
unittest.main()
