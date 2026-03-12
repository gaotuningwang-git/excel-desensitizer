#!/bin/bash
# GitHub 仓库初始化脚本

echo "=================================="
echo "Excel数据脱敏工具 - GitHub 初始化"
echo "=================================="
echo ""

# 检查是否已初始化
if [ -d ".git" ]; then
    echo "✓ Git 仓库已存在"
else
    echo "→ 初始化 Git 仓库..."
    git init
    echo "✓ Git 仓库初始化完成"
fi

echo ""
echo "→ 添加文件到 Git..."
git add .

echo ""
echo "→ 提交更改..."
git commit -m "Initial commit: Excel数据脱敏工具"

echo ""
echo "=================================="
echo "✓ 本地 Git 仓库初始化完成"
echo "=================================="
echo ""
echo "下一步操作："
echo ""
echo "1. 在 GitHub 创建新仓库："
echo "   https://github.com/new"
echo ""
echo "2. 创建后，运行以下命令推送代码："
echo "   git remote add origin https://github.com/你的用户名/仓库名.git"
echo "   git push -u origin main"
echo ""
echo "3. 推送后，访问 Actions 页面查看打包状态："
echo "   https://github.com/你的用户名/仓库名/actions"
echo ""
echo "详细说明请查看：打包说明.md"
echo ""
