# -*- coding: utf-8 -*-
"""Access 数据库连接与基础操作（pyodbc）"""
import os
import pyodbc
from config import db_path, ODBC_DRIVER

PART_TABLE = "PART_TABLE"

# PART_TABLE 字段清单（与《库管理规范》一致，顺序为展示顺序）
PART_FIELDS = [
    "Part_Number", "Value", "Tolerance", "Part_Type", "Manufacturer", "MPN",
    "Description", "Symbol_Name", "PCB_Footprint", "Step_Model", "Datasheet",
    "RoHS", "Temp_Range", "Supplier", "Cost", "Lifecycle", "Remark",
]

# 带方括号的 SQL 字段名（Value 等为 Access 保留字，SQL 中须用 [ ] 转义）
SQL_FIELDS = [f"[{c}]" for c in PART_FIELDS]


def db_exists():
    """数据库文件是否存在"""
    return os.path.isfile(db_path())


def check_driver():
    """检测系统中可用的 Access ODBC 驱动"""
    try:
        return [d for d in pyodbc.drivers() if "Access" in d]
    except Exception:
        return []


def get_connection():
    """建立 Access 连接（若文件不存在则抛错）"""
    if not db_exists():
        raise FileNotFoundError(f"数据库文件不存在：{db_path()}")
    conn_str = f"DRIVER={{{ODBC_DRIVER}}};DBQ={db_path()};"
    return pyodbc.connect(conn_str)


def db_status():
    """数据库连接状态检查（供 /api/db/info）"""
    status = {
        "db_exists": db_exists(),
        "db_path": db_path(),
        "drivers": check_driver(),
        "connected": False,
    }
    if not db_exists():
        status["error"] = f"数据库文件不存在：{db_path()}，请先在 Access 中创建并建表"
        return status
    try:
        conn = get_connection()
        cur = conn.cursor()
        tables = [r.table_name for r in cur.tables(tableType="TABLE")]
        status["connected"] = True
        status["tables"] = tables
        status["has_part_table"] = PART_TABLE in tables
        cur.close()
        conn.close()
    except Exception as e:
        status["connected"] = False
        status["error"] = str(e)
    return status


def list_parts(search="", part_type=""):
    """查询器件列表，返回 dict 列表"""
    sql = "SELECT * FROM " + PART_TABLE
    cond, params = [], []
    if search:
        cond.append("Part_Number LIKE ?")
        params.append(f"%{search}%")
    if part_type:
        cond.append("Part_Type = ?")
        params.append(part_type)
    if cond:
        sql += " WHERE " + " AND ".join(cond)
    sql += " ORDER BY Part_Number"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    cols = [c[0] for c in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def get_part(pn):
    """按器件编号查询单条"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {PART_TABLE} WHERE Part_Number=?", (pn,))
    cols = [c[0] for c in cur.description]
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(zip(cols, row)) if row else None


# ===== 建表 SQL（供用户在有库后执行建表，或软件校验）=====
CREATE_PART_TABLE_SQL = f"""CREATE TABLE {PART_TABLE} (
    [Part_Number]   TEXT(50)   NOT NULL PRIMARY KEY,
    [Value]         TEXT(50),
    [Tolerance]     TEXT(20),
    [Part_Type]     TEXT(50),
    [Manufacturer]  TEXT(100),
    [MPN]           TEXT(100),
    [Description]   TEXT(200),
    [Symbol_Name]   TEXT(50),
    [PCB_Footprint] TEXT(50),
    [Step_Model]    TEXT(50),
    [Datasheet]     TEXT(255),
    [RoHS]          TEXT(10),
    [Temp_Range]    TEXT(50),
    [Supplier]      TEXT(100),
    [Cost]          CURRENCY,
    [Lifecycle]     TEXT(20),
    [Remark]        TEXT(200)
)"""


# ===== A1 增删改查 =====
def _row_values(part, fields):
    """从 part 取值；Cost 为货币列，空串/空白转 None（NULL），避免类型写入错误。"""
    vals = []
    for c in fields:
        v = part.get(c)
        if c == "Cost" and (v is None or str(v).strip() == ""):
            v = None
        vals.append(v)
    return vals


def create_part(part):
    """新增器件；Part_Number 必填，返回 True"""
    pn = (part.get("Part_Number") or "").strip()
    if not pn:
        raise ValueError("器件编号（Part_Number）不能为空")
    cols = SQL_FIELDS
    vals = _row_values(part, PART_FIELDS)
    qs = ",".join("?" * len(cols))
    sql = f"INSERT INTO {PART_TABLE} ({','.join(cols)}) VALUES ({qs})"
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, vals)
        conn.commit()
    finally:
        cur.close()
        conn.close()
    return True


def update_part(pn, part):
    """按器件编号更新（主键 Part_Number 不可改）；返回受影响行数"""
    col_idx = [i for i, c in enumerate(PART_FIELDS) if c != "Part_Number"]
    sets = ",".join(f"{SQL_FIELDS[i]}=?" for i in col_idx)
    vals = _row_values(part, [PART_FIELDS[i] for i in col_idx]) + [pn]
    sql = f"UPDATE {PART_TABLE} SET {sets} WHERE [Part_Number]=?"
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, vals)
        conn.commit()
        return cur.rowcount
    finally:
        cur.close()
        conn.close()


def delete_part(pn):
    """按器件编号删除；返回受影响行数"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"DELETE FROM {PART_TABLE} WHERE Part_Number=?", (pn,))
        conn.commit()
        return cur.rowcount
    finally:
        cur.close()
        conn.close()
