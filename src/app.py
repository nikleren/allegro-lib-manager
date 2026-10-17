# -*- coding: utf-8 -*-
"""Allegro 库管理软件 · Flask 入口
启动：在 src 目录下运行  python app.py
访问：http://127.0.0.1:5000
"""
import os
import sys
import time
import subprocess
from flask import Flask, render_template, jsonify, request

from db_manage import db
from config import get_config, set_lib_root, set_db_file

# 页面映射（key 兼容带 / 不带 .html 后缀）
PAGES = {
    "index":  "index.html",
    "db":     "db.html",
    "files":  "files.html",
    "models": "models.html",
    "env":    "env.html",
    "git":    "git.html",
}

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # 中文正常输出
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0  # 静态文件不缓存，避免修改后浏览器仍用旧样式/脚本


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<page>")
def show_page(page):
    page = page.removesuffix(".html")  # 兼容导航链接的 xxx.html 后缀
    f = PAGES.get(page)
    if f:
        return render_template(f)
    return "Not Found", 404


# ===== G4：库根目录配置 API =====
@app.route("/api/config", methods=["GET"])
def api_config_get():
    return jsonify(get_config())


@app.route("/api/config", methods=["POST"])
def api_config_post():
    data = request.get_json(silent=True) or {}
    msgs = []
    ok = True
    if data.get("lib_root") is not None:
        o, m = set_lib_root(data.get("lib_root"))
        ok = ok and o
        msgs.append(m)
    if data.get("db_file") is not None:
        o, m = set_db_file(data.get("db_file"))
        ok = ok and o
        msgs.append(m)
    if ok:
        return jsonify({"ok": True, "message": "；".join(msgs) or "配置已保存", "config": get_config()})
    return jsonify({"ok": False, "message": "；".join(msgs), "config": None})


# ===== 数据库文件"打开选择"对话框（Windows 原生） =====
@app.route("/api/config/browse-db")
def api_config_browse_db():
    path = _browse_access_file()
    if path:
        return jsonify({"ok": True, "path": path})
    return jsonify({"ok": False, "message": "未选择文件"})


def _browse_access_file():
    """在用户交互桌面弹出文件选择对话框，返回路径或 None。

    背景：后端由内置/沙箱 python 启动，其窗口站与用户桌面隔离，
    直接（含子进程）弹 tkinter/WinForms 对话框都不可见。
    解决：动态生成 VBS，经 explorer.exe（用户交互 shell）→ wscript 启动
    系统 PowerShell 弹 WinForms 打开文件框，选中后写入结果文件，本函数轮询读取。
    """
    base = os.path.dirname(os.path.abspath(__file__))
    ps1 = os.path.join(base, "browse_dialog.ps1")
    vbs = os.path.join(base, "browse_launch.vbs")
    out = os.path.join(base, "_browse_result.txt")
    try:
        if os.path.exists(out):
            os.remove(out)
        # 生成纯 ASCII 的 VBS（反斜杠在 VBS 字符串中无需转义，内嵌引号用 "" 转义）
        with open(vbs, "w", encoding="ascii") as f:
            f.write('Set sh = CreateObject("WScript.Shell")\n')
            f.write('sh.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""%s"" -Out ""%s""", 0, False\n' % (ps1, out))
        # 经 explorer 在用户交互桌面启动（不等待）
        subprocess.Popen(["explorer.exe", vbs])
        # 轮询结果文件（最多 10 分钟）
        for _ in range(600):
            if os.path.exists(out):
                with open(out, encoding="utf-8") as f:
                    path = f.read().strip()
                try:
                    os.remove(out)
                except OSError:
                    pass
                return path or None
            time.sleep(1)
    except Exception:
        return None
    return None


# ===== 模块A：数据库 API =====
@app.route("/api/db/info")
def api_db_info():
    return jsonify(db.db_status())


@app.route("/api/parts")
def api_parts():
    """查询器件列表"""
    search = request.args.get("search", "")
    ptype = request.args.get("type", "")
    try:
        rows = db.list_parts(search, ptype)
        return jsonify({"ok": True, "count": len(rows), "rows": rows})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/parts", methods=["POST"])
def api_parts_create():
    """新增器件（A1）"""
    data = request.get_json(silent=True) or {}
    try:
        db.create_part(data)
        return jsonify({"ok": True, "message": "器件已新增"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/parts/<pn>", methods=["PUT"])
def api_parts_update(pn):
    """更新器件（A1）"""
    data = request.get_json(silent=True) or {}
    try:
        n = db.update_part(pn, data)
        if n == 0:
            return jsonify({"ok": False, "error": f"未找到器件：{pn}"})
        return jsonify({"ok": True, "message": "器件已更新"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/parts/<pn>", methods=["DELETE"])
def api_parts_delete(pn):
    """删除器件（A1，前端二次确认后调用）"""
    try:
        n = db.delete_part(pn)
        if n == 0:
            return jsonify({"ok": False, "error": f"未找到器件：{pn}"})
        return jsonify({"ok": True, "message": "器件已删除"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/db/init-sql")
def api_db_init_sql():
    """返回建表 SQL 指引（库/表缺失时供用户创建）"""
    return jsonify({"ok": True, "table": db.PART_TABLE, "sql": db.CREATE_PART_TABLE_SQL})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
