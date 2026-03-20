#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发布机器人 - 上传模块（真实接口版）
版本：v2.0
日期：2026-03-13
"""

import requests
import os
from typing import Optional, Dict
import sys
sys.path.append('/Users/mac/Desktop/自动发布机器人')
from config import BASE_URL, UPLOAD_API, TIMEOUT, RETRY_COUNT


class Uploader:
    """文件上传器（真实接口）"""
    
    def __init__(self, session: requests.Session = None, headers: Dict = None):
        """
        初始化上传器
        
        Args:
            session: requests 会话对象（包含登录态）
            headers: 请求头
        """
        self.session = session or requests.Session()
        self.headers = headers or {}
    
    def upload_excel(self, filepath: str) -> bool:
        """
        上传 Excel 文件（调用真实 API）
        
        Args:
            filepath: Excel 文件路径
            
        Returns:
            上传是否成功
        """
        if not os.path.exists(filepath):
            print(f"❌ 文件不存在：{filepath}")
            return False
        
        url = f"{BASE_URL}{UPLOAD_API}"
        
        print(f"🔄 正在上传：{os.path.basename(filepath)}")
        print(f"📡 请求 URL: {url}")
        print(f"📄 文件大小：{os.path.getsize(filepath)} bytes")
        
        for attempt in range(1, RETRY_COUNT + 1):
            try:
                # 准备文件（multipart/form-data）
                with open(filepath, 'rb') as f:
                    files = {
                        'file': (os.path.basename(filepath), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    }
                    
                    # 使用上传专用 headers（不需要 Content-Type，requests 会自动设置）
                    upload_headers = {k: v for k, v in self.headers.items() if k != 'Content-Type'}
                    
                    print(f"📤 发送上传请求...")
                    
                    response = self.session.post(
                        url,
                        files=files,
                        headers=upload_headers,
                        timeout=TIMEOUT * 2  # 上传需要更长时间
                    )
                    
                    print(f"📊 响应状态码：{response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 检查返回码
                    if result.get('code') == 200:
                        print("✅ 上传成功！")
                        print(f"📝 响应：{result.get('msg', '操作成功')}")
                        return True
                    else:
                        print(f"❌ 上传失败：{result.get('msg', '未知错误')}")
                        return False
                else:
                    print(f"⚠️ HTTP {response.status_code}，重试 {attempt}/{RETRY_COUNT}")
                    print(f"响应内容：{response.text[:200]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"⚠️ 请求异常：{e}，重试 {attempt}/{RETRY_COUNT}")
        
        print("❌ 上传失败：超过最大重试次数")
        return False
    
    def upload_with_data(self, filepath: str, extra_data: Dict = None) -> bool:
        """
        上传文件并附带额外数据
        
        Args:
            filepath: 文件路径
            extra_data: 额外的表单数据
            
        Returns:
            上传是否成功
        """
        if not os.path.exists(filepath):
            print(f"❌ 文件不存在：{filepath}")
            return False
        
        url = f"{BASE_URL}{UPLOAD_API}"
        
        print(f"🔄 正在上传：{os.path.basename(filepath)}")
        print(f"📡 请求 URL: {url}")
        
        for attempt in range(1, RETRY_COUNT + 1):
            try:
                with open(filepath, 'rb') as f:
                    # 准备表单数据
                    data = extra_data or {}
                    files = {
                        'file': (os.path.basename(filepath), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                        **{k: (None, v) for k, v in data.items()}
                    }
                    
                    response = self.session.post(
                        url,
                        files=files,
                        headers=self.headers,
                        timeout=TIMEOUT * 2
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('code') == 200:
                        print("✅ 上传成功！")
                        return True
                    else:
                        print(f"❌ 上传失败：{result.get('msg', '未知错误')}")
                        return False
                else:
                    print(f"⚠️ HTTP {response.status_code}，重试 {attempt}/{RETRY_COUNT}")
                    
            except requests.exceptions.RequestException as e:
                print(f"⚠️ 请求异常：{e}，重试 {attempt}/{RETRY_COUNT}")
        
        print("❌ 上传失败：超过最大重试次数")
        return False


if __name__ == '__main__':
    # 测试上传
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python3 uploader.py <excel 文件路径>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    # 需要先登录获取 token
    from login import LoginManager
    login_mgr = LoginManager()
    
    if not login_mgr.login():
        print("❌ 请先登录")
        sys.exit(1)
    
    uploader = Uploader(
        session=login_mgr.get_session(),
        headers=login_mgr.get_headers()
    )
    
    success = uploader.upload_excel(filepath)
    sys.exit(0 if success else 1)
