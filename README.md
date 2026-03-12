# Excel数据脱敏工具

对Excel文件中的敏感数据进行脱敏处理，支持脱敏后还原。

## 功能特性

- ✅ **数据脱敏**: 将指定列的敏感数据替换为随机值
- ✅ **保留首尾**: 可选保留首尾字符（如：张**三）
- ✅ **完全随机**: 支持完全随机替换（如：MASK_A3F7B2D1）
- ✅ **对照表生成**: 自动生成原始值与脱敏值的对照表
- ✅ **数据还原**: 使用对照表还原脱敏数据到原始值
- ✅ **文件预览**: 快速预览Excel文件结构和内容
- ✅ **Web界面**: 提供美观的网页操作界面，无需命令行

## 安装

```bash
# 进入项目目录
cd excel-data-desensitization

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### Web界面方式（推荐）

启动Web服务：
```bash
python app.py
```

然后打开浏览器访问：http://localhost:5000

**功能说明：**
1. **数据脱敏页签**
   - 上传Excel文件
   - 预览数据内容
   - 勾选需要脱敏的列
   - 选择脱敏模式（保留首尾/完全随机）
   - 一键脱敏并下载结果

2. **数据还原页签**
   - 上传脱敏后的Excel文件
   - 上传对照表
   - 一键还原原始数据

### 命令行方式

#### 1. 预览Excel文件

```bash
python main.py preview -i data.xlsx
```

### 2. 数据脱敏

**保留首尾字符模式（推荐）:**
```bash
python main.py desensitize \
  -i input.xlsx \
  -o masked.xlsx \
  -m mapping.xlsx \
  -c 姓名 手机号 身份证号
```

**完全随机替换模式:**
```bash
python main.py desensitize \
  -i input.xlsx \
  -o masked.xlsx \
  -m mapping.xlsx \
  -c 姓名 手机号 身份证号 \
  --full-mask
```

参数说明:
- `-i, --input`: 输入Excel文件路径
- `-o, --output`: 脱敏后Excel输出路径
- `-m, --mapping`: 对照表输出路径
- `-c, --columns`: 需要脱敏的列名（可指定多个）
- `--full-mask`: 完全随机替换（默认保留首尾字符）

### 3. 数据还原

```bash
python main.py restore \
  -d masked.xlsx \
  -m mapping.xlsx \
  -o restored.xlsx
```

参数说明:
- `-d, --desensitized`: 脱敏后的Excel路径
- `-m, --mapping`: 对照表路径
- `-o, --output`: 还原后Excel输出路径

## 示例

假设有以下原始数据 `users.xlsx`:

| 姓名 | 手机号 | 身份证号 | 地址 |
|------|--------|----------|------|
| 张三 | 13800138000 | 110101199001011234 | 北京市 |
| 李四 | 13900139000 | 310101198502023456 | 上海市 |

### 脱敏处理

```bash
python main.py desensitize -i users.xlsx -o users_masked.xlsx -m mapping.xlsx -c 姓名 手机号 身份证号
```

生成 `users_masked.xlsx`:

| 姓名 | 手机号 | 身份证号 | 地址 |
|------|--------|----------|------|
| 张*三 | 138*****000 | 110101********1234 | 北京市 |
| 李*四 | 139*****000 | 310101********3456 | 上海市 |

生成 `mapping.xlsx` 对照表:

| 列名 | 原始值 | 脱敏值 |
|------|--------|--------|
| 姓名 | 张三 | 张*三 |
| 姓名 | 李四 | 李*四 |
| 手机号 | 13800138000 | 138*****000 |
| ... | ... | ... |

### 还原处理

```bash
python main.py restore -d users_masked.xlsx -m mapping.xlsx -o users_restored.xlsx
```

还原后的 `users_restored.xlsx` 将与原始数据完全一致。

## 项目结构

```
excel-data-desensitization/
├── app.py                 # Web应用入口 (Flask)
├── main.py                # 命令行工具入口
├── desensitizer.py        # 脱敏核心模块
├── requirements.txt       # 依赖列表
├── README.md              # 使用说明
├── example_data.py        # 生成示例数据
├── test_demo.sh           # 测试演示脚本
├── build.py               # Windows EXE 打包脚本
├── pyinstaller.spec       # PyInstaller 打包配置
├── 打包说明.md             # Windows EXE 打包详细说明
├── .github/
│   └── workflows/
│       └── build-windows.yml  # GitHub Actions 自动打包配置
├── templates/
│   └── index.html         # Web页面模板
└── static/
    ├── style.css          # 页面样式
    └── script.js          # 页面交互逻辑
```

## 依赖

- Python >= 3.8
- pandas >= 2.0.0
- openpyxl >= 3.1.0
- Flask >= 2.3.0 (Web界面需要)
- Werkzeug >= 2.3.0 (Web界面需要)

## 打包成 Windows EXE

如果你想将本工具打包成 Windows 上无需安装 Python 即可运行的 exe 文件：

### 环境准备

1. 在 Windows 电脑上安装 Python 3.8+
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

### 打包步骤

**方式一：使用打包脚本（推荐）**
```bash
python build.py
```

**方式二：直接使用 PyInstaller**
```bash
pyinstaller --clean --noconfirm pyinstaller.spec
```

### 打包输出

打包完成后，会在 `dist/` 目录下生成：
```
dist/
└── Excel数据脱敏工具.exe
```

### 分发使用

1. 将 `dist/Excel数据脱敏工具.exe` 复制到任意 Windows 电脑
2. 双击运行，程序会自动打开浏览器
3. 无需安装 Python 或任何依赖

### 打包配置说明

- `pyinstaller.spec` - PyInstaller 打包配置文件
- `build.py` - 自动化打包脚本
- 打包后的文件会自动包含所有模板和静态资源

## 注意事项

1. **对照表安全**: 对照表包含原始敏感数据，请妥善保管
2. **数据备份**: 操作前建议备份原始数据
3. **列名匹配**: 脱敏和还原时，Excel中的列名必须与指定的一致
