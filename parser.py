#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发布机器人 - 产品信息解析模块
版本：v1.0
日期：2026-03-13
"""

import os
import re
from typing import Dict, List, Optional
from pathlib import Path
import sys
sys.path.append('/Users/mac/Desktop/自动发布机器人')
from config import PRODUCTS_DIR


class ProductParser:
    """产品信息解析器"""
    
    # 字段映射（txt 中的字段名 → Excel 中的列名）
    FIELD_MAPPING = {
        '产品名称': '产品名称',
        '产品名': '产品名称',
        '名称': '产品名称',
        '品牌': '品牌',
        '品牌名': '品牌',
        '型号': '料号型号',
        '料号': '料号型号',
        '料号型号': '料号型号',
        'part': '料号型号',
        'part_number': '料号型号',
        '单价': '单价',
        '价格': '单价',
        'price': '单价',
        '货币': '货币单位（usd/cny）',
        '货币单位': '货币单位（usd/cny）',
        'currency': '货币单位（usd/cny）',
        '数量': '数量',
        'qty': '数量',
        'quantity': '数量',
        '单位': '单位',
        '货所在地': '货所在地',
        '所在地': '货所在地',
        '地点': '货所在地',
        '批次': '批次（DC）',
        'dc': '批次（DC）',
        'date_code': '批次（DC）',
        '货物情况': '货物情况（多选）',
        '成色': '货物情况（多选）',
        '情况': '货物情况（多选）',
        '产品分类': '产品分类',
        '分类': '产品分类',
        '应用': '应用',
        '起订量': '起订量',
        'moq': '起订量',
        '有效期': '有效期',
        '交货天数': '交货天数',
        '交期': '交货天数',
        '厂家': '厂家',
        '厂商': '厂家',
        '重量': '重量',
        '尺寸': '尺寸 - 长',  # 特殊处理
        '长': '尺寸 - 长',
        '宽': '尺寸 - 宽',
        '高': '尺寸 - 高',
        '替代品牌': '替代品牌',
        '替代': '替代品牌',
        '替代型号': '替代型号',
        '企业名称': '企业名称',
        '公司': '企业名称',
        '货主': '货主',
        '姓名': '货主',
        '性别': '性别',
        '手机号': '手机号',
        '电话': '手机号',
        '微信': '微信',
        'wechat': '微信',
    }
    
    # Excel 列顺序（标准格式）
    EXCEL_COLUMNS = [
        '企业名称', '货主', '性别', '手机号', '微信', '产品名称', '品牌', '料号型号',
        '单价', '货币单位（usd/cny）', '数量', '单位', '货所在地', '批次（DC）',
        '货物情况（多选）', '产品分类', '应用', '起订量', '有效期', '交货天数',
        '厂家', '重量', '尺寸 - 长', '尺寸 - 宽', '尺寸 - 高', '替代品牌', '替代型号'
    ]
    
    def __init__(self):
        self.products = []
    
    def parse_file(self, file_path: str) -> Optional[Dict]:
        """
        解析单个产品文件
        
        Args:
            file_path: txt 文件路径
            
        Returns:
            产品数据字典（Excel 格式）
        """
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在：{file_path}")
            return None
        
        product_data = {col: None for col in self.EXCEL_COLUMNS}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 逐行解析
            for line in content.strip().split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 支持多种分隔符（包括全角/半角冒号）
                fullwidth_colon = chr(0xFF1A)  # 全角冒号：
                halfwidth_colon = chr(0x003A)  # 半角冒号:
                
                if fullwidth_colon in line:
                    key, value = line.split(fullwidth_colon, 1)
                elif halfwidth_colon in line:
                    key, value = line.split(halfwidth_colon, 1)
                elif '=' in line:
                    key, value = line.split('=', 1)
                else:
                    continue
                
                key = key.strip()
                value = value.strip()
                
                if not key or not value:
                    continue
                
                # 字段映射
                excel_field = self.FIELD_MAPPING.get(key)
                
                if excel_field:
                    product_data[excel_field] = value
                else:
                    # 尝试模糊匹配
                    matched = self.fuzzy_match(key)
                    if matched:
                        product_data[matched] = value
            
            # 设置默认值
            if product_data['货币单位（usd/cny）'] is None:
                product_data['货币单位（usd/cny）'] = 'cny'
            
            if product_data['单位'] is None:
                product_data['单位'] = '个'
            
            print(f"✅ 解析成功：{file_path}")
            print(f"   产品：{product_data.get('产品名称', 'N/A')} | 品牌：{product_data.get('品牌', 'N/A')} | 型号：{product_data.get('料号型号', 'N/A')}")
            
            return product_data
            
        except Exception as e:
            print(f"❌ 解析失败 {file_path}: {e}")
            return None
    
    def fuzzy_match(self, key: str) -> Optional[str]:
        """模糊匹配字段名"""
        key_lower = key.lower()
        
        for txt_key, excel_key in self.FIELD_MAPPING.items():
            if txt_key.lower() in key_lower or key_lower in txt_key.lower():
                return excel_key
        
        return None
    
    def parse_directory(self, directory: str = None) -> List[Dict]:
        """
        解析目录下所有产品文件
        
        Args:
            directory: 目录路径，默认使用 PRODUCTS_DIR
            
        Returns:
            产品数据列表
        """
        if directory is None:
            directory = PRODUCTS_DIR
        
        if not os.path.exists(directory):
            print(f"❌ 目录不存在：{directory}")
            return []
        
        products = []
        
        # 查找所有 txt 文件
        txt_files = list(Path(directory).glob('*.txt'))
        
        if not txt_files:
            print(f"⚠️  目录中没有找到 txt 文件：{directory}")
            return products
        
        print(f"📂 找到 {len(txt_files)} 个产品文件")
        
        for txt_file in txt_files:
            product_data = self.parse_file(str(txt_file))
            if product_data:
                products.append(product_data)
        
        print(f"✅ 共解析 {len(products)} 个有效产品")
        return products


if __name__ == '__main__':
    # 测试解析
    parser = ProductParser()
    products = parser.parse_directory()
    
    if products:
        print(f"\n解析结果：{len(products)} 个产品")
        for i, p in enumerate(products[:3], 1):  # 只显示前 3 个
            print(f"\n产品{i}:")
            for k, v in p.items():
                if v:
                    print(f"  {k}: {v}")
