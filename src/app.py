# -*- coding: utf-8 -*-
"""Allegro 库管理软件 · Flask 入口
启动：在 src 目录下运行  python app.py
访问：http://127.0.0.1:5000
"""
import os
from flask import Flask, render_template, jsonify, request

from db_manage import db
from config import get_config, set_lib_root

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
    lib_root = (data.get("lib_root") or "").strip()
    ok, msg = set_lib_root(lib_root)
    if ok:
        return jsonify({"ok": True, "message": msg, "config": get_config()})
    return jsonify({"ok": False, "message": msg, "config": None})


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
