"""
Unit Tests for Assignment 2 — Port Scanner
"""

import unittest

# TODO: Import your classes and common_ports from assignment2_studentID
from assignment2_101402390 import PortScanner, common_ports


class TestPortScanner(unittest.TestCase):

    def test_scanner_initialization(self):
        """Test that PortScanner initializes with correct target and empty results list."""
        scanner = PortScanner("127.0.0.1")
        self.assertEqual(scanner.target, "127.0.0.1")
        self.assertEqual(scanner.scan_results, [])
       

    def test_get_open_ports_filters_correctly(self):
        """Test that get_open_ports returns only Open ports."""
        scanner = PortScanner("127.0.0.1")
        scanner.scan_results = [
            (22, "Open", "SSH"),
            (23, "Closed", "Telnet"),
            (80, "Open", "HTTP")
        ]
        result = scanner.get_open_ports()
        self.assertListEqual([p[0] for p in result], [22, 80])

    def test_common_ports_dict(self):
        """Test that common_ports dictionary has correct entries."""
        self.assertEqual(common_ports[80], "HTTP")
        self.assertEqual(common_ports[22], "SSH")

    def test_invalid_target(self):
        """Test that setter rejects empty string target."""
        scanner = PortScanner("127.0.0.1")
        scanner.target = ""   
        self.assertEqual(scanner.target, "127.0.0.1")


if __name__ == "__main__":
    unittest.main()
