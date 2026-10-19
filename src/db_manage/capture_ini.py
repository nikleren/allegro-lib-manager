# -*- coding: utf-8 -*-
"""G6：读取 Cadence Capture.ini，提取封装路径与 datasheet 路径。

Capture.ini 位于 <SPB_Data>\\cdssetup\\OrCAD_Capture\\<版本>\\Capture.ini。
关键段（Cadence Capture 17.x）：
  [Allegro Footprints]   Dir0=... / Dir1=...   -> 封装（footprint）路径
  [Part Library Directories] Dir0=...         -> 原理图符号库路径
  datasheet 相关路径可能位于 [Part Management] / [Component Datasheet] 等段。
本模块对段/键做容错：缺失或格式异常仅跳过该项，不抛错。
"""
import os
import glob
import configparser


def _latest_version_dir(capture_root):
    """在 OrCAD_Capture 根下返回版本号最大的子目录（如 17.4.0），无则返回 None。"""
    try:
        entries = [p for p in glob.glob(os.path.join(capture_root, "*")) if os.path.isdir(p)]
    except Exception:
        return None
    if not entries:
        return None
    # 版本号按数值段比较（17.4.0 > 17.2.0）
    def ver_key(p):
        name = os.path.basename(p)
        parts = []
        for s in name.replace("-", ".").split("."):
            try:
                parts.append(int(s))
            except ValueError:
                parts.append(-1)
        return tuple(parts) + (name,)
    return sorted(entries, key=ver_key)[-1]


def find_capture_ini(specified=""):
    """定位 Capture.ini。

    - specified 非空且为文件：直接使用。
    - 否则探测常见安装根下的 SPB_Data\\cdssetup\\OrCAD_Capture。
    返回 (path, hint)；找不到返回 (None, hint)。
    """
    hint = ""
    if specified and os.path.isfile(specified):
        return os.path.abspath(specified), "已使用指定路径"
    # 常见 Cadence 安装根
    candidates_roots = []
    for root in ("C:/Cadence", "D:/Cadence", "C:/SPB_Data", "D:/SPB_Data", "C:/Cadence/SPB_Data", "D:/Cadence/SPB_Data"):
        if os.path.isdir(root):
            candidates_roots.append(root)
    for base in candidates_roots:
        capture_root = os.path.join(base, "cdssetup", "OrCAD_Capture")
        if not os.path.isdir(capture_root):
            continue
        vdir = _latest_version_dir(capture_root)
        if vdir:
            ini = os.path.join(vdir, "Capture.ini")
            if os.path.isfile(ini):
                return os.path.abspath(ini), "自动探测：" + os.path.abspath(ini)
    if specified:
        return None, f"指定的 Capture.ini 不存在：{specified}"
    return None, "未找到 Capture.ini（可在配置页手动指定路径）"


def _section(parser, name):
    """取段为 dict，容忍大小写差异；无段返回 {}。"""
    if parser.has_section(name):
        return dict(parser.items(name))
    for sec in parser.sections():
        if sec.strip().lower() == name.lower():
            return dict(parser.items(sec))
    return {}


def _dir_values(sec):
    """提取段内 Dir0/Dir1/...（也兼容 dir0）非空路径列表。"""
    out = []
    for k, v in sec.items():
        key = k.strip()
        if key.lower().startswith("dir") and v and v.strip():
            path = v.strip().strip('"')
            if path:
                out.append(path)
    return out


def parse_capture_ini(path):
    """解析 Capture.ini，返回结构化结果。

    返回 dict：
      path          : 文件路径
      footprint_dirs: [封装路径...]（来自 [Allegro Footprints]）
      symbol_dirs   : [符号库路径...]（来自 [Part Library Directories]）
      datasheet_dir : datasheet 目录（尽力从相关段提取，找不到为 None）
      raw_sections  : 解析出的段名列表
    """
    result = {
        "path": os.path.abspath(path),
        "footprint_dirs": [],
        "symbol_dirs": [],
        "datasheet_dir": None,
        "raw_sections": [],
    }
    if not os.path.isfile(path):
        return result
    parser = configparser.ConfigParser()
    try:
        parser.read(path, encoding="utf-8")
    except Exception:
        try:
            parser.read(path, encoding="gbk")
        except Exception:
            return result
    result["raw_sections"] = parser.sections()

    fp = _section(parser, "Allegro Footprints")
    result["footprint_dirs"] = _dir_values(fp)

    lib = _section(parser, "Part Library Directories")
    result["symbol_dirs"] = _dir_values(lib)

    # datasheet 路径：优先 [Part Management]/[Component Datasheet]，否则扫描所有段里含 "datasheet" 或 "pdf" 的键
    for sec_name in ("Part Management", "Component Datasheet", "Datasheet Paths", "Datasheet"):
        sec = _section(parser, sec_name)
        for k, v in sec.items():
            if v and v.strip() and (k.lower() in ("dir0", "path", "datasheet", "datasheetpath", "pdfpath") or "datasheet" in k.lower()):
                p = v.strip().strip('"')
                if p:
                    result["datasheet_dir"] = p
                    break
        if result["datasheet_dir"]:
            break
    return result


def build_datasheet_url(datasheet_dir, part):
    """按 datasheet 目录为器件构造数据手册路径（回填用）。

    规则：<dir>\\<Part_Number>.pdf；找不到文件名规则时用目录本身。失败返回 None。
    """
    if not datasheet_dir:
        return None
    d = datasheet_dir.strip().strip('"')
    if not d:
        return None
    pn = (part.get("Part_Number") or "").strip()
    if pn:
        return os.path.join(d, pn + ".pdf")
    return None
