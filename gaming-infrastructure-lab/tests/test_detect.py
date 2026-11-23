import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from detect import detect

def line(minute, ip="192.0.2.42"):
    return f"2026-01-01T12:{minute:02d}:00Z host sshd[1]: Failed password for demo from {ip} port 1234 ssh2"

class DetectTests(unittest.TestCase):
    def test_threshold(self):
        self.assertEqual(len(detect([line(i) for i in range(6)])),1)
    def test_below_threshold(self):
        self.assertEqual(detect([line(i) for i in range(4)]),[])
    def test_outside_window(self):
        self.assertEqual(detect([line(i*6) for i in range(5)]),[])
    def test_separate_ips(self):
        self.assertEqual(detect([line(i,"192.0.2."+str(i+1)) for i in range(6)]),[])
    def test_invalid_input(self):
        self.assertEqual(detect(["garbage",line(0,"not-an-ip")]),[])
    def test_out_of_order(self):
        self.assertEqual(len(detect([line(i) for i in reversed(range(6))])),1)

if __name__=="__main__":
    unittest.main()
