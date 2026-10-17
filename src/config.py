# -*- coding: utf-8 -*-
"""Allegro 库管理软件 · 全局配置"""
import os

# ===== 库根目录（自动识别项目根，拷贝到新电脑无需改路径）=====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # src 目录
LIB_ROOT = os.path.dirname(BASE_DIR)                    # 项目根目录（src 的上一级）

# ===== 库子目录（与《库管理规范》一致）=====
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

# ===== CIS Access 数据库 =====
DB_PATH = os.path.join(LIB_ROOT, DIRS["database"], "Allegro_CIS_DB.accdb")
ODBC_DRIVER = "Microsoft Access Driver (*.mdb, *.accdb)"

# ===== Allegro env 文件路径（可经环境变量覆盖）=====
ENV_PATH = os.getenv("ALLEGRO_ENV", "")

# ===== Git 远程（可选，模块E）=====
GIT_REMOTE_DEFAULT = ""   # 如 https://github.com/user/allegro-lib.git
