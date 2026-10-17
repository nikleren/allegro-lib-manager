# -*- coding: utf-8 -*-
"""Allegro 库管理软件 · 全局配置
G4：元件库根目录可配置，与程序部署目录分离。
配置文件 config.ini（程序部署目录下）：[paths] lib_root = <库根路径>
"""
import os
import configparser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # src 目录
PROJECT_ROOT = os.path.dirname(BASE_DIR)                # 程序部署目录（项目根）
CONFIG_INI = os.path.join(PROJECT_ROOT, "config.ini")   # 配置文件

# ===== 库子目录（与《库管理规范》一致，一律相对库根解析）=====
DIRS = {
    "database":  "database",               # CIS 元件数据库
    "schematic": "schematic",              # 原理图符号
    "footprint": "symbol/footprint",       # PCB 封装
    "pad":       "symbol/pad",             # 焊盘
    "flash":     "symbol/flash",           # 花焊盘
    "mech":      "symbol/mech",            # 机械符号
    "model3d":   "3d",                     # 3D 模型
    "doc":       "doc",                    # 数据手册
}

# 默认库根：未配置时指向程序部署目录（项目根），保证现有库立即可用；
# 用户可在首页配置为任意独立目录（如 D:\AllegroLib），实现与程序目录分离。
DEFAULT_LIB_ROOT = PROJECT_ROOT


def _read_lib_root():
    """读取配置文件中配置的库根；无配置或路径无效时返回默认值"""
    try:
        cp = configparser.ConfigParser()
        cp.read(CONFIG_INI, encoding="utf-8")
        p = cp.get("paths", "lib_root", fallback="").strip()
        if p and os.path.isdir(p):
            return os.path.abspath(os.path.expandvars(p))
    except Exception:
        pass
    return DEFAULT_LIB_ROOT


# 当前生效的库根（import 时按配置初始化）
LIB_ROOT = _read_lib_root()


def _read_db_file():
    """读取配置文件中配置的数据库文件路径；未配置返回空串"""
    try:
        cp = configparser.ConfigParser()
        cp.read(CONFIG_INI, encoding="utf-8")
        p = cp.get("paths", "db_file", fallback="").strip()
        if p:
            return os.path.abspath(os.path.expandvars(p))
    except Exception:
        pass
    return ""


# 可配置的数据库文件路径（G5）；空串表示未配置，db_path() 按库根推导
DB_FILE = _read_db_file()


def db_path():
    """CIS Access 数据库路径：优先用配置的 db_file（G5），未配置则按库根推导"""
    if DB_FILE:
        return DB_FILE
    return os.path.join(LIB_ROOT, DIRS["database"], "Allegro_CIS_DB.accdb")


ODBC_DRIVER = "Microsoft Access Driver (*.mdb, *.accdb)"

# ===== Allegro env 文件路径（可经环境变量覆盖）=====
ENV_PATH = os.getenv("ALLEGRO_ENV", "")

# ===== Git 远程（可选，模块E）=====
GIT_REMOTE_DEFAULT = ""   # 如 https://github.com/user/allegro-lib.git


def get_config():
    """返回当前配置快照（供 /api/config GET）"""
    return {
        "lib_root": LIB_ROOT,
        "config_ini": CONFIG_INI,
        "db_file": DB_FILE,
        "db_path": db_path(),
        "subdirs": {
            k: {
                "path": os.path.join(LIB_ROOT, v),
                "exists": os.path.isdir(os.path.join(LIB_ROOT, v)),
            }
            for k, v in DIRS.items()
        },
    }


def set_lib_root(path):
    """校验并保存新的库根；成功返回 (True, 消息)，失败返回 (False, 错误)。"""
    global LIB_ROOT
    if not path or not path.strip():
        return False, "库根路径不能为空"
    p = os.path.abspath(os.path.expandvars(path.strip()))
    if not os.path.isdir(p):
        return False, f"目录不存在：{p}"
    if not os.access(p, os.W_OK):
        return False, f"目录不可写：{p}"
    # 写回 config.ini
    cp = configparser.ConfigParser()
    if os.path.isfile(CONFIG_INI):
        cp.read(CONFIG_INI, encoding="utf-8")
    if not cp.has_section("paths"):
        cp.add_section("paths")
    cp.set("paths", "lib_root", p)
    os.makedirs(os.path.dirname(CONFIG_INI), exist_ok=True)
    with open(CONFIG_INI, "w", encoding="utf-8") as f:
        cp.write(f)
    LIB_ROOT = p
    return True, f"库根已更新：{p}"


def set_db_file(path):
    """校验并保存新的数据库文件路径；传空串表示恢复为按库根推导。"""
    global DB_FILE
    p = (path or "").strip()
    p = os.path.abspath(os.path.expandvars(p)) if p else ""
    if p:
        parent = os.path.dirname(p)
        if not os.path.isdir(parent):
            return False, f"数据库所在目录不存在：{parent}"
        if not p.lower().endswith((".accdb", ".mdb")):
            return False, "数据库文件需为 .accdb 或 .mdb 格式"
    # 写回 config.ini
    cp = configparser.ConfigParser()
    if os.path.isfile(CONFIG_INI):
        cp.read(CONFIG_INI, encoding="utf-8")
    if not cp.has_section("paths"):
        cp.add_section("paths")
    cp.set("paths", "db_file", p)  # 空串 = 未配置，按库根推导
    os.makedirs(os.path.dirname(CONFIG_INI), exist_ok=True)
    with open(CONFIG_INI, "w", encoding="utf-8") as f:
        cp.write(f)
    DB_FILE = p
    return True, ("数据库路径已更新：" + p) if p else "数据库路径已恢复为按库根推导"
