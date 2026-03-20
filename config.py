#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发布机器人 - 配置文件（真实接口版）
版本：v2.0
日期：2026-03-13
"""

# ========== 账号配置 ==========
PHONE_NUMBER = "13798441628"  # 手机号
SMS_CODE = "2222"             # 短信验证码（固定值）

# ========== 接口配置（真实环境）==========
BASE_URL = "http://129.204.124.204:89/dev-api"
LOGIN_API = "/api/mts-api/login"           # 登录接口
UPLOAD_API = "/api/mts-api/clue/import"    # 发布接口

# ========== 文件路径配置 ==========
PROJECT_DIR = "/Users/mac/Desktop/自动发布机器人"
PRODUCTS_DIR = f"{PROJECT_DIR}/products"
OUTPUT_DIR = f"{PROJECT_DIR}/output"
LOGS_DIR = f"{PROJECT_DIR}/logs"

# ========== 程序配置 ==========
TIMEOUT = 30               # 请求超时时间（秒）
RETRY_COUNT = 3            # 失败重试次数

# ========== 运行模式 ==========
# SIMULATE: 模拟模式（生成 Excel，不上传）
# REAL: 真实模式（登录 + 上传）
RUN_MODE = "REAL"          # 已配置真实接口
