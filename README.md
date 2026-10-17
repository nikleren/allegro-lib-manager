# Allegro 库管理软件（Allegro Library Manager）

面向 **Cadence Allegro 17.4 / Capture CIS** 的单机版元件库管理工具。通过本地网页界面统一管理 **Access（.accdb）CIS 元件数据库**、封装/焊盘/符号文件、3D 模型以及 Allegro env 库路径配置，替代手工维护，提升库的一致性与可追溯性。

- 后端：Python + Flask，通过 ODBC（pyodbc）直接读写 Access `.accdb`
- 前端：原生 HTML / CSS / JavaScript（无需打包）
- 形态：本地运行，浏览器访问 `http://127.0.0.1:5000`
- 版本：本地 git 管理，支持推送 / 拉取 GitHub 或私有 GitLab

## 功能模块

| 模块 | 说明 |
|---|---|
| A · CIS 数据库管理 | 器件增删改查（真实读写 Access）、CSV 导入、导出 CSV 模板、生成 DBC、导出元件清单；页面顶部显示当前数据库路径 |
| B · 封装 / 符号文件管理 | 浏览、文件级校验（存在性、命名规范、数量/大小）、查重、生成报表 |
| C · 3D 模型管理 | 封装与 `.stp/.step` 模型对应关系检查、缺失提示 |
| D · env 配置 | 读取 Allegro env 初始化文件，输出可关联库目录的配置脚本 |
| E · Git 同步 | 打包上传 / 拉取，支持 GitHub 与私有 GitLab |
| 通用 G1~G5 | 删除二次确认、首页显示库目录、库版本与更新提示、可配置库根目录、可配置数据库路径（支持"打开选择文件"对话框） |

## 目录结构

```
allegroLibmm/
├── src/
│   ├── app.py              # Flask 入口与 API
│   ├── config.py           # 库根 / 数据库路径配置（config.ini）
│   ├── browse_dialog.ps1   # Windows 文件选择对话框
│   ├── db_manage/
│   │   └── db.py           # Access 建表与增删改查
│   ├── templates/          # 页面（index/db/files/models/env/git）
│   └── static/             # css / js
├── tests/
│   └── test_db.py          # 数据库单元测试
├── install.bat             # 一键安装依赖 + 初始化库目录
├── run.bat                 # 一键启动
├── requirements.txt
├── 库管理规范.md            # 库表结构、目录结构、命名规范（权威规范）
├── 需求规格说明.md          # 软件需求规格
└── 部署说明.md              # 新电脑部署说明
```

部署时由 `install.bat` 在库根（默认程序目录）下自动创建以下库目录（**不随本仓库分发**）：

```
database/            # Access 数据库（.accdb）
schematic/           # 原理图符号库（.olb）
symbol/footprint/    # 封装（.dra/.psm）
symbol/pad/          # 焊盘（.pad）
symbol/flash/        # 花焊盘（flash）
symbol/mech/         # 机械符号
3d/                  # 3D 模型（.stp/.step）
doc/                 # 数据手册
```

## 安装与运行

1. 安装 **Python 3**（勾选 Add Python to PATH）。
2. 安装 **Microsoft Access Database Engine x64**（提供 64 位 Access ODBC 驱动，用于读写 `.accdb`）。
3. 双击 `install.bat`：自动安装 Python 依赖并创建库目录结构。
4. 双击 `run.bat` 启动，浏览器打开 `http://127.0.0.1:5000`。

详见《部署说明.md》。

## 数据库

- 按《库管理规范.md》建立单表 `PART_TABLE`（17 个字段），`Part_Number` 为主键。
- 数据库文件默认位于 `<库根>\database\Allegro_CIS_DB.accdb`，可在首页配置（G5），程序部署目录与元件库目录可分离（G4）。
- 运行单元测试：`python -m unittest discover -s tests`

## 关于元件库文件

封装、焊盘、符号、3D 模型等**元件库文件不包含在本仓库中**，它们通常来自器件厂商或第三方库且有各自的版权 / 许可。请自行合法获取并放入上述库目录，再在 Access 数据库中登记。

## 许可证

[MIT License](LICENSE)
