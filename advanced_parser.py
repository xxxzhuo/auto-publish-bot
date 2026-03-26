#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Offer Parser - 支持 10+ 种 OFFER 格式
"""

import re
from typing import Dict, List, Optional


def build_empty_product() -> Dict:
    """创建标准产品字典"""
    return {
        "企业名称": None,
        "货主": None,
        "性别": None,
        "手机号": None,
        "微信": None,
        "产品名称": None,
        "品牌": None,
        "料号型号": None,
        "单价": None,
        "货币单位（usd/cny）": "usd",
        "数量": None,
        "单位": "个",
        "货所在地": "香港",
        "批次（DC）": None,
        "货物情况（多选）": "全新",
        "产品分类": "存储芯片",
        "应用": None,
        "起订量": None,
        "有效期": None,
        "交货天数": 7,
        "厂家": None,
        "重量": None,
        "尺寸 - 长": None,
        "尺寸 - 宽": None,
        "尺寸 - 高": None,
        "替代品牌": None,
        "替代型号": None,
    }


class AdvancedOfferParser:
    """高级 OFFER 解析器 - 支持 10+ 种格式"""
    
    # 品牌映射
    BRAND_MAP = {
        # 中文品牌
        '三星': 'Samsung',
        '海力士': 'SK Hynix',
        'SK 海力士': 'SK Hynix',
        '美光': 'Micron',
        '镁光': 'Micron',
        '南亚': '南亚科技 (Nanya)',
        '铠侠': 'KIOXIA',
        '闪迪': 'SanDisk',
        '长鑫': 'CXMT',
        '佰维': 'Biwin',
        '江波龙': 'Longsys',
        '翊动': 'Yidong',
        '芯思维': 'XSM',
        # 英文品牌
        'SAMSUNG': 'Samsung',
        'SK HYNIX': 'SK Hynix',
        'SK Hynix': 'SK Hynix',
        'NANYA': '南亚科技 (Nanya)',
        'Nanya': '南亚科技 (Nanya)',
        'MICRON': 'Micron',
        'KIOXIA': 'KIOXIA',
        'SanDisk': 'SanDisk',
        'CXMT': 'CXMT',
    }
    
    # 料号前缀识别品牌
    PART_BRAND_PREFIX = {
        'K4': 'Samsung', 'K8': 'Samsung', 'KLM': 'Samsung', 'M32': 'Samsung', 'MZ': 'Samsung', 'THG': 'Samsung',
        'H5C': 'SK Hynix', 'H5AN': 'SK Hynix', 'H5HC': 'SK Hynix', 'H9C': 'SK Hynix', 'HMC': 'SK Hynix',
        'MT4': 'Micron', 'MT5': 'Micron', 'MT6': 'Micron', 'MT29': 'Micron', '25Q': 'Micron',
        'NT5': '南亚科技 (Nanya)', 'NT6': '南亚科技 (Nanya)',
        'THGBM': 'KIOXIA',
        'SDIN': 'SanDisk',
        'CXDB': 'CXMT',
        'FEMD': 'Longsys',
        'XSEM': 'XSM',
    }
    
    # 货源地映射
    LOCATION_MAP = {
        '香港': '香港', 'HK': '香港', 'HKG': '香港',
        '大陆': '大陆', 'CN': '大陆', 'CHINA': '大陆', '中国': '大陆',
        'VN': '越南', '越南': '越南',
        'KR': '韩国', '韩国': '韩国',
    }
    
    def __init__(self):
        self.current_company = None
        self.current_brand = None
        self.current_category = None
        self.default_location = '香港'
    
    def parse(self, text: str) -> List[Dict]:
        """解析 OFFER 文本"""
        products = []
        lines = text.strip().split('\n')
        
        # 检测文档类型和默认设置
        self._detect_document_type(lines)
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line or line.startswith('#'):
                i += 1
                continue
            
            # 检测公司名行
            if self._is_company_line(line):
                self.current_company = self._extract_company(line)
                i += 1
                continue
            
            # 检测品牌分类行
            if self._is_brand_category_line(line):
                brand, category = self._extract_brand_category(line)
                if brand:
                    self.current_brand = brand
                if category:
                    self.current_category = category
                i += 1
                continue
            
            # 尝试解析产品行
            product = self._parse_product_line(line, lines, i)
            if product:
                products.append(product)
            
            i += 1
        
        return products
    
    def _detect_document_type(self, lines: List[str]):
        """检测文档类型"""
        text = '\n'.join(lines[:10]).upper()
        
        if '香港现货' in text or 'HK STOCK' in text:
            self.default_location = '香港'
        elif '大陆' in text or 'CN ' in text:
            self.default_location = '大陆'
        else:
            self.default_location = '香港'
    
    def _is_company_line(self, line: str) -> bool:
        """是否为公司名行"""
        # 万佳电子 / 香港现货  实单来砍:
        if re.search(r'(电子 | 半导体 | 科技).*?(香港现货 | 实单)', line, re.IGNORECASE):
            return True
        return False
    
    def _extract_company(self, line: str) -> str:
        """提取公司名"""
        match = re.match(r'^([^\s]+电子|[^\s]+半导体)', line)
        if match:
            return match.group(1)
        return '香港现货供应商'
    
    def _is_brand_category_line(self, line: str) -> bool:
        """是否品牌分类行"""
        # 三星 DDR5 RDIMM / SAMSUNG DDR4 / SK Hynix DDR3
        if re.search(r'(三星 | 海力士 | 美光 | 南亚|SAMSUNG|SK HYNIX|NANYA|MICRON).*?(DDR|LPDDR|EMMC|NAND|SSD|RDIMM|UDIMM)', line, re.IGNORECASE):
            return True
        return False
    
    def _extract_brand_category(self, line: str) -> (Optional[str], Optional[str]):
        """提取品牌和分类"""
        brand = None
        category = None
        
        # 中文品牌
        if '三星' in line:
            brand = 'Samsung'
        elif '海力士' in line or 'SK ' in line.upper():
            brand = 'SK Hynix'
        elif '美光' in line or '镁光' in line:
            brand = 'Micron'
        elif '南亚' in line:
            brand = '南亚科技 (Nanya)'
        
        # 英文品牌
        if not brand:
            for en_brand, cn_brand in [('SAMSUNG', 'Samsung'), ('SK HYNIX', 'SK Hynix'), ('NANYA', '南亚科技 (Nanya)'), ('MICRON', 'Micron')]:
                if en_brand in line.upper():
                    brand = cn_brand
                    break
        
        # 分类
        if 'DDR5' in line.upper():
            category = 'DDR5'
        elif 'DDR4' in line.upper():
            category = 'DDR4'
        elif 'DDR3' in line.upper():
            category = 'DDR3'
        elif 'LPDDR5' in line.upper():
            category = 'LPDDR5'
        elif 'LPDDR4' in line.upper():
            category = 'LPDDR4'
        elif 'LPDDR3' in line.upper():
            category = 'LPDDR3'
        elif 'EMMC' in line.upper():
            category = 'EMMC'
        elif 'SSD' in line.upper():
            category = 'SSD'
        elif 'RDIMM' in line.upper():
            category = 'RDIMM'
        elif 'UDIMM' in line.upper():
            category = 'UDIMM'
        
        return brand, category
    
    def _parse_product_line(self, line: str, all_lines: List[str], current_idx: int) -> Optional[Dict]:
        """解析产品行"""
        product = None
        
        # 尝试各种格式
        # 格式 1: 万佳格式 - K3KL9L90QM-MFCT          25+  170U
        product = self._parse_wanjia_format(line)
        if product:
            return self._finalize_product(product)
        
        # 格式 2: 混合 OFFER - NT6AN256T32AV-J2 usd 19.5,  reel, dc21+
        product = self._parse_mixed_offer_format(line)
        if product:
            return self._finalize_product(product)
        
        # 格式 3: 三星 DDR5 - M321R8GA0PB0-CWMCJ    500PCS      $2780  DC25+
        product = self._parse_samsung_ddr5_format(line)
        if product:
            return self._finalize_product(product)
        
        # 格式 4: 品牌 + 容量描述 - 三星 LPDDR4 2GB (下一行料号)
        product = self._parse_brand_capacity_format(line, all_lines, current_idx)
        if product:
            return self._finalize_product(product)
        
        # 格式 5: 简单报价 - H5ANAG8NCJR-XNC      69      25+
        product = self._parse_simple_quote_format(line)
        if product:
            return self._finalize_product(product)
        
        # 格式 6: SSD - 480GB	MZ7L3480HCHQ-00A07	$440.00
        product = self._parse_ssd_format(line)
        if product:
            return self._finalize_product(product)
        
        # 格式 7: 内存条 - DDR5 64G 5600（500PCS）
        product = self._parse_memory_module_format(line, all_lines, current_idx)
        if product:
            return self._finalize_product(product)
        
        # 格式 8: 带产地 - M321R8GA0PB0-CWMXH，产地中国，25+
        product = self._parse_location_format(line)
        if product:
            return self._finalize_product(product)
        
        # 格式 9: 数量 + 价格 - K4B4G1646E-BCNB000   67200  24+/25+  4.9U
        product = self._parse_qty_price_format(line)
        if product:
            return self._finalize_product(product)
        
        # 格式 10: 标准 HK OFFER - 256*16 K4A4G165WF-BCTD $6.25
        product = self._parse_standard_format(line)
        if product:
            return self._finalize_product(product)
        
        # 格式 11: 通用回退 - 尽可能解析任何包含料号和价格的行
        product = self._parse_generic_offer_format(line)
        if product:
            return self._finalize_product(product)
        
        return None
    
    def _parse_wanjia_format(self, line: str) -> Optional[Dict]:
        """万佳格式：料号  DC+  价格 U"""
        # K3KL9L90QM-MFCT          25+  170U
        match = re.match(r'^([A-Z0-9\-]+)\s+(\d{2}\+)\s+([\d.]+)U\s*$', line, re.IGNORECASE)
        if match:
            part_number = match.group(1)
            dc = match.group(2)
            price = float(match.group(3))
            
            product = build_empty_product()
            product['料号型号'] = part_number
            product['产品名称'] = part_number
            product['品牌'] = self._identify_brand(part_number)
            product['厂家'] = product['品牌']
            product['单价'] = price
            product['批次（DC）'] = dc
            product['货所在地'] = '香港'
            return product
        return None
    
    def _parse_mixed_offer_format(self, line: str) -> Optional[Dict]:
        """混合 OFFER 格式：料号 usd 价格，[描述], dcXX+"""
        # NT6AN256T32AV-J2 usd 19.5,  reel, dc21+ , 1week
        match = re.match(r'^([A-Z0-9\-]+)\s+usd\s+([\d.]+),?\s*(.+?)$', line, re.IGNORECASE)
        if match:
            part_number = match.group(1)
            price = float(match.group(2))
            desc = match.group(3).lower()
            
            product = build_empty_product()
            product['料号型号'] = part_number
            product['产品名称'] = part_number
            product['品牌'] = self._identify_brand(part_number)
            product['厂家'] = product['品牌']
            product['单价'] = price
            
            # 解析描述
            if 'reel' in desc:
                product['货物情况（多选）'] = 'Reel'
            if 'dc' in desc:
                dc_match = re.search(r'dc\s*(\d{2}\+)', desc, re.IGNORECASE)
                if dc_match:
                    product['批次（DC）'] = dc_match.group(1)
            
            product['货所在地'] = '香港'
            return product
        return None
    
    def _parse_samsung_ddr5_format(self, line: str) -> Optional[Dict]:
        """三星 DDR5 格式：料号  数量 PCS  价格  DC"""
        # M321R8GA0PB0-CWMCJ    500PCS      $2780  DC25+
        match = re.match(r'^([A-Z0-9\-]+)\s+(\d+)PCS\s+\$?([\d,]+)\s*(?:DC)?(\d{2}\+)?', line, re.IGNORECASE)
        if match:
            part_number = match.group(1)
            qty = int(match.group(2))
            price_str = match.group(3).replace(',', '')
            price = float(price_str)
            dc = match.group(4) if match.group(4) else None
            
            product = build_empty_product()
            product['料号型号'] = part_number
            product['产品名称'] = f'Samsung DDR5 RDIMM {part_number}'
            product['品牌'] = 'Samsung'
            product['厂家'] = 'Samsung'
            product['单价'] = price
            product['数量'] = qty
            product['单位'] = 'PCS'
            product['产品分类'] = 'RDIMM'
            if dc:
                product['批次（DC）'] = dc
            product['货所在地'] = '香港'
            return product
        return None
    
    def _parse_brand_capacity_format(self, line: str, all_lines: List[str], current_idx: int) -> Optional[Dict]:
        """品牌 + 容量格式：三星 LPDDR4 2GB (下一行料号)"""
        # 检查是否是标题行
        match = re.match(r'^(三星 | 海力士 | 美光 | 南亚|SK Hynix)\s*(LPDDR\d+|DDR\d+|EMMC)\s*(\d+GB|\d+G)?', line, re.IGNORECASE)
        if match:
            # 下一行是料号
            if current_idx + 1 < len(all_lines):
                next_line = all_lines[current_idx + 1].strip()
                # 再下一行是价格等信息
                if current_idx + 2 < len(all_lines):
                    info_line = all_lines[current_idx + 2].strip()
                    
                    part_number = next_line
                    # 解析信息行：23+，80k，37.5 美金，香港
                    info_match = re.match(r'(\d{2}\+)\s*,?\s*(\d+[kK]?)\s*,?\s*([\d.]+)\s*(?:美金 | 美元|U|USD)?\s*,?\s*(香港 | 大陆 |HK|CN)?', info_line)
                    if info_match:
                        dc = info_match.group(1)
                        qty_str = info_match.group(2).lower().replace('k', '000')
                        qty = int(qty_str) if qty_str.isdigit() else None
                        price = float(info_match.group(3))
                        location = info_match.group(4) if info_match.group(4) else '香港'
                        
                        product = build_empty_product()
                        product['料号型号'] = part_number
                        product['产品名称'] = part_number
                        product['品牌'] = self._identify_brand(part_number)
                        product['厂家'] = product['品牌']
                        product['单价'] = price
                        product['数量'] = qty
                        product['批次（DC）'] = dc
                        product['货所在地'] = self._map_location(location)
                        return product
        return None
    
    def _parse_simple_quote_format(self, line: str) -> Optional[Dict]:
        """简单报价格式：料号  DC+  描述  价格 或 料号  价格  DC+"""
        # 格式 1: K4B4G1646E-BYMA 24+ 整箱 4.0
        # 格式 2: K4A8G165WG-BCWE 25+ PARTIAL 28
        # 格式 3: H5ANAG8NCJR-XNC      69      25+
        
        # 先尝试格式 1/2: 料号 DC+ 描述 价格
        match1 = re.match(r'^([A-Z0-9\-]+)\s+(\d{2}\+)\s+(\w+|PARTIAL|FULL|REEL|BID)\s+([\d.]+)(?:U|USD)?\s*$', line, re.IGNORECASE)
        if match1:
            part_number = match1.group(1)
            dc = match1.group(2)
            desc = match1.group(3).upper()
            price = float(match1.group(4))
            
            product = build_empty_product()
            product['料号型号'] = part_number
            product['产品名称'] = part_number
            product['品牌'] = self._identify_brand(part_number)
            product['厂家'] = product['品牌']
            product['单价'] = price
            product['批次（DC）'] = dc
            
            # 解析描述
            if desc == 'PARTIAL':
                product['货物情况（多选）'] = '部分'
            elif desc == 'FULL':
                product['货物情况（多选）'] = '全新'
            elif '整箱' in desc or 'FULL' in desc:
                product['货物情况（多选）'] = '全新原箱'
            else:
                product['货物情况（多选）'] = '全新'
            
            product['货所在地'] = '香港'
            return product
        
        # 尝试格式 3: 料号 价格 DC+
        match2 = re.match(r'^([A-Z0-9\-]+)\s+([\d.]+)\s+(\d{2}\+)', line)
        if match2:
            part_number = match2.group(1)
            price = float(match2.group(2))
            dc = match2.group(3)
            
            product = build_empty_product()
            product['料号型号'] = part_number
            product['产品名称'] = part_number
            product['品牌'] = self._identify_brand(part_number)
            product['厂家'] = product['品牌']
            product['单价'] = price
            product['批次（DC）'] = dc
            product['货所在地'] = '香港'
            return product
        
        return None
    
    def _parse_generic_offer_format(self, line: str) -> Optional[Dict]:
        """通用 OFFER 格式：尽可能解析任何包含料号和价格的行"""
        # 匹配料号前缀 (至少 1 个大写字母 + 数字 + 更多字母数字)
        part_match = re.match(r'^([A-Z]\d*[A-Z][A-Z0-9\-:]+)', line)
        if not part_match:
            return None
        
        part_number = part_match.group(1)
        product = build_empty_product()
        product['料号型号'] = part_number
        product['产品名称'] = part_number
        product['品牌'] = self._identify_brand(part_number)
        product['厂家'] = product['品牌']
        product['货所在地'] = '香港'
        
        # 尝试提取价格 - 优先匹配 usd 后面的数字
        price = None
        # 格式 1: usd2420.0 或 usd 2420.0
        usd_match = re.search(r'usd\s*([\d.]+)', line, re.IGNORECASE)
        if usd_match:
            try:
                price = float(usd_match.group(1))
            except Exception:
                pass
        
        # 格式 2: XX.X*XK 格式 (如 92.0*2k, 44.0*6K) - 价格是乘号前面的数字
        if price is None:
            price_qty_match = re.search(r'(\d+(?:\.\d+)?)\s*\*\s*(\d+[kK]?)', line)
            if price_qty_match:
                try:
                    price = float(price_qty_match.group(1))
                    # 同时提取数量
                    qty_str = price_qty_match.group(2).lower()
                    multiplier = 1000 if 'k' in qty_str else 1
                    product['数量'] = int(multiplier)
                except Exception:
                    pass
        
        # 格式 3: 单独的数字 (排除 DC 和数量)
        if price is None:
            # 查找所有数字，排除 DC (XX+) 和数量 (*XK)
            numbers = re.findall(r'(?<!\d)(\d+(?:\.\d+)?)(?!\d)', line)
            for num_str in numbers:
                # 跳过 DC 格式 (25+)
                if re.search(rf'{num_str}\s*\+', line):
                    continue
                # 跳过纯数量格式 (250pcs)
                if re.search(rf'{num_str}\s*pcs', line, re.IGNORECASE):
                    continue
                try:
                    num = float(num_str)
                    # 价格通常在 0.1-10000 之间
                    if 0.1 <= num <= 10000:
                        price = num
                        break
                except Exception:
                    pass
        
        if price is not None:
            product['单价'] = price
        
        # 尝试提取 DC
        dc_match = re.search(r'(?:dc\s*)?(\d{2}\+)', line, re.IGNORECASE)
        if dc_match:
            product['批次（DC）'] = dc_match.group(1)
        
        # 尝试提取数量 (如 *2k, *6K, *10K, 250pcs)
        qty_match = re.search(r'(\d+(?:\.\d+)?)\s*\*\s*(\d+[kK]?)', line)
        if qty_match:
            try:
                qty_str = qty_match.group(2).lower()
                multiplier = 1000 if 'k' in qty_str else 1
                product['数量'] = int(float(qty_match.group(1)) * multiplier)
            except Exception:
                pass
        
        # 尝试提取货源地 (non cn, CN, VN 等)
        if re.search(r'non\s*cn|non-cn|非 cn|非中国', line, re.IGNORECASE):
            product['货所在地'] = '非 CN'
        elif re.search(r'\bCN\b|,CN|，CN', line, re.IGNORECASE):
            product['货所在地'] = '大陆'
        elif re.search(r'\bVN\b|,VN|，VN', line, re.IGNORECASE):
            product['货所在地'] = '越南'
        
        # 只有当解析到价格时才返回产品
        if product['单价'] is not None and product['单价'] > 0:
            return product
        
        return None
    
    def _parse_ssd_format(self, line: str) -> Optional[Dict]:
        """SSD 格式：容量  料号  价格"""
        # 480GB	MZ7L3480HCHQ-00A07	$440.00
        match = re.match(r'^(\d+(?:\.\d+)?(?:GB|TB))\s+([A-Z0-9\-]+)\s+\$?([\d,]+)', line, re.IGNORECASE)
        if match:
            capacity = match.group(1).upper()
            part_number = match.group(2)
            price_str = match.group(3).replace(',', '')
            price = float(price_str)
            
            product = build_empty_product()
            product['料号型号'] = part_number
            product['产品名称'] = f'Samsung SSD {capacity} {part_number}'
            product['品牌'] = 'Samsung'
            product['厂家'] = 'Samsung'
            product['单价'] = price
            product['产品分类'] = 'SSD'
            product['货所在地'] = '香港'
            return product
        return None
    
    def _parse_memory_module_format(self, line: str, all_lines: List[str], current_idx: int) -> Optional[Dict]:
        """内存条格式：DDR5 64G 5600（500PCS）或 三星内存条 DDR5 64G 5600"""
        # 检测标题行：三星内存条 DDR5 64G 5600
        title_match = re.match(r'^(三星 | 海力士 |SK)?\s*(?:内存条)?\s*(DDR\d+)\s+(\d+G)\s*(\d+)?\s*(?:（(\d+)PCS）)?', line, re.IGNORECASE)
        if title_match:
            brand_name = title_match.group(1)
            category = title_match.group(2).upper()
            capacity = title_match.group(3)
            
            # 解析后续产品行
            products = []
            for i in range(current_idx + 1, min(current_idx + 5, len(all_lines))):
                prod_line = all_lines[i].strip()
                if not prod_line or not re.match(r'^[A-Z]', prod_line):
                    break
                
                # M321R8GA0PB0-CWMKJ 250PCS 原封整箱 2500U DC25+ 产地非 CN
                # 格式：料号 数量 PCS 描述 价格 U DC 产地
                prod_match = re.match(
                    r'^([A-Z0-9\-]+)\s+(\d+)PCS\s*(?:\*(\d+)箱)?\s*(.+?)\s+(\d+)U\s*(?:DC)?(\d{2}\+)?\s*(?:产地 ([^,\s]+))?',
                    prod_line,
                    re.IGNORECASE
                )
                
                if prod_match:
                    part_number = prod_match.group(1)
                    qty = int(prod_match.group(2))
                    boxes = int(prod_match.group(3)) if prod_match.group(3) else None
                    desc = prod_match.group(4)
                    price = float(prod_match.group(5))
                    dc = prod_match.group(6)
                    location = prod_match.group(7)
                    
                    product = build_empty_product()
                    product['料号型号'] = part_number
                    product['产品名称'] = f'{brand_name or "Samsung"} {category} {capacity} {part_number}'
                    product['品牌'] = self._identify_brand(part_number)
                    product['厂家'] = product['品牌']
                    product['单价'] = price
                    product['数量'] = qty * boxes if boxes else qty
                    product['单位'] = 'PCS'
                    product['产品分类'] = category
                    if dc:
                        product['批次（DC）'] = dc
                    
                    # 解析描述
                    if '原封整箱' in desc or '原封整出' in desc:
                        product['货物情况（多选）'] = '全新原箱'
                    elif '原封尾箱' in desc:
                        product['货物情况（多选）'] = '尾数'
                    elif '原封' in desc:
                        product['货物情况（多选）'] = '全新'
                    
                    # 货源地
                    if location:
                        product['货所在地'] = self._map_location(location)
                    else:
                        product['货所在地'] = '香港'
                    
                    products.append(product)
            
            return products[0] if products else None
        return None
    
    def _parse_location_format(self, line: str) -> Optional[Dict]:
        """带产地格式：料号，产地中国，25+"""
        # M321R8GA0PB0-CWMXH，产地中国，25+，原封箱，250pcs，2450 美金
        match = re.match(r'^([A-Z0-9\-]+)\s*,?\s*产地 ([^,]+)\s*,?\s*(\d{2}\+)\s*,?\s*([^,]+)\s*,?\s*(\d+)PCS?\s*,?\s*([\d.]+)\s*(?:美金 | 美元|USD|U)?', line, re.IGNORECASE)
        if match:
            part_number = match.group(1)
            location_text = match.group(2)
            dc = match.group(3)
            package = match.group(4)
            qty = int(match.group(5))
            price = float(match.group(6))
            
            product = build_empty_product()
            product['料号型号'] = part_number
            product['产品名称'] = part_number
            product['品牌'] = self._identify_brand(part_number)
            product['厂家'] = product['品牌']
            product['单价'] = price
            product['数量'] = qty
            product['批次（DC）'] = dc
            product['货所在地'] = self._map_location(location_text)
            
            # 包装
            if '原封' in package or '原箱' in package:
                product['货物情况（多选）'] = '全新原箱'
            elif '开箱' in package or '拆箱' in package:
                product['货物情况（多选）'] = '开箱'
            
            return product
        return None
    
    def _parse_qty_price_format(self, line: str) -> Optional[Dict]:
        """数量 + 价格格式：料号  数量  DC+  价格 U"""
        # K4B4G1646E-BCNB000   67200  24+/25+  4.9U
        match = re.match(r'^([A-Z0-9\-]+)\s+(\d+)\s+(\d{2}\+(?:/\d{2}\+)?)\s+([\d.]+)U\s*$', line, re.IGNORECASE)
        if match:
            part_number = match.group(1)
            qty = int(match.group(2))
            dc = match.group(3)
            price = float(match.group(4))
            
            product = build_empty_product()
            product['料号型号'] = part_number
            product['产品名称'] = part_number
            product['品牌'] = self._identify_brand(part_number)
            product['厂家'] = product['品牌']
            product['单价'] = price
            product['数量'] = qty
            product['批次（DC）'] = dc.split('/')[0]  # 取第一个 DC
            product['货所在地'] = '香港'
            return product
        return None
    
    def _parse_standard_format(self, line: str) -> Optional[Dict]:
        """标准 HK OFFER 格式：256*16 K4A4G165WF-BCTD $6.25"""
        match = re.match(r'^(?:(\d+)\*(\d+)\s+)?([A-Z0-9\-]+)\s+\$?([\d.]+|BID)\s*(?:DC)?(\d{2}\+)?', line, re.IGNORECASE)
        if match:
            spec_width = match.group(1)
            spec_depth = match.group(2)
            part_number = match.group(3)
            price_str = match.group(4)
            dc = match.group(5)
            
            if price_str.upper() == 'BID':
                price = 0.01
            else:
                price = float(price_str)
            
            product = build_empty_product()
            product['料号型号'] = part_number
            product['产品名称'] = part_number
            product['品牌'] = self._identify_brand(part_number)
            product['厂家'] = product['品牌']
            product['单价'] = price
            if dc:
                product['批次（DC）'] = dc
            if spec_width and spec_depth:
                product['数量'] = int(spec_width)
                product['单位'] = f'{spec_depth}bit'
            product['货所在地'] = '香港'
            return product
        return None
    
    def _identify_brand(self, part_number: str) -> str:
        """根据料号识别品牌"""
        part_upper = part_number.upper()
        for prefix, brand in self.PART_BRAND_PREFIX.items():
            if part_upper.startswith(prefix):
                return brand
        return '未知品牌'
    
    def _map_location(self, location_text: str) -> str:
        """映射货源地"""
        text_upper = location_text.upper()
        
        # 非中国
        if 'NON CN' in text_upper or '非中国' in text_upper or '非 CN' in text_upper:
            return '大陆'  # 非中国大陆
        
        # 越南
        if 'VN' in text_upper or '越南' in text_upper:
            return '越南'
        
        # 韩国
        if 'KR' in text_upper or '韩国' in text_upper:
            return '韩国'
        
        # 标准映射
        for key, value in self.LOCATION_MAP.items():
            if key.upper() in text_upper or key in text_upper:
                return value
        
        return '香港'  # 默认
    
    def _finalize_product(self, product: Dict) -> Dict:
        """完成产品设置"""
        if not product.get('企业名称'):
            product['企业名称'] = '香港现货供应商'
        if not product.get('货主'):
            product['货主'] = '系统导入'
        if not product.get('性别'):
            product['性别'] = '先生'
        if not product.get('微信'):
            product['微信'] = '待补充'
        if not product.get('手机号'):
            product['手机号'] = '待补充'
        if product.get('单价') is None:
            product['单价'] = 0.01
        if not product.get('产品名称'):
            product['产品名称'] = product.get('料号型号', '')
        return product


# 测试
if __name__ == '__main__':
    test_text = """
万佳电子 
香港现货  实单来砍:
K3KL9L90QM-MFCT          25+  170U
K4F6E3S4HB-KHCL            25+   50U

OFFER:
NT6AN256T32AV-J2 usd 19.5,  reel, dc21+ , 1week 
H5CG48MEBDX014N  usd 31.0，dc 25+ 

H5ANAG8NCJR-XNC      69      25+
H5CG48MEBDX014N     30.0   25+

480GB	MZ7L3480HCHQ-00A07	$440.00
"""
    
    parser = AdvancedOfferParser()
    products = parser.parse(test_text)
    
    print(f'解析到 {len(products)} 个产品')
    for i, p in enumerate(products[:5], 1):
        print(f"{i}. {p['料号型号']:30} | {p['品牌']:20} | ${p['单价']:8} | {p['货所在地']}")
