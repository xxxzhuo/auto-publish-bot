#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发布机器人 - OFFER 文本解析模块
版本：v1.0
日期：2026-03-13

功能：解析鸿达半导体 OFFER 文本格式，提取产品信息
"""

import re
from typing import Dict, List, Optional
from datetime import datetime


class OfferParser:
    """OFFER 文本解析器"""
    
    # 默认值
    DEFAULT_COMPANY = None  # 不默认，从文本提取
    DEFAULT_BRAND_MAP = {
        'NT6A': '南亚科技 (Nanya)',
        'H5C': 'SK Hynix',
        'H5AN': 'SK Hynix',
        'MT4': 'Micron',
        'MT40': 'Micron',
        'M32': 'Samsung',
    }
    
    # 供应商标识关键词
    COMPANY_PATTERNS = [
        r'^(.+?)\s*OFFER[:：]?\s*$',  # XXX OFFER:
        r'^(.+?)\s*现货[:：]?\s*$',    # XXX 现货:
        r'^(.+?)\s*实单[:：]?\s*$',    # XXX 实单:
        r'^(.+?)\s*开价[:：]?\s*$',    # XXX 开价:
    ]
    
    def __init__(self):
        self.products = []
    
    def parse_offer_text(self, text: str) -> List[Dict]:
        """
        解析 OFFER 文本
        
        Args:
            text: OFFER 文本内容
            
        Returns:
            产品列表
        """
        products = []
        lines = text.strip().split('\n')
        
        # 提取供应商名称（从标题行）
        company = self._extract_company(lines)
        print(f"🏢 供应商：{company or '未识别（将使用默认值）'}")
        
        current_product = None
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行和标题行
            if not line or self._is_title_line(line):
                continue
            
            # 尝试解析产品行
            product = self._parse_line(line, company)
            
            if product:
                products.append(product)
                print(f"✅ 解析：{product.get('料号型号')} - USD {product.get('单价')} - DC{product.get('批次（DC）', 'N/A')}")
        
        return products
    
    def _extract_company(self, lines: List[str]) -> Optional[str]:
        """从标题行提取供应商名称"""
        for line in lines[:5]:  # 只检查前 5 行
            line = line.strip()
            
            for pattern in self.COMPANY_PATTERNS:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    company = match.group(1).strip()
                    # 清理常见前缀
                    company = re.sub(r'^[出发][，,!]', '', company)
                    return company
        
        return None
    
    def _is_title_line(self, line: str) -> bool:
        """判断是否为标题行"""
        title_keywords = ['offer', '现货', '实单', '开价', '价格', '出，', '发，']
        line_lower = line.lower()
        
        for keyword in title_keywords:
            if keyword in line_lower:
                return True
        
        return False
    
    def _parse_line(self, line: str, company: str = None) -> Optional[Dict]:
        """解析单行产品信息"""
        
        # 初始化产品数据
        product = {
            '企业名称': company or None,  # 使用提取的供应商，不默认
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
            '货所在地': 'HK',  # 默认 HK
            '批次（DC）': None,
            '货物情况（多选）': '全新',
            '产品分类': '存储芯片',
            '应用': None,
            '起订量': None,
            '有效期': None,
            '交货天数': 7,  # 默认 7 天
            '厂家': None,
            '重量': None,
            '尺寸 - 长': None,
            '尺寸 - 宽': None,
            '尺寸 - 高': None,
            '替代品牌': None,
            '替代型号': None,
        }
        
        # 提取料号型号（多个正则模式匹配）
        part_patterns = [
            # 模式 1: NT6AN256T32AV-J2 类型
            r'(NT\d+[A-Z]+\d+[A-Z]*[-:]\w+)',
            # 模式 2: H5CG48MEBDX014N 类型
            r'(H5C\d+[A-Z]+\d+[A-Z])',
            # 模式 3: H5ANAG8NCJR-XNC 类型
            r'(H5AN\d+[A-Z]+[-:]\w+)',
            # 模式 4: MT41K256M16TW-107:P 类型
            r'(MT\d+[A-Z]+\d+[A-Z]*[-:]\d+[A-Z]:\w+)',
            # 模式 5: MT40A1G16TB-062E IT:F 类型
            r'(MT\d+[A-Z]+\d+[A-Z]*[-:]\d+[A-Z]\s*\w+:\w+)',
            # 模式 6: M323R4GA3EB0-CWM 类型
            r'(M32\d+[A-Z]+\d+[A-Z]*[-:]\w+)',
        ]
        
        part_number = None
        for pattern in part_patterns:
            match = re.search(pattern, line)
            if match:
                part_number = match.group(1).replace(' ', '')  # 移除空格
                break
        
        # 如果都没匹配到，尝试通用模式
        if not part_number:
            # 提取行首的料号（usd 之前的部分）
            match = re.match(r'^([A-Z]+\d+[A-Z0-9\-:]+)', line.strip())
            if match:
                part_number = match.group(1)
        
        if not part_number:
            return None
        
        product['料号型号'] = part_number
        product['产品名称'] = part_number  # 产品名称与料号相同
        
        # 识别品牌
        brand = self._identify_brand(part_number)
        product['品牌'] = brand
        product['厂家'] = brand
        
        # 提取价格（USD XXX 或 USDXXX）
        price_pattern = r'usd\s*(\d+\.?\d*)'
        price_match = re.search(price_pattern, line, re.IGNORECASE)
        
        if price_match:
            product['单价'] = float(price_match.group(1))
        
        # 提取 DC（dc21+ 或 dc 25+ 或 25+）
        dc_pattern = r'(?:dc\s*)?(\d{2}\+)'
        dc_match = re.search(dc_pattern, line, re.IGNORECASE)
        
        if dc_match:
            product['批次（DC）'] = dc_match.group(1)
        
        # 提取数量（XXX pcs 或 *XXX）
        qty_pattern = r'\*\s*(\d+)\s*pcs'
        qty_match = re.search(qty_pattern, line, re.IGNORECASE)
        
        if qty_match:
            product['数量'] = int(qty_match.group(1))
        
        # 提取货期（1week, 2days, next Monday 等）
        if '1week' in line.lower() or '1 week' in line.lower():
            product['交货天数'] = 7
        elif '2days' in line.lower() or '2 days' in line.lower():
            product['交货天数'] = 2
        elif 'next monday' in line.lower():
            product['交货天数'] = 14  # 下周一约 14 天
        elif 'stK' in line or 'stk' in line:
            product['交货天数'] = 1  # 现货
        
        # 提取地点信息
        if 'non cn' in line.lower() or 'NON CN' in line:
            product['货所在地'] = 'HK (Non-CN)'
        elif 'hk' in line.lower():
            product['货所在地'] = 'HK'
        elif 'partial' in line.lower():
            product['货物情况（多选）'] = '部分'
        
        # reel 包装
        if 'reel' in line.lower():
            product['货物情况（多选）'] = '全新 (Reel)'
        
        # 特殊备注
        if 'around' in line.lower():
            product['货物情况（多选）'] = '现货 around'
        
        return product
    
    def _identify_brand(self, part_number: str) -> str:
        """根据料号识别品牌"""
        for prefix, brand in self.DEFAULT_BRAND_MAP.items():
            if part_number.startswith(prefix):
                return brand
        return '未知品牌'
    
    def parse_offer_file(self, filepath: str) -> List[Dict]:
        """
        解析 OFFER 文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            产品列表
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.parse_offer_text(content)
            
        except Exception as e:
            print(f"❌ 读取文件失败：{e}")
            return []
    
    def save_to_file(self, filepath: str, text: str):
        """保存 OFFER 文本到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"✅ OFFER 已保存：{filepath}")


if __name__ == '__main__':
    # 测试 OFFER 解析
    offer_text = """
鸿达半导体 OFFER:
NT6AN256T32AV-J2 usd 19.5, reel, dc21+ , 1week 
H5CG48MEBDX014N usd 27.5，dc 25+ 
"""
    
    parser = OfferParser()
    products = parser.parse_offer_text(offer_text)
    
    print(f"\n共解析 {len(products)} 个产品")
    for p in products:
        print(f"  {p['料号型号']} - {p['品牌']} - USD {p['单价']} - DC{p['批次（DC）']}")
