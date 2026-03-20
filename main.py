#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发布机器人 - 主程序
版本：v1.0
日期：2026-03-13

功能流程：
1. 登录（可选） → 2. 解析产品 txt → 3. 生成 Excel → 4. 上传发布（可选）
"""

import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, '/Users/mac/Desktop/自动发布机器人')

from config import PHONE_NUMBER, PASSWORD, RUN_MODE, BASE_URL, LOGIN_API
from parser import ProductParser
from excel_generator import ExcelGenerator


def main():
    """主函数"""
    print("=" * 60)
    print("🤖 自动发布机器人 v1.0")
    print("=" * 60)
    print(f"⏰ 启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 运行模式：{RUN_MODE}")
    print()
    
    # ========== 步骤 1: 登录（仅 REAL 模式）==========
    if RUN_MODE == "REAL":
        print("【步骤 1/4】登录系统")
        print("-" * 60)
        
        from login import LoginManager
        
        login_mgr = LoginManager()
        
        if not PHONE_NUMBER or not PASSWORD:
            print("❌ 错误：请在 config.py 中配置手机号和密码")
            return False
        
        if not BASE_URL or not LOGIN_API:
            print("❌ 错误：请在 config.py 中配置 BASE_URL 和 LOGIN_API")
            return False
        
        if not login_mgr.login():
            print("❌ 登录失败，程序终止")
            return False
        
        print()
    else:
        print("【步骤 1/4】跳过登录（模拟模式）")
        print("-" * 60)
        print("ℹ️  提示：修改 config.py 中 RUN_MODE=\"REAL\" 启用真实上传")
        print()
    
    # ========== 步骤 2: 解析产品文件 ==========
    print("【步骤 2/4】解析产品信息")
    print("-" * 60)
    
    parser = ProductParser()
    products = parser.parse_directory()
    
    if not products:
        print("❌ 没有解析到任何产品，程序终止")
        return False
    
    # 验证必填字段
    print("\n【验证必填字段】")
    required_fields = ['企业名称', '产品名称', '料号型号']
    valid_products = []
    
    for i, product in enumerate(products, 1):
        missing = [f for f in required_fields if not product.get(f)]
        
        if missing:
            print(f"⚠️  产品{i}: 缺少字段 {missing}，已跳过")
        else:
            valid_products.append(product)
            print(f"✅ 产品{i}: {product.get('产品名称')} - 验证通过")
    
    if not valid_products:
        print("❌ 没有有效产品，程序终止")
        return False
    
    products = valid_products
    print()
    
    # ========== 步骤 3: 生成 Excel 表格 ==========
    print("【步骤 3/4】生成 Excel 表格")
    print("-" * 60)
    
    generator = ExcelGenerator()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"供需信息_{timestamp}.xlsx"
    
    filepath = generator.create_excel(products, filename)
    
    if not filepath:
        print("❌ Excel 生成失败，程序终止")
        return False
    
    print()
    
    # ========== 步骤 4: 上传发布（仅 REAL 模式）==========
    if RUN_MODE == "REAL":
        print("【步骤 4/4】上传发布")
        print("-" * 60)
        
        from uploader import Uploader
        
        uploader = Uploader(
            session=login_mgr.get_session(),
            headers=login_mgr.get_headers()
        )
        
        if not uploader.upload_excel(filepath):
            print("⚠️  上传失败，但 Excel 文件已保存在本地")
            print(f"   文件路径：{filepath}")
            return False
        
        print()
        print("=" * 60)
        print("✅ 发布完成！")
        print("=" * 60)
    else:
        print("【步骤 4/4】跳过上传（模拟模式）")
        print("-" * 60)
        print("✅ Excel 文件已生成，可手动上传或测试后启用 REAL 模式")
        print()
        print("=" * 60)
        print("✅ 模拟运行完成！")
        print("=" * 60)
    
    print(f"📊 成功处理产品数：{len(products)}")
    print(f"📄 Excel 文件：{filepath}")
    print()
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
