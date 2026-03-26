#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Publish-Bot Skill - 高级解析器版本
支持 10+ 种 OFFER 格式
"""

import sys
import os
from datetime import datetime

# 项目路径
PROJECT_DIR = "/Users/mac/Desktop/自动发布机器人"
sys.path.insert(0, PROJECT_DIR)

from advanced_parser import AdvancedOfferParser
from all_in_one import ExcelGenerator, LoginManager, Uploader


def parse_and_publish(offer_text: str, parse_only: bool = False):
    """解析并发布 OFFER"""
    print("=" * 80)
    print("🚀 自动发布机器人 - 高级解析器")
    print("=" * 80)
    print()
    
    # 步骤 1: 解析
    print("【步骤 1/4】解析 OFFER 文本")
    print("-" * 80)
    parser = AdvancedOfferParser()
    products = parser.parse(offer_text)
    
    if not products:
        print("❌ 未解析到任何产品")
        return False
    
    print(f"✅ 解析成功：{len(products)} 个产品")
    print()
    
    # 步骤 2: 补全信息
    print("【步骤 2/4】补全产品信息")
    print("-" * 80)
    for p in products:
        if not p.get('企业名称'):
            p['企业名称'] = '香港现货供应商'
        if not p.get('货主'):
            p['货主'] = '系统导入'
        if not p.get('性别'):
            p['性别'] = '先生'
        if not p.get('微信'):
            p['微信'] = '待补充'
        if not p.get('手机号'):
            p['手机号'] = '待补充'
        if p.get('单价') is None or p.get('单价') == 0:
            p['单价'] = 0.01
    print("✅ 信息补全完成")
    print()
    
    # 步骤 3: 生成 Excel
    print("【步骤 3/4】生成 Excel")
    print("-" * 80)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    generator = ExcelGenerator()
    filepath = generator.create_excel(products, f"OFFER_Advanced_{timestamp}.xlsx")
    print(f"✅ Excel 已生成：{filepath}")
    print()
    
    if parse_only:
        print("⏭️  跳过上传（仅解析模式）")
        print()
        print("=" * 80)
        print("✅ 解析完成")
        print("=" * 80)
        return True
    
    # 步骤 4: 上传
    print("【步骤 4/4】登录并上传")
    print("-" * 80)
    
    login_mgr = LoginManager()
    success = login_mgr.login('13798441628', '2222')
    
    if not success:
        print("❌ 登录失败")
        return False
    
    print(f"✅ 登录成功：{login_mgr.user_info.get('nickname')}")
    print()
    
    print("⬆️  上传 Excel...")
    uploader = Uploader(session=login_mgr.get_session(), headers=login_mgr.get_headers())
    upload_success = uploader.upload_excel(filepath)
    
    if not upload_success:
        print(f"❌ 上传失败：{uploader.last_error}")
        return False
    
    print("✅ 上传成功")
    print()
    print("=" * 80)
    print("🎉 发布完成！")
    print("=" * 80)
    print(f"📊 发布产品数：{len(products)}")
    print(f"📄 Excel 文件：{filepath}")
    print()
    
    # 统计
    brand_count = {}
    location_count = {}
    for p in products:
        brand = p.get('品牌', '未知')
        location = p.get('货所在地', '未知')
        brand_count[brand] = brand_count.get(brand, 0) + 1
        location_count[location] = location_count.get(location, 0) + 1
    
    print("📈 品牌分布:")
    for brand, count in sorted(brand_count.items(), key=lambda x: -x[1]):
        print(f"  {brand}: {count} 个")
    print()
    
    print("📍 货源地分布:")
    for loc, count in sorted(location_count.items(), key=lambda x: -x[1]):
        print(f"  {loc}: {count} 个")
    print()
    
    return True


def main():
    if len(sys.argv) < 2:
        print("用法：python3 publish_advanced.py <offer 文件路径>")
        print("   或：python3 publish_advanced.py --parse-only <offer 文件路径>")
        sys.exit(1)
    
    parse_only = False
    file_path = sys.argv[1]
    
    if file_path == '--parse-only':
        parse_only = True
        if len(sys.argv) < 3:
            print("❌ 缺少文件路径")
            sys.exit(1)
        file_path = sys.argv[2]
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在：{file_path}")
        sys.exit(1)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        offer_text = f.read()
    
    success = parse_and_publish(offer_text, parse_only=parse_only)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
