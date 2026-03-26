#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三星 DDR5 内存条专用解析器
"""

import re
import sys
sys.path.insert(0, '/Users/mac/Desktop/自动发布机器人')

from advanced_parser import AdvancedOfferParser, build_empty_product


def parse_samsung_ddr5(line: str) -> dict:
    """解析三星 DDR5 内存条行"""
    # M321R8GA0PB0-CWMKJ 250PCS 原封整箱 2500U DC25+ 产地非 CN
    match = re.match(
        r'^([A-Z0-9\-]+)\s+(\d+)PCS\s*(?:\*(\d+)箱)?\s*(.+?)\s+(\d+)U\s*(?:DC)?(\d{2}\+)?\s*(?:产地 ([^\s]+))?',
        line.strip(),
        re.IGNORECASE
    )
    
    if not match:
        return None
    
    part_number = match.group(1)
    qty = int(match.group(2))
    boxes = int(match.group(3)) if match.group(3) else None
    desc = match.group(4)
    price = float(match.group(5))
    dc = match.group(6)
    location = match.group(7)
    
    product = build_empty_product()
    product['料号型号'] = part_number
    product['产品名称'] = f'Samsung DDR5 RDIMM {part_number}'
    product['品牌'] = 'Samsung'
    product['厂家'] = 'Samsung'
    product['单价'] = price
    product['数量'] = qty * boxes if boxes else qty
    product['单位'] = 'PCS'
    product['产品分类'] = 'RDIMM'
    if dc:
        product['批次（DC）'] = dc
    
    # 解析描述
    if '原封整箱' in desc or '原封整出' in desc:
        product['货物情况（多选）'] = '全新原箱'
    elif '原封尾箱' in desc:
        product['货物情况（多选）'] = '尾数'
    elif '含税' in desc:
        product['货物情况（多选）'] = '含税'
    else:
        product['货物情况（多选）'] = '全新'
    
    # 货源地映射
    if location:
        if '非 CN' in location or '非中国' in location:
            product['货所在地'] = '大陆'  # 非中国大陆
        elif 'CN' in location or '中国' in location:
            product['货所在地'] = '大陆'
        else:
            product['货所在地'] = '香港'
    else:
        product['货所在地'] = '香港'
    
    return product


# 测试
test_lines = [
    'M321R8GA0PB0-CWMKJ 250PCS 原封整箱 2500U DC25+ 产地非 CN',
    'M321R8GA0PB0-CWMKJ 221PCS 原封尾箱 2450U DC25+ 产地非 CN',
    'M321R8GA0EB2-CWMXH 250PCS*2 箱 原封整出 18800 含税 1 对 1 开票 DC25+ 产地 CN',
]

print('=' * 80)
print('📦 三星 DDR5 内存条解析测试')
print('=' * 80)
print()

for i, line in enumerate(test_lines, 1):
    product = parse_samsung_ddr5(line)
    if product:
        print(f"{i}. {product['料号型号']}")
        print(f"   单价：${product['单价']}")
        print(f"   数量：{product['数量']} PCS")
        print(f"   DC: {product['批次（DC）']}")
        print(f"   货物情况：{product['货物情况（多选）']}")
        print(f"   货源地：{product['货所在地']}")
        print()
