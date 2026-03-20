#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发布机器人 - 通用格式识别器
版本：v1.0
日期：2026-03-13

功能：自动识别多种 OFFER 格式并解析
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class UniversalOfferParser:
    """通用 OFFER 解析器 - 支持多种格式"""
    
    # 品牌识别规则
    BRAND_PATTERNS = {
        '南亚科技 (Nanya)': [r'^NT\d+A', r'^NT\d+T'],
        'SK Hynix': [r'^H5C', r'^H5AN', r'^H9HC'],
        'Micron': [r'^MT\d', r'^MT4', r'^25Q', r'^29F'],
        'Samsung': [r'^M32\d', r'^K4', r'^K8', r'^KMZ'],
        'Intel': [r'^29F\d', r'^SSD'],
        'Kingston': [r'^D\d', r'^KVR'],
    }
    
    def __init__(self):
        self.format_detected = None
        self.products = []
    
    def detect_format(self, text: str) -> str:
        """
        检测 OFFER 文本格式
        
        支持的格式：
        1. 鸿达格式：料号 usd 价格，dc 批次
        2. 香港现货：标题 + 两行一个产品
        3. 单行详细：料号 类型 容量 DC 价格
        4. 标准格式：料号 | 品牌 | 价格 | 数量 | DC
        5. 表格格式：料号，品牌，单价，数量，DC
        6. 简短格式：料号 价格 DC
        7. 邮件格式：Part: xxx, Price: xxx, DC: xxx
        """
        
        lines = text.strip().split('\n')
        
        # 检测特征
        has_hkstock_title = any(line.strip() == '出，香港现货！' for line in lines)  # 精确匹配标题
        has_detailed = any(re.search(r'[A-Z0-9\-]+\s+[A-Z0-9]+\s+\d+GB', line) for line in lines)  # 料号 + 类型 + 容量
        has_pipe = any('|' in line for line in lines)
        has_usd = any('usd' in line.lower() for line in lines)
        has_part_prefix = any(line.lower().startswith('part') for line in lines)
        has_price_prefix = any('price' in line.lower() for line in lines)
        has_comma_separated = any(line.count(',') >= 3 for line in lines)
        
        # 检测香港现货格式（两行一个产品）
        if has_hkstock_title:
            return 'hkstock_format'
        elif has_detailed:
            return 'detailed_format'  # 单行详细格式
        elif has_pipe:
            return 'table_pipe'  # 表格格式（竖线分隔）
        elif has_part_prefix or has_price_prefix:
            return 'email_format'  # 邮件格式
        elif has_comma_separated and not has_usd:
            return 'csv_format'  # CSV 格式
        elif has_usd:
            return 'hongda_format'  # 鸿达格式
        else:
            return 'short_format'  # 简短格式
    
    def parse(self, text: str) -> List[Dict]:
        """
        通用解析入口
        
        Args:
            text: OFFER 文本
            
        Returns:
            产品列表
        """
        self.format_detected = self.detect_format(text)
        
        print(f"📋 检测到格式：{self.format_detected}")
        
        if self.format_detected == 'detailed_format':
            return self._parse_detailed(text)
        elif self.format_detected == 'hkstock_format':
            return self._parse_hkstock(text)
        elif self.format_detected == 'hongda_format':
            return self._parse_hongda(text)
        elif self.format_detected == 'table_pipe':
            return self._parse_table_pipe(text)
        elif self.format_detected == 'email_format':
            return self._parse_email(text)
        elif self.format_detected == 'csv_format':
            return self._parse_csv(text)
        elif self.format_detected == 'short_format':
            return self._parse_short(text)
        else:
            return self._parse_hongda(text)  # 默认使用鸿达格式
    
    def _parse_detailed(self, text: str) -> List[Dict]:
        """解析单行详细格式"""
        from detailed_parser import DetailedLineParser
        parser = DetailedLineParser()
        return parser.parse(text)
    
    def _parse_hkstock(self, text: str) -> List[Dict]:
        """解析香港现货格式"""
        from hkstock_parser import HKStockParser
        parser = HKStockParser()
        return parser.parse(text)
    
    def _parse_hongda(self, text: str) -> List[Dict]:
        """解析鸿达格式"""
        from offer_parser import OfferParser
        parser = OfferParser()
        return parser.parse_offer_text(text)
    
    def _parse_table_pipe(self, text: str) -> List[Dict]:
        """解析表格格式（竖线分隔）"""
        products = []
        lines = text.strip().split('\n')
        
        headers = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 分割字段
            fields = [f.strip() for f in line.split('|')]
            
            # 第一行作为表头
            if headers is None:
                headers = fields
                continue
            
            # 解析产品
            product = self._fields_to_product(headers, fields)
            if product and product.get('料号型号'):
                products.append(product)
                print(f"✅ 解析：{product['料号型号']}")
        
        return products
    
    def _parse_email(self, text: str) -> List[Dict]:
        """解析邮件格式"""
        products = []
        
        # 提取产品块（按空行分割）
        blocks = re.split(r'\n\s*\n', text)
        
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            
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
                '数量': None,
                '单位': '个',
                '货所在地': 'HK',
                '批次（DC）': None,
                '货物情况（多选）': '全新',
                '产品分类': '存储芯片',
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
            
            # 解析键值对
            patterns = {
                '料号型号': [r'(?:Part(?: Number)?|MPN|Model)[:\s]+([A-Z0-9\-:]+)', r'^([A-Z]{2,}\d+[A-Z0-9\-]+)'],
                '品牌': [r'(?:Brand|Mfr|Manufacturer)[:\s]+([A-Za-z\s]+)'],
                '单价': [r'(?:Price|Unit Price|USD)[:\s]+\$?([\d.]+)'],
                '数量': [r'(?:Qty|Quantity|Stock)[:\s]+(\d+)'],
                '批次（DC）': [r'(?:DC|Date Code|Batch)[:\s]+(\d+\+?)'],
            }
            
            for field, pattern_list in patterns.items():
                for pattern in pattern_list:
                    match = re.search(pattern, block, re.IGNORECASE)
                    if match:
                        value = match.group(1).strip()
                        if field == '单价':
                            try:
                                product[field] = float(value)
                            except:
                                pass
                        elif field == '数量':
                            try:
                                product[field] = int(value)
                            except:
                                pass
                        else:
                            product[field] = value
                        break
            
            # 识别品牌
            if product['料号型号'] and not product['品牌']:
                product['品牌'] = self._identify_brand(product['料号型号'])
                product['厂家'] = product['品牌']
            
            if product['料号型号']:
                product['产品名称'] = product['料号型号']
                products.append(product)
                print(f"✅ 解析：{product['料号型号']}")
        
        return products
    
    def _parse_csv(self, text: str) -> List[Dict]:
        """解析 CSV 格式（逗号分隔）"""
        products = []
        lines = text.strip().split('\n')
        
        headers = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 分割字段
            fields = [f.strip() for f in line.split(',')]
            
            # 第一行作为表头
            if headers is None:
                headers = fields
                continue
            
            # 解析产品
            product = self._fields_to_product(headers, fields)
            if product and product.get('料号型号'):
                products.append(product)
                print(f"✅ 解析：{product['料号型号']}")
        
        return products
    
    def _parse_short(self, text: str) -> List[Dict]:
        """解析简短格式"""
        products = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 尝试提取料号（行首的字母数字组合）
            part_match = re.match(r'^([A-Z]{2,}\d+[A-Z0-9\-:]+)', line)
            
            if part_match:
                part_number = part_match.group(1)
                
                product = {
                    '企业名称': '鸿达半导体',
                    '料号型号': part_number,
                    '产品名称': part_number,
                    '品牌': self._identify_brand(part_number),
                    '厂家': self._identify_brand(part_number),
                    '单价': None,
                    '货币单位（usd/cny）': 'usd',
                    '数量': None,
                    '批次（DC）': None,
                    '货所在地': 'HK',
                    '交货天数': 7,
                    '货物情况（多选）': '全新',
                    '产品分类': '存储芯片',
                }
                
                # 提取价格
                price_match = re.search(r'\$?([\d.]+)', line)
                if price_match:
                    try:
                        product['单价'] = float(price_match.group(1))
                    except:
                        pass
                
                # 提取 DC
                dc_match = re.search(r'(\d{2}\+)', line)
                if dc_match:
                    product['批次（DC）'] = dc_match.group(1)
                
                products.append(product)
                print(f"✅ 解析：{part_number}")
        
        return products
    
    def _fields_to_product(self, headers: List[str], fields: List[str]) -> Dict:
        """将字段列表转换为产品字典"""
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
            '数量': None,
            '单位': '个',
            '货所在地': 'HK',
            '批次（DC）': None,
            '货物情况（多选）': '全新',
            '产品分类': '存储芯片',
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
        
        # 字段名映射
        field_map = {
            '料号': '料号型号',
            '料号型号': '料号型号',
            'part': '料号型号',
            'part number': '料号型号',
            'mpn': '料号型号',
            '型号': '料号型号',
            '品牌': '品牌',
            'brand': '品牌',
            'mfr': '品牌',
            'manufacturer': '品牌',
            '单价': '单价',
            '价格': '单价',
            'price': '单价',
            'unit price': '单价',
            'usd': '单价',
            '数量': '数量',
            'qty': '数量',
            'quantity': '数量',
            'stock': '数量',
            'dc': '批次（DC）',
            '批次': '批次（DC）',
            'date code': '批次（DC）',
            'batch': '批次（DC）',
            '货所在地': '货所在地',
            '地点': '货所在地',
            'location': '货所在地',
            '交期': '交货天数',
            '交货期': '交货天数',
            'lead time': '交货天数',
        }
        
        for i, header in enumerate(headers):
            if i >= len(fields):
                break
            
            header_lower = header.lower().strip()
            mapped_field = field_map.get(header_lower, header_lower)
            
            if mapped_field in product:
                value = fields[i].strip()
                
                if not value or value == '-':
                    continue
                
                # 类型转换
                if mapped_field == '单价':
                    try:
                        value = float(value.replace('$', '').replace(',', ''))
                    except:
                        pass
                elif mapped_field == '数量':
                    try:
                        value = int(value.replace(',', ''))
                    except:
                        pass
                
                product[mapped_field] = value
        
        # 自动识别品牌
        if product['料号型号'] and not product['品牌']:
            product['品牌'] = self._identify_brand(product['料号型号'])
            product['厂家'] = product['品牌']
        
        if product['料号型号']:
            product['产品名称'] = product['料号型号']
        
        return product
    
    def _identify_brand(self, part_number: str) -> str:
        """根据料号识别品牌"""
        for brand, patterns in self.BRAND_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, part_number, re.IGNORECASE):
                    return brand
        return '未知品牌'


if __name__ == '__main__':
    # 测试多种格式
    parser = UniversalOfferParser()
    
    # 测试 1: 鸿达格式
    print("=" * 60)
    print("测试 1: 鸿达格式")
    print("=" * 60)
    text1 = """
NT6AN256T32AV-J2 usd 19.5, reel, dc21+
H5CG48MEBDX014N usd 27.5，dc 25+
"""
    products1 = parser.parse(text1)
    print(f"解析 {len(products1)} 个产品\n")
    
    # 测试 2: 表格格式
    print("=" * 60)
    print("测试 2: 表格格式（竖线分隔）")
    print("=" * 60)
    text2 = """
料号型号 | 品牌 | 单价 | 数量 | DC
MT41K256M16TW-107:P | Micron | 5.5 | 1000 | 25+
H5CG48MEBDX014N | SK Hynix | 27.5 | 500 | 25+
"""
    products2 = parser.parse(text2)
    print(f"解析 {len(products2)} 个产品\n")
    
    # 测试 3: 邮件格式
    print("=" * 60)
    print("测试 3: 邮件格式")
    print("=" * 60)
    text3 = """
Part: NT6AN256T32AV-J2
Brand: Nanya
Price: 19.5
DC: 21+
Qty: 100

Part: H5CG48MEBDX014N
Brand: SK Hynix
Price: 27.5
DC: 25+
"""
    products3 = parser.parse(text3)
    print(f"解析 {len(products3)} 个产品\n")
