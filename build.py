#!/usr/bin/env python3
"""
Excel数据脱敏工具 - Windows EXE 打包脚本
"""
import subprocess
import sys
import shutil
from pathlib import Path

def build():
    """使用 PyInstaller 打包"""
    print("=" * 60)
    print("Excel数据脱敏工具 - Windows EXE 打包")
    print("=" * 60)
    print()

    # 检查 pyinstaller 是否安装
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
    except ImportError:
        print("✗ PyInstaller 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✓ PyInstaller 安装完成")
    print()

    # 清理旧的构建目录
    print("清理旧的构建文件...")
    for dir_name in ['build', 'dist']:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"  删除 {dir_name}/")
    print()

    # 运行 PyInstaller
    print("开始打包...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "pyinstaller.spec"
    ]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print()
        print("=" * 60)
        print("✓ 打包成功！")
        print("=" * 60)
        print()
        print("输出文件:")
        print("  dist/Excel数据脱敏工具.exe")
        print()
        print("使用说明:")
        print("  1. 将整个 dist 文件夹复制到目标电脑")
        print("  2. 双击 'Excel数据脱敏工具.exe' 运行")
        print("  3. 程序会自动打开浏览器")
        print()
    else:
        print("✗ 打包失败")
        sys.exit(1)

if __name__ == '__main__':
    build()
