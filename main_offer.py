#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发布机器人 - OFFER 解析主程序
版本：v1.0
日期：2026-03-13

功能：解析 OFFER 文本 → 生成标准 Excel
"""

import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, '/Users/mac/Desktop/自动发布机器人')

from offer_parser import OfferParser
from excel_generator import ExcelGenerator


def main():
    """主函数"""
    print("=" * 60)
    print("🤖 自动发布机器人 - OFFER 解析版")
    print("=" * 60)
    print(f"⏰ 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ========== 步骤 1: 解析 OFFER ==========
    print("【步骤 1/2】解析 OFFER 文本")
    print("-" * 60)
    
    offer_parser = OfferParser()
    
    # 从文件读取 OFFER
    offer_file = '/Users/mac/Desktop/自动发布机器人/products/offer_20260313.txt'
    
    if os.path.exists(offer_file):
        products = offer_parser.parse_offer_file(offer_file)
    else:
        print(f"❌ 文件不存在：{offer_file}")
        return False
    
    if not products:
        print("❌ 没有解析到任何产品")
        return False
    
    print(f"\n✅ 成功解析 {len(products)} 个产品")
    print()
    
    # ========== 步骤 2: 生成 Excel ==========
    print("【步骤 2/2】生成 Excel 表格")
    print("-" * 60)
    
    generator = ExcelGenerator()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"鸿达_OFFER_{timestamp}.xlsx"
    
    filepath = generator.create_excel(products, filename)
    
    if not filepath:
        print("❌ Excel 生成失败")
        return False
    
    print()
    print("=" * 60)
    print("✅ OFFER 处理完成！")
    print("=" * 60)
    print(f"📊 产品数量：{len(products)}")
    print(f"📄 Excel 文件：{filepath}")
    print()
    
    # 统计信息
    brands = {}
    total_value = 0
    
    for p in products:
        brand = p.get('品牌', '未知')
        brands[brand] = brands.get(brand, 0) + 1
        
        if p.get('单价') and p.get('数量'):
            total_value += p['单价'] * p['数量']
    
    print("📈 品牌统计:")
    for brand, count in sorted(brands.items(), key=lambda x: -x[1]):
        print(f"   {brand}: {count} 个")
    
    if total_value > 0:
        print(f"\n💰 总金额：USD {total_value:,.2f}")
    
    print()
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
