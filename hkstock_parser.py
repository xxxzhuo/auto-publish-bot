#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发布机器人 - 香港现货格式解析器（重写版）
版本：v3.0
日期：2026-03-13

改进：
1. 增强的文本预处理
2. 逐行识别产品
3. 不依赖格式检测
"""

import re
from typing import Dict, List, Optional


class HKStockParser:
    """香港现货格式解析器（重写版）"""
    
    # 品牌识别规则
    BRAND_PATTERNS = {
        'Micron': [r'^MT\d', r'^MT4', r'^MT5', r'^MT6', r'^MT29', r'^MT62F'],
        '南亚科技 (Nanya)': [r'^NT5', r'^NT6'],
        'Samsung': [
            r'^K4', r'^KLM', r'^K4A', r'^K4B', r'^K4U', r'^K4F', r'^K3K',
            r'^KMF', r'^KLUD', r'^HN8T', r'^H26T', r'^THG', r'^K4AAG'
        ],
        'SK Hynix': [r'^H5C', r'^H5AN', r'^H5AG'],
    }
    
    # 备注关键词
    REMARK_KEYWORDS = {
        '小盒开': '小盒装',
        '托盘': '托盘装',
        '涂标': '涂标货',
        'reel': 'Reel 装',
        'bulk': '散装',
    }
    
    def parse(self, text: str) -> List[Dict]:
        """
        解析香港现货格式（重写版）
        
        流程：
        1. 文本预处理（清理空格、空行）
        2. 提取供应商（从第一行）
        3. 逐行识别产品
        
        Args:
            text: OFFER 文本
            
        Returns:
            产品列表
        """
        products = []
        
        # 步骤 1: 文本预处理
        lines = self._preprocess_text(text)
        
        if not lines:
            print("❌ 预处理后无有效行")
            return products
        
        print(f"📋 预处理后行数：{len(lines)}")
        
        # 步骤 2: 提取供应商（从第一行）
        company = self._extract_company(lines[0])
        print(f"🏢 供应商：{company or '未识别'}")
        
        # 步骤 3: 逐行识别产品（跳过第一行标题）
        print(f"\n开始解析产品...")
        for i, line in enumerate(lines[1:], 1):
            product = self._parse_product_line(line, company)
            if product:
                products.append(product)
                print(f"✅ [{i}] {product['料号型号']} - {product['品牌']} - USD {product['单价']} - DC{product['批次（DC）']}")
        
        print(f"\n共解析 {len(products)} 个产品")
        return products
    
    def _preprocess_text(self, text: str) -> List[str]:
        """
        文本预处理
        
        操作：
        1. 分割成行
        2. 去除每行首尾空格
        3. 去除空行
        4. 合并多余空格
        """
        # 分割成行
        raw_lines = text.strip().split('\n')
        
        # 处理每行
        processed = []
        for line in raw_lines:
            # 去除首尾空格
            line = line.strip()
            
            # 跳过空行
            if not line:
                continue
            
            # 合并多余空格（多个空格变一个）
            line = re.sub(r'\s+', ' ', line)
            
            # 添加到结果
            processed.append(line)
        
        return processed
    
    def _extract_company(self, first_line: str) -> Optional[str]:
        """从第一行提取供应商名称"""
        line = first_line.strip()
        
        # 模式 1: XXX 香港现货 / XXX 实单 / XXX 开价
        patterns = [
            (r'^(.+?)\s*香港现货', 1),
            (r'^(.+?)\s*实单', 1),
            (r'^(.+?)\s*开价', 1),
            (r'^(.+?)\s*OFFER', 1),
            (r'^[出发][，,!\s]+\s*(.+)', 1),
        ]
        
        for pattern, group in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                company = match.group(group).strip()
                # 清理后缀
                company = re.sub(r'\s*(香港 | 现货 | 实单 | 开价|OFFER).*$', '', company, flags=re.IGNORECASE)
                company = company.strip()
                return company if company else None
        
        return None
    
    def _parse_product_line(self, line: str, company: str = None) -> Optional[Dict]:
        """
        解析单行产品数据
        
        支持的格式：
        1. 料号 DC+ 价格 U（如：K3KL9L900M-MFCT 25+ 170U）
        2. 料号 价格 U DC+（如：K3KL9L900M-MFCT 170U 25+）
        3. 料号 备注 DC+ 价格 U（如：MT62F2G32D4DS-023 AIT:C 25+ 285U）
        """
        line = line.strip()
        
        if not line:
            return None
        
        # 跳过标题行（包含"现货"、"实单"、"开价"、"OFFER"等）
        if any(kw in line.upper() for kw in ['现货', '实单', '开价', 'OFFER', '出，', '发，']):
            return None
        
        # 提取料号（行首的字母数字组合，包含连字符/冒号）
        part_match = re.match(r'^([A-Z0-9\-:]+)', line)
        if not part_match:
            print(f"  ⚠️  无法提取料号：{line}")
            return None
        
        part_number = part_match.group(1)
        
        # 验证料号合理性（至少包含字母和数字）
        if not (re.search(r'[A-Z]', part_number) and re.search(r'\d', part_number)):
            print(f"  ⚠️  料号格式异常：{part_number}")
            return None
        
        # 初始化产品
        product = {
            '企业名称': company,
            '料号型号': part_number,
            '产品名称': part_number,
            '品牌': self._identify_brand(part_number),
            '厂家': self._identify_brand(part_number),
            '单价': None,
            '货币单位（usd/cny）': 'usd',
            '数量': None,
            '单位': '个',
            '货所在地': 'HK',
            '批次（DC）': None,
            '货物情况（多选）': '全新',
            '产品分类': '存储芯片',
            '交货天数': 1,
            '应用': None,
            '起订量': None,
            '有效期': None,
        }
        
        # 提取 DC（数字 + 号，如 25+）
        dc_match = re.search(r'(\d{2})\s*\+', line)
        if dc_match:
            product['批次（DC）'] = dc_match.group(1) + '+'
        
        # 提取价格（数字 + U/USD，如 170U, 285U）
        price_match = re.search(r'(\d+\.?\d*)\s*(?:USD|U)\b', line, re.IGNORECASE)
        if price_match:
            try:
                product['单价'] = float(price_match.group(1))
            except:
                pass
        
        # 提取备注
        for keyword, meaning in self.REMARK_KEYWORDS.items():
            if keyword in line:
                product['货物情况（多选）'] = meaning
                break
        
        # 验证：必须有价格
        if product['单价'] is None:
            print(f"  ⚠️  未找到价格：{line}")
            return None
        
        return product
    
    def _identify_brand(self, part_number: str) -> str:
        """根据料号识别品牌"""
        for brand, patterns in self.BRAND_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, part_number, re.IGNORECASE):
                    return brand
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
            output_file = f"香港现货_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = generator.create_excel(products, output_file)
        print(f"\n✅ Excel 已生成：{filepath}")
        
        return filepath
