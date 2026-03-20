#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发布机器人 - 单行详细格式解析器
版本：v1.0
日期：2026-03-13

格式特点：
- 单行一个产品
- 包含：料号 + 型号/类型 + 容量 + DC + 价格
- 可能包含品牌中文名
"""

import re
from typing import Dict, List, Optional


class DetailedLineParser:
    """单行详细格式解析器"""
    
    # 品牌识别（包含中英文）
    BRAND_PATTERNS = {
        'Samsung': [r'^K4', r'^KLM', r'三星'],
        'SK Hynix': [r'^H9C', r'^H5C', r'海力士', r' SK '],
        'Kingston': [r'金士顿', r'金士'],
        'Micron': [r'^MT\d', r'镁光', r'美光'],
        '南亚科技 (Nanya)': [r'^NT\d', r'南亚'],
        'GigaDevice': [r'兆易', r'^GD'],
        'Winbond': [r'华邦', '^W'],
        '晶存': [r'晶存'],
    }
    
    # 产品类型识别
    PRODUCT_TYPES = {
        'LPDDR4X': 'LPDDR4X',
        'LPDDR4': 'LPDDR4',
        'LPDDR5': 'LPDDR5',
        'LPDDR3': 'LPDDR3',
        'DDR4': 'DDR4',
        'DDR3': 'DDR3',
        'eMMC': 'eMMC',
        'EMMC': 'eMMC',
        'UFS': 'UFS',
        'NAND': 'NAND',
    }
    
    # 容量单位识别
    CAPACITY_UNITS = {
        'GB': 'GB',
        'MB': 'MB',
        'TB': 'TB',
        'gb': 'GB',
        'mb': 'MB',
    }
    
    def parse(self, text: str) -> List[Dict]:
        """
        解析单行详细格式
        
        Args:
            text: OFFER 文本
            
        Returns:
            产品列表
        """
        products = []
        lines = text.strip().split('\n')
        
        # 跳过标题行
        start_idx = 0
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if 'offer' in line_lower or '现货' in line_lower or '下单' in line_lower:
                start_idx = i + 1
                print(f"📋 识别到标题行，从第{i+2}行开始解析")
                break
        
        for i in range(start_idx, len(lines)):
            line = lines[i].strip()
            
            # 跳过空行和标题行
            if not line or 'offer' in line.lower() or '现货' in line.lower():
                continue
            
            # 解析产品
            product = self._parse_line(line)
            
            if product and product.get('料号型号'):
                products.append(product)
                print(f"✅ 解析：{product['料号型号']} - {product.get('产品分类', 'N/A')} {product.get('数量', '')} - USD {product['单价']} - DC{product['批次（DC）']}")
        
        return products
    
    def _parse_line(self, line: str) -> Optional[Dict]:
        """解析单行产品数据"""
        
        # 初始化产品
        product = {
            '企业名称': '鸿达半导体',
            '货主': None,
            '性别': None,
            '手机号': None,
            '微信': None,
            '产品名称': None,
            '品牌': None,
            '料号型号': None,
            '单价': None,
            '货币单位（usd/cny）': 'usd',
            '数量': None,  # 容量
            '单位': '个',
            '货所在地': 'HK',
            '批次（DC）': None,
            '货物情况（多选）': '全新',
            '产品分类': None,
            '应用': None,
            '起订量': None,
            '有效期': None,
            '交货天数': 7,
            '厂家': None,
            '重量': None,
            '尺寸 - 长': None,
            '尺寸 - 宽': None,
            '尺寸 - 高': None,
            '替代品牌': None,
            '替代型号': None,
        }
        
        # 1. 提取料号（行首的字母数字组合）
        part_match = re.match(r'^([A-Z0-9\-]+)', line)
        if part_match:
            product['料号型号'] = part_match.group(1)
            product['产品名称'] = part_match.group(1)
        
        if not product['料号型号']:
            return None
        
        # 2. 识别品牌
        product['品牌'] = self._identify_brand(line)
        product['厂家'] = product['品牌']
        
        # 3. 提取产品类型（LPDDR4X, LPDDR5, eMMC 等）
        for type_name, type_value in self.PRODUCT_TYPES.items():
            if type_name in line.upper():
                product['产品分类'] = type_value
                break
        
        # 4. 提取容量（2GB, 16GB 等）
        capacity_match = re.search(r'(\d+)\s*(GB|MB|TB)', line, re.IGNORECASE)
        if capacity_match:
            product['数量'] = int(capacity_match.group(1))
            product['单位'] = capacity_match.group(2).upper()
        
        # 5. 提取 DC（25+ 或 22+ 等，在容量之后）
        # 先找到容量位置，然后在容量后查找 DC
        capacity_match = re.search(r'(\d+)\s*(GB|MB|TB)', line, re.IGNORECASE)
        if capacity_match:
            # 在容量之后查找 DC
            remaining = line[capacity_match.end():]
            dc_match = re.search(r'(\d{2})\s*\+', remaining)
            if dc_match:
                product['批次（DC）'] = dc_match.group(1) + '+'
        
        # 6. 提取价格（48u, 22u, 90u 等，u 代表 USD）
        price_match = re.search(r'(\d+\.?\d*)\s*u\b', line, re.IGNORECASE)
        if price_match:
            try:
                product['单价'] = float(price_match.group(1))
            except:
                pass
        
        # 7. 特殊备注
        if '现货' in line:
            product['货所在地'] = 'HK'
            product['交货天数'] = 1
            product['货物情况（多选）'] = '现货'
        
        return product
    
    def _identify_brand(self, line: str) -> str:
        """根据料号或文本识别品牌"""
        for brand, patterns in self.BRAND_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return brand
        
        # 尝试从料号前缀识别
        part_match = re.match(r'^([A-Z]{2,}\d+)', line)
        if part_match:
            prefix = part_match.group(1)[:4]
            
            if prefix.startswith('K4') or prefix.startswith('KLM'):
                return 'Samsung'
            elif prefix.startswith('H9C') or prefix.startswith('H5C'):
                return 'SK Hynix'
            elif prefix.startswith('MT'):
                return 'Micron'
            elif prefix.startswith('NT'):
                return '南亚科技 (Nanya)'
        
        return '未知品牌'
    
    def parse_to_excel(self, text: str, output_file: str = None):
        """解析并生成 Excel"""
        from excel_generator import ExcelGenerator
        
        products = self.parse(text)
        
        if not products:
            print("❌ 没有解析到产品")
            return None
        
        generator = ExcelGenerator()
        
        if output_file is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"详细单行_{timestamp}.xlsx"
        
        filepath = generator.create_excel(products, output_file)
        print(f"\n✅ Excel 已生成：{filepath}")
        
        return filepath


if __name__ == '__main__':
    # 测试单行详细格式
    test_text = """
offer
K4U6E3S4AB-KHCL LPDDR4X 2GB 25+ 48u
K4F6E3S4HM-TFCL LPDDR4 2GB 25+ 48u
RS2G32LO5D4FDB-31BT 晶存 LPDDR5 8GB 25+ 90u 
EMMC16G-MW28-GA01 金士顿 16GB eMMC 25+ 22u 
H9CCNNNBJTALAR -NVDR 海力士 LPDDR3 2GB 22+ 20u 
香港现货，下单再确认！
"""
    
    parser = DetailedLineParser()
    products = parser.parse(test_text)
    
    print(f"\n{'='*60}")
    print(f"共解析 {len(products)} 个产品")
    print(f"{'='*60}\n")
    
    # 显示详情
    for i, p in enumerate(products, 1):
        print(f"{i}. {p['料号型号']}")
        print(f"   品牌：{p['品牌']}")
        print(f"   类型：{p['产品分类']}")
        print(f"   容量：{p['数量']}{p['单位']}")
        print(f"   价格：USD {p['单价']}")
        print(f"   DC: {p['批次（DC）']}")
        print()
    
    # 生成 Excel
    print("📄 生成 Excel...")
    parser.parse_to_excel(test_text)
