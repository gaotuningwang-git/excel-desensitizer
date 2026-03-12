#!/usr/bin/env python3
"""
Excel数据脱敏工具 - 命令行版本

功能:
1. 脱敏: 导入Excel，将指定列用随机值替代，生成脱敏Excel和对照表
2. 还原: 导入脱敏Excel和对照表，还原原始Excel

命令行用法:
    python main.py desensitize -i input.xlsx -o output.xlsx -m mapping.xlsx -c 姓名 手机号 身份证号
    python main.py restore -d desensitized.xlsx -m mapping.xlsx -o restored.xlsx
    python main.py preview -i input.xlsx

Web界面用法:
    python app.py
    然后访问 http://localhost:5000
"""
import argparse
import sys
from pathlib import Path

from desensitizer import ExcelDesensitizer, preview_excel


def main():
    parser = argparse.ArgumentParser(
        description='Excel数据脱敏工具 - 对敏感数据进行脱敏和还原',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览Excel文件
  python main.py preview -i data.xlsx

  # 脱敏处理（保留首尾字符）
  python main.py desensitize -i data.xlsx -o masked.xlsx -m mapping.xlsx -c 姓名 手机号

  # 脱敏处理（完全随机替换）
  python main.py desensitize -i data.xlsx -o masked.xlsx -m mapping.xlsx -c 姓名 --full-mask

  # 还原数据
  python main.py restore -d masked.xlsx -m mapping.xlsx -o restored.xlsx
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 预览命令
    preview_parser = subparsers.add_parser('preview', help='预览Excel文件')
    preview_parser.add_argument('-i', '--input', required=True, help='输入Excel文件路径')
    preview_parser.add_argument('-n', '--rows', type=int, default=5, help='显示行数（默认5）')

    # 脱敏命令
    desensitize_parser = subparsers.add_parser('desensitize', help='对Excel进行脱敏')
    desensitize_parser.add_argument('-i', '--input', required=True, help='输入Excel文件路径')
    desensitize_parser.add_argument('-o', '--output', required=True, help='脱敏后Excel输出路径')
    desensitize_parser.add_argument('-m', '--mapping', required=True, help='对照表输出路径')
    desensitize_parser.add_argument(
        '-c', '--columns',
        nargs='+',
        required=True,
        help='需要脱敏的列名（可指定多个）'
    )
    desensitize_parser.add_argument(
        '--full-mask',
        action='store_true',
        help='完全随机替换（默认保留首尾字符）'
    )

    # 还原命令
    restore_parser = subparsers.add_parser('restore', help='还原脱敏的Excel')
    restore_parser.add_argument('-d', '--desensitized', required=True, help='脱敏后的Excel路径')
    restore_parser.add_argument('-m', '--mapping', required=True, help='对照表路径')
    restore_parser.add_argument('-o', '--output', required=True, help='还原后Excel输出路径')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'preview':
            preview_excel(args.input, args.rows)

        elif args.command == 'desensitize':
            print(f"🔐 开始脱敏处理...")
            print(f"   输入文件: {args.input}")
            print(f"   脱敏列: {args.columns}")
            print(f"   模式: {'完全随机' if args.full_mask else '保留首尾字符'}")
            print()

            desensitizer = ExcelDesensitizer()
            desensitizer.desensitize(
                input_path=args.input,
                output_path=args.output,
                mapping_path=args.mapping,
                columns=args.columns,
                keep_first_last=not args.full_mask
            )
            print("\n✨ 脱敏完成!")

        elif args.command == 'restore':
            print(f"🔓 开始还原数据...")
            print(f"   脱敏文件: {args.desensitized}")
            print(f"   对照表: {args.mapping}")
            print()

            desensitizer = ExcelDesensitizer()
            desensitizer.restore(
                desensitized_path=args.desensitized,
                mapping_path=args.mapping,
                output_path=args.output
            )
            print("\n✨ 还原完成!")

    except FileNotFoundError as e:
        print(f"❌ 错误: 文件不存在 - {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
