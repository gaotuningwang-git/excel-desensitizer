#!/bin/bash
# 测试演示脚本

echo "========================================"
echo "  Excel数据脱敏工具 - 测试演示"
echo "========================================"
echo ""

# 1. 生成示例数据
echo "📋 步骤1: 生成示例数据..."
python example_data.py
echo ""

# 2. 预览原始数据
echo "📋 步骤2: 预览原始数据..."
python main.py preview -i sample_data.xlsx -n 3
echo ""

# 3. 脱敏处理
echo "📋 步骤3: 对敏感列进行脱敏..."
python main.py desensitize \
  -i sample_data.xlsx \
  -o sample_masked.xlsx \
  -m sample_mapping.xlsx \
  -c 姓名 手机号 身份证号 邮箱
echo ""

# 4. 查看脱敏结果
echo "📋 步骤4: 查看脱敏结果..."
python main.py preview -i sample_masked.xlsx -n 3
echo ""

# 5. 查看对照表
echo "📋 步骤5: 查看对照表..."
python main.py preview -i sample_mapping.xlsx -n 10
echo ""

# 6. 还原数据
echo "📋 步骤6: 还原脱敏数据..."
python main.py restore \
  -d sample_masked.xlsx \
  -m sample_mapping.xlsx \
  -o sample_restored.xlsx
echo ""

# 7. 查看还原结果
echo "📋 步骤7: 查看还原结果..."
python main.py preview -i sample_restored.xlsx -n 3
echo ""

echo "========================================"
echo "  测试完成!"
echo "========================================"
echo ""
echo "生成的文件:"
echo "  - sample_data.xlsx     (原始数据)"
echo "  - sample_masked.xlsx   (脱敏后数据)"
echo "  - sample_mapping.xlsx  (对照表)"
echo "  - sample_restored.xlsx (还原后数据)"
