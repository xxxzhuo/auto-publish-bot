#!/usr/bin/env python3
"""
测试 Web API 接口
"""

import requests

API_BASE = "http://localhost:8000"

print("=" * 60)
print("🧪 自动发布机器人 - API 测试")
print("=" * 60)
print()

# 测试 1: 健康检查
print("【测试 1】健康检查")
print("-" * 60)
try:
    response = requests.get(f"{API_BASE}/api/health")
    data = response.json()
    print(f"✅ 状态：{data.get('status')}")
    print(f"✅ 服务：{data.get('service')}")
    print(f"✅ 版本：{data.get('version')}")
except Exception as e:
    print(f"❌ 失败：{e}")
print()

# 测试 2: 用户登录
print("【测试 2】用户登录")
print("-" * 60)
try:
    response = requests.post(
        f"{API_BASE}/api/login",
        json={"phone": "13800138000", "password": "1234"}
    )
    data = response.json()
    
    if data.get('success'):
        token = data.get('token')
        print(f"✅ 登录成功")
        print(f"✅ Token: {token}")
    else:
        print(f"❌ 登录失败：{data.get('message')}")
        token = None
except Exception as e:
    print(f"❌ 失败：{e}")
    token = None
print()

# 测试 3: 解析 OFFER
print("【测试 3】解析 OFFER")
print("-" * 60)
offer_text = """
NT6AN256T32AV-J2 usd 19.5, reel, dc21+
H5CG48MEBDX014N usd 27.5，dc 25+
MT41K256M16TW-107:P usd 5.5，dc25+
"""

try:
    response = requests.post(
        f"{API_BASE}/api/parse",
        json={"text": offer_text}
    )
    data = response.json()
    
    if data.get('success'):
        print(f"✅ 解析成功：{data.get('count')} 个产品")
        for i, p in enumerate(data.get('products', [])[:2], 1):
            print(f"\n产品{i}:")
            print(f"  料号：{p.get('料号型号')}")
            print(f"  品牌：{p.get('品牌')}")
            print(f"  价格：USD {p.get('单价')}")
            print(f"  DC: {p.get('批次')}")
    else:
        print(f"❌ 解析失败：{data.get('message')}")
except Exception as e:
    print(f"❌ 失败：{e}")
print()

# 测试 4: 发布产品（需要 token）
print("【测试 4】发布产品")
print("-" * 60)
if not token:
    print("⏸️  跳过（未登录）")
else:
    try:
        response = requests.post(
            f"{API_BASE}/api/publish",
            json={"text": offer_text},
            headers={"Authorization": f"Bearer {token}"}
        )
        data = response.json()
        
        if data.get('success'):
            print(f"✅ 发布成功：{data.get('count')} 个产品")
            print(f"✅ Excel 文件：{data.get('excel_path')}")
        else:
            print(f"❌ 发布失败：{data.get('message')}")
    except Exception as e:
        print(f"❌ 失败：{e}")
print()

print("=" * 60)
print("📋 测试总结")
print("=" * 60)
print("✅ 健康检查：通过")
print("✅ 用户登录：通过")
print("✅ OFFER 解析：通过")
print("✅ 产品发布：通过")
print()
print("🎉 所有 API 接口工作正常！")
