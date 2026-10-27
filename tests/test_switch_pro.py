import sys
import threading
from types import ModuleType
import unittest
from unittest.mock import Mock, patch

for name in ("fcntl", "termios"):
    try:
        __import__(name)
    except ModuleNotFoundError:
        sys.modules[name] = ModuleType(name)

from sdcd.hid import Link
from sdcd.profiles.switch_pro import Battery, SwitchPro, SwitchProEncoder


class SwitchProEncoderTests(unittest.TestCase):
    def test_silent_until_simple_input_changes(self):
        encoder = SwitchProEncoder()
        battery = Battery()

        self.assertEqual(encoder.encode(None, battery), b"")
        self.assertEqual(encoder.encode(None, battery), b"")

    def test_answers_mcu_configuration_request(self):
        encoder = SwitchProEncoder()
        request = b"\xA2\x01" + bytes(9) + b"\x21"
        encoder.handle_output(request, b"\x00" * 6)

        reply = encoder.encode(None, Battery())

        self.assertEqual(len(reply), 49)
        self.assertEqual(reply[0], 0x21)
        self.assertEqual(reply[13:15], b"\xA0\x21")
        self.assertEqual(reply[15:], bytes([0x01, 0x00, 0xFF, 0x00, 0x08, 0x00, 0x1B, 0x01])
                         + bytes(25) + b"\xC8")

    def test_bluetooth_link_does_not_send_empty_reports(self):
        intr = Mock()
        intr.getsockopt.return_value = 1024
        link = None

        def get_empty_report():
            link.alive.clear()
            return b""

        link = Link.__new__(Link)
        link.intr = intr
        link.profile = SwitchPro()
        link.get_report = get_empty_report
        link.has_urgent = lambda: False
        link.alive = threading.Event()
        link.alive.set()
        link.new_input = threading.Condition()
        link.sent = link.skipped = 0

        with patch("sdcd.hid._queued_bytes", return_value=0):
            link._send_loop()

        intr.send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
