"""
Excel数据脱敏工具核心模块
"""
import pandas as pd
import uuid
import json
from pathlib import Path
from typing import List, Dict, Optional


class ExcelDesensitizer:
    """Excel数据脱敏器"""

    def __init__(self):
        self.mapping: Dict[str, Dict[str, str]] = {}  # {列名: {原始值: 随机值}}

    def desensitize(
        self,
        input_path: str,
        output_path: str,
        mapping_path: str,
        columns: List[str],
        keep_first_last: bool = True
    ) -> None:
        """
        对Excel进行脱敏处理

        Args:
            input_path: 输入Excel路径
            output_path: 脱敏后Excel输出路径
            mapping_path: 对照表输出路径
            columns: 需要脱敏的列名列表
            keep_first_last: 是否保留首尾字符（如保留则显示为 张**三）
        """
        # 读取Excel
        df = pd.read_excel(input_path)

        # 检查列是否存在
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"列 '{col}' 不存在于Excel中，可用列: {list(df.columns)}")

        # 初始化映射表
        self.mapping = {col: {} for col in columns}

        # 处理每一列
        for col in columns:
            df[col] = df[col].apply(
                lambda x: self._mask_value(x, col, keep_first_last) if pd.notna(x) else x
            )

        # 保存脱敏后的Excel
        df.to_excel(output_path, index=False)
        print(f"✅ 脱敏后的Excel已保存: {output_path}")

        # 保存对照表
        mapping_df = self._create_mapping_df()
        mapping_df.to_excel(mapping_path, index=False)
        print(f"✅ 对照表已保存: {mapping_path}")

    def _mask_value(self, value, column: str, keep_first_last: bool) -> str:
        """对单个值进行脱敏"""
        original_str = str(value).strip()

        # 如果已经处理过，直接返回缓存的随机值
        if original_str in self.mapping[column]:
            return self.mapping[column][original_str]

        # 生成随机值
        if keep_first_last and len(original_str) > 2:
            # 保留首尾字符，中间用***替代
            masked = original_str[0] + '*' * (len(original_str) - 2) + original_str[-1]
        else:
            # 完全随机替换
            masked = f"MASK_{uuid.uuid4().hex[:8].upper()}"

        # 保存映射关系
        self.mapping[column][original_str] = masked

        return masked

    def _create_mapping_df(self) -> pd.DataFrame:
        """创建对照表DataFrame"""
        rows = []
        for column, mapping_dict in self.mapping.items():
            for original, masked in mapping_dict.items():
                rows.append({
                    '列名': column,
                    '原始值': original,
                    '脱敏值': masked
                })
        return pd.DataFrame(rows)

    def restore(
        self,
        desensitized_path: str,
        mapping_path: str,
        output_path: str
    ) -> None:
        """
        还原脱敏的Excel

        Args:
            desensitized_path: 脱敏后的Excel路径
            mapping_path: 对照表路径
            output_path: 还原后Excel输出路径
        """
        # 读取脱敏后的Excel和对照表
        df = pd.read_excel(desensitized_path)
        mapping_df = pd.read_excel(mapping_path)

        # 构建反向映射 {列名: {脱敏值: 原始值}}
        reverse_mapping: Dict[str, Dict[str, str]] = {}
        for _, row in mapping_df.iterrows():
            col = row['列名']
            original = row['原始值']
            masked = row['脱敏值']

            if col not in reverse_mapping:
                reverse_mapping[col] = {}
            reverse_mapping[col][masked] = original

        # 还原数据
        for col, mapping in reverse_mapping.items():
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: mapping.get(str(x).strip(), x) if pd.notna(x) else x
                )

        # 保存还原后的Excel
        df.to_excel(output_path, index=False)
        print(f"✅ 还原后的Excel已保存: {output_path}")


def preview_excel(file_path: str, n_rows: int = 5) -> None:
    """预览Excel文件"""
    df = pd.read_excel(file_path)
    print(f"\n📊 Excel预览 (共 {len(df)} 行, {len(df.columns)} 列)")
    print(f"列名: {list(df.columns)}")
    print(f"\n前 {n_rows} 行数据:")
    print(df.head(n_rows).to_string())
    print()
