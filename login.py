#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发布机器人 - 登录模块（真实接口版）
版本：v2.0
日期：2026-03-13
"""

import requests
import json
from typing import Dict, Optional
import sys
sys.path.append('/Users/mac/Desktop/自动发布机器人')
from config import PHONE_NUMBER, SMS_CODE, BASE_URL, LOGIN_API, TIMEOUT, RETRY_COUNT


class LoginManager:
    """登录管理器（真实接口）"""
    
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        
    def login(self, mobile: str = None, sms_code: str = None) -> bool:
        """
        执行登录（调用真实 API）
        
        Args:
            mobile: 手机号（可选，默认使用 config 配置）
            sms_code: 短信验证码（可选，默认使用 config 配置）
            
        Returns:
            bool: 登录是否成功
        """
        mobile = mobile or PHONE_NUMBER
        sms_code = sms_code or SMS_CODE
        
        if not mobile or not sms_code:
            print("❌ 错误：请在 config.py 中配置手机号和短信验证码")
            return False
        
        url = f"{BASE_URL}{LOGIN_API}"
        
        # 登录参数
        login_data = {
            "mobile": mobile,
            "smsCode": sms_code
        }
        
        print(f"🔄 正在登录：{mobile[:3]}****{mobile[-4:]}")
        print(f"📡 请求 URL: {url}")
        
        for attempt in range(1, RETRY_COUNT + 1):
            try:
                response = self.session.post(
                    url,
                    json=login_data,
                    timeout=TIMEOUT
                )
                
                print(f"📊 响应状态码：{response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 检查返回码
                    if result.get('code') == 200:
                        data = result.get('data', {})
                        self.token = data.get('token')
                        self.user_info = {
                            'username': data.get('username'),
                            'nickname': data.get('nickname'),
                            'mobile': data.get('mobile'),
                            'userId': data.get('userId')
                        }
                        
                        print("✅ 登录成功！")
                        print(f"👤 用户：{self.user_info['username']}")
                        print(f"🔑 Token: {self.token[:50]}...")
                        return True
                    else:
                        print(f"❌ 登录失败：{result.get('msg', '未知错误')}")
                        return False
                else:
                    print(f"⚠️ HTTP {response.status_code}，重试 {attempt}/{RETRY_COUNT}")
                    
            except requests.exceptions.RequestException as e:
                print(f"⚠️ 请求异常：{e}，重试 {attempt}/{RETRY_COUNT}")
        
        print("❌ 登录失败：超过最大重试次数")
        return False
    
    def get_headers(self) -> Dict:
        """获取请求头（包含 Token）"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'AutoBot/2.0'
        }
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        return headers
    
    def get_session(self) -> requests.Session:
        """获取会话对象"""
        return self.session
    
    def get_token(self) -> str:
        """获取 Token"""
        return self.token


if __name__ == '__main__':
    # 测试登录
    login_mgr = LoginManager()
    success = login_mgr.login()
    
    if success:
        print(f"\n✅ 登录成功")
        print(f"Token: {login_mgr.get_token()[:50]}...")
    else:
        print("\n❌ 登录失败")
