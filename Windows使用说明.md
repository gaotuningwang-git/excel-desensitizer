# Windows 使用说明

## 常见问题

### 1. 提示"找不到系统程序"或无法运行（缺少 VCRUNTIME140.dll 等）

**原因**：Windows 缺少 Microsoft Visual C++ Redistributable 运行时库

**解决方案**：
- **方法1**：下载并安装 Microsoft Visual C++ Redistributable：
  https://aka.ms/vs/17/release/vc_redist.x64.exe

- **方法2**：如果无法安装运行时，可以安装完整 Python 后运行源码：
  ```
  pip install pandas openpyxl Flask Werkzeug
  python app.py
  ```

### 2. 杀毒软件拦截或报毒

**原因**：PyInstaller 打包的程序有时会被误报

**解决方案**：
- 将 `Excel数据脱敏工具.exe` 添加到杀毒软件白名单
- 或暂时关闭杀毒软件后再运行

### 3. 双击后没有反应

**原因**：程序在后台运行，但没有自动打开浏览器

**解决方案**：
1. 打开浏览器
2. 访问 http://127.0.0.1:5000

### 4. 端口被占用

**原因**：5000端口被其他程序占用

**解决方案**：
- 关闭占用 5000 端口的程序
- 或修改 app.py 中的端口号

## 使用方法

1. **双击运行** `Excel数据脱敏工具.exe`
2. **等待 1-2 秒**，程序会自动打开浏览器
3. 如果浏览器没有自动打开，**手动访问** http://127.0.0.1:5000
4. 使用完毕后，**关闭浏览器**，在任务栏找到程序图标右键退出

## 数据安全

- 所有处理都在本地进行，不会上传到任何服务器
- 临时文件保存在用户目录下的 `.excel_desensitizer` 文件夹
- 对照表包含原始数据，请妥善保管
