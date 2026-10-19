# -*- coding: utf-8 -*-
"""G6：capture_ini 解析单元测试（用合成示例，不依赖真实 Cadence 安装）。"""
import os
import sys
import tempfile
import unittest

# 让测试能找到 src 下模块
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from db_manage import capture_ini  # noqa: E402

SAMPLE = """[Window Placement]
Max Position=2
[Part Library Directories]
Dir0=C:\\Cadence\\SPB_17.4\\share\\pcb\\pcb_lib\\symbols
Dir1=C:\\Users\\me\\Documents\\OrCAD\\Lib
[Allegro Footprints]
Dir0=C:\\Users\\me\\Documents\\OrCAD\\Footprints
Dir1=D:\\AllegroLib\\symbol\\footprint
[Part Management]
DatasheetDir=D:\\AllegroLib\\doc
"""


class CaptureIniTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.ini_path = os.path.join(self.dir, "Capture.ini")
        with open(self.ini_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE)

    def tearDown(self):
        try:
            os.remove(self.ini_path)
            os.rmdir(self.dir)
        except OSError:
            pass

    def test_parse_footprint_dirs(self):
        r = capture_ini.parse_capture_ini(self.ini_path)
        self.assertEqual(r["footprint_dirs"], [
            "C:\\Users\\me\\Documents\\OrCAD\\Footprints",
            "D:\\AllegroLib\\symbol\\footprint",
        ])

    def test_parse_symbol_dirs(self):
        r = capture_ini.parse_capture_ini(self.ini_path)
        self.assertEqual(r["symbol_dirs"], [
            "C:\\Cadence\\SPB_17.4\\share\\pcb\\pcb_lib\\symbols",
            "C:\\Users\\me\\Documents\\OrCAD\\Lib",
        ])

    def test_parse_datasheet_dir(self):
        r = capture_ini.parse_capture_ini(self.ini_path)
        self.assertEqual(r["datasheet_dir"], "D:\\AllegroLib\\doc")

    def test_parse_missing_section(self):
        # 去掉 datasheet 相关段，仍能解析封装路径
        txt = SAMPLE.split("[Part Management]")[0]
        ini2 = os.path.join(self.dir, "Capture2.ini")
        with open(ini2, "w", encoding="utf-8") as f:
            f.write(txt)
        r = capture_ini.parse_capture_ini(ini2)
        self.assertTrue(r["footprint_dirs"])
        self.assertIsNone(r["datasheet_dir"])
        os.remove(ini2)

    def test_nonexistent_file(self):
        r = capture_ini.parse_capture_ini(os.path.join(self.dir, "nope.ini"))
        self.assertEqual(r["footprint_dirs"], [])
        self.assertEqual(r["raw_sections"], [])

    def test_find_specified_file(self):
        p, hint = capture_ini.find_capture_ini(self.ini_path)
        self.assertEqual(p, os.path.abspath(self.ini_path))

    def test_find_missing_specified(self):
        p, hint = capture_ini.find_capture_ini(os.path.join(self.dir, "missing.ini"))
        self.assertIsNone(p)
        self.assertIn("不存在", hint)

    def test_build_datasheet_url(self):
        url = capture_ini.build_datasheet_url("D:\\AllegroLib\\doc", {"Part_Number": "R-0603-10K"})
        self.assertEqual(url, "D:\\AllegroLib\\doc\\R-0603-10K.pdf")

    def test_build_datasheet_url_empty(self):
        self.assertIsNone(capture_ini.build_datasheet_url("", {"Part_Number": "X"}))
        self.assertIsNone(capture_ini.build_datasheet_url("D:\\doc", {}))


if __name__ == "__main__":
    unittest.main()
