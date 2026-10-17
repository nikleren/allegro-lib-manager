# -*- coding: utf-8 -*-
"""模块 A（CIS 数据库）单元测试

运行方式（在项目根或 tests 目录）：
    python -m unittest discover -s tests -v
或：
    cd tests && python -m unittest test_db -v

前提：已初始化数据库（database/Allegro_CIS_DB.accdb 且含 PART_TABLE 表），
否则相关用例自动跳过（skip），并提示先初始化。
CRUD 用例插入临时器件编号（T-UT-*），测试后清理，不残留真实数据。
"""
import os
import sys
import unittest

# 使测试可导入 src 下的 db_manage
_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import pyodbc
from db_manage import db


class TestDbCRUD(unittest.TestCase):
    """对真实 Access 库做增删改查联调（插入临时记录，测后清理，不残留）"""

    @classmethod
    def setUpClass(cls):
        if not db.db_exists():
            raise unittest.SkipTest("数据库文件不存在，请先初始化数据库（database/Allegro_CIS_DB.accdb）")
        conn = pyodbc.connect("DRIVER={%s};DBQ=%s;" % (db.ODBC_DRIVER, db.db_path()))
        cur = conn.cursor()
        tables = [r.table_name for r in cur.tables(tableType="TABLE")]
        cur.close()
        conn.close()
        if db.PART_TABLE not in tables:
            raise unittest.SkipTest("PART_TABLE 表不存在，请先建表")

    def setUp(self):
        # 每条测试用唯一器件编号，避免相互冲突
        self.pn = "T-UT-" + os.urandom(4).hex().upper()
        self.part = {
            "Part_Number": self.pn,
            "Value": "10K",
            "Tolerance": "±1%",
            "Part_Type": "电阻",
            "Manufacturer": "UnitTest",
            "MPN": "UT-001",
            "Description": "单元测试器件",
            "Symbol_Name": "RES0603",
            "PCB_Footprint": "R0603",
            "Step_Model": "",
            "Datasheet": "",
            "RoHS": "ROHS",
            "Temp_Range": "-55~155℃",
            "Supplier": "test",
            "Cost": 0.01,
            "Lifecycle": "Active",
            "Remark": "单元测试",
        }

    def tearDown(self):
        # 清理临时记录，避免残留
        try:
            db.delete_part(self.pn)
        except Exception:
            pass

    def test_create_and_get(self):
        db.create_part(self.part)
        got = db.get_part(self.pn)
        self.assertIsNotNone(got)
        self.assertEqual(got["Value"], "10K")
        self.assertEqual(got["PCB_Footprint"], "R0603")

    def test_create_duplicate_raises(self):
        db.create_part(self.part)
        with self.assertRaises(Exception):
            db.create_part(self.part)  # 主键重复应报错

    def test_update(self):
        db.create_part(self.part)
        db.update_part(self.pn, dict(self.part, Value="11K", Remark="已更新"))
        got = db.get_part(self.pn)
        self.assertEqual(got["Value"], "11K")
        self.assertEqual(got["Remark"], "已更新")

    def test_update_missing(self):
        n = db.update_part(self.pn, dict(self.part))
        self.assertEqual(n, 0)  # 不存在的编号，受影响 0 行

    def test_delete(self):
        db.create_part(self.part)
        n = db.delete_part(self.pn)
        self.assertEqual(n, 1)
        self.assertIsNone(db.get_part(self.pn))

    def test_list_and_filter(self):
        db.create_part(self.part)
        rows = db.list_parts(search=self.pn)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Part_Number"], self.pn)
        rows_type = db.list_parts(part_type="电阻")
        self.assertTrue(any(r["Part_Number"] == self.pn for r in rows_type))

    def test_create_requires_pn(self):
        bad = dict(self.part, Part_Number="  ")
        with self.assertRaises(ValueError):
            db.create_part(bad)


class TestDbSchema(unittest.TestCase):
    """表结构 / 字段规范校验"""

    def test_db_exists(self):
        self.assertIsInstance(db.db_exists(), bool)

    def test_part_fields_complete(self):
        # 与《库管理规范》一致的 17 字段
        self.assertEqual(len(db.PART_FIELDS), 17)
        self.assertEqual(db.PART_FIELDS[0], "Part_Number")
        for req in ("Symbol_Name", "PCB_Footprint"):
            self.assertIn(req, db.PART_FIELDS)

    def test_sql_fields_escaped(self):
        # Access 保留字（Value 等）已用方括号转义
        value_idx = db.PART_FIELDS.index("Value")
        self.assertTrue(db.SQL_FIELDS[value_idx].startswith("["))
        self.assertTrue(db.SQL_FIELDS[value_idx].endswith("]"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
