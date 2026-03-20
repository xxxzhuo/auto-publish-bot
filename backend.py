#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发布机器人 - Web 后端 API 服务（真实接口版）
版本:v2.0
日期:2026-03-13

功能:
- POST /api/login - 用户登录（调用真实接口）
- POST /api/parse - 解析 OFFER 文本
- POST /api/publish - 发布产品（调用真实上传接口）
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import sys
import os

# 添加项目路径
sys.path.insert(0, '/Users/mac/Desktop/自动发布机器人')

from offer_parser import OfferParser
from excel_generator import ExcelGenerator
from login import LoginManager
from uploader import Uploader
from config import BASE_URL, LOGIN_API, UPLOAD_API, PHONE_NUMBER, SMS_CODE

# 创建 FastAPI 应用
app = FastAPI(
    title="自动发布机器人 API",
    description="鸿达半导体自动发布系统（真实接口版）",
    version="2.0"
)

# 配置 CORS（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 数据模型 ==========

class LoginRequest(BaseModel):
    mobile: str
    smsCode: str = "2222"

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    username: Optional[str] = None

class ParseRequest(BaseModel):
    text: str

class ProductItem(BaseModel):
    料号型号:str
    品牌:str
    单价:float
    货币单位:str
    数量:Optional[int] = None
    批次:Optional[str] = None
    交货天数:int
    货所在地:str

class ParseResponse(BaseModel):
    success: bool
    count: int
    products: List[Dict]
    message: str

class PublishRequest(BaseModel):
    text: str

class PublishResponse(BaseModel):
    success: bool
    message: str
    excel_path: Optional[str] = None
    count: int

# ========== 全局变量 ==========

# 存储用户 token 和信息
user_sessions = {}

# ========== API 接口 ==========

@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录接口（调用真实 API）
    
    - mobile: 手机号
    - smsCode: 短信验证码（默认 2222）
    """
    try:
        print(f"\n📞 登录请求:{request.mobile}")
        
        # 调用真实登录接口
        login_mgr = LoginManager()
        success = login_mgr.login(request.mobile, request.smsCode)
        
        if success:
            token = login_mgr.get_token()
            user_info = login_mgr.user_info
            
            # 存储会话
            user_sessions[request.mobile] = {
                'token': token,
                'session': login_mgr.get_session(),
                'user_info': user_info
            }
            
            return LoginResponse(
                success=True,
                message="登录成功",
                token=token,
                username=user_info.get('username')
            )
        else:
            return LoginResponse(
                success=False,
                message="登录失败，请检查手机号和验证码",
                token=None
            )
            
    except Exception as e:
        print(f"❌ 登录异常:{e}")
        return LoginResponse(
            success=False,
            message=f"登录失败:{str(e)}",
            token=None
        )

@app.post("/api/parse", response_model=ParseResponse)
async def parse_offer(request: ParseRequest):
    """
    解析 OFFER 文本
    
    - text: OFFER 文本内容
    """
    try:
        from universal_parser import UniversalOfferParser
        
        parser = UniversalOfferParser()
        products = parser.parse(request.text)
        
        if not products:
            return ParseResponse(
                success=False,
                count=0,
                products=[],
                message="未解析到任何产品"
            )
        
        # 格式化产品列表
        product_list = []
        for p in products:
            product_list.append({
                '料号型号': p.get('料号型号', ''),
                '品牌': p.get('品牌', ''),
                '单价': p.get('单价', 0),
                '货币单位': p.get('货币单位（usd/cny）', 'usd'),
                '数量': p.get('数量'),
                '批次': p.get('批次（DC）'),
                '交货天数': p.get('交货天数', 7),
                '货所在地': p.get('货所在地', 'HK'),
                '企业名称': p.get('企业名称', '鸿达半导体'),
                '货物情况': p.get('货物情况（多选）', '全新'),
                '产品分类': p.get('产品分类', '存储芯片'),
            })
        
        return ParseResponse(
            success=True,
            count=len(products),
            products=product_list,
            message=f"成功解析 {len(products)} 个产品"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"解析失败:{str(e)}")

@app.post("/api/publish", response_model=PublishResponse)
async def publish(request: PublishRequest, authorization: Optional[str] = Header(None)):
    """
    发布产品（调用真实上传接口）
    
    - text: OFFER 文本内容
    - authorization: Bearer token
    """
    try:
        # 验证 token
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="未授权访问")
        
        token = authorization.split(" ")[1]
        
        # 查找用户会话
        user_session = None
        for mobile, session in user_sessions.items():
            if session['token'] == token:
                user_session = session
                break
        
        if not user_session:
            raise HTTPException(status_code=401, detail="Token 无效或已过期")
        
        # 解析 OFFER
        from universal_parser import UniversalOfferParser
        parser = UniversalOfferParser()
        products = parser.parse(request.text)
        
        if not products:
            raise HTTPException(status_code=400, detail="未解析到任何产品")
        
        # 生成 Excel
        from datetime import datetime
        generator = ExcelGenerator()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"供需信息_{timestamp}.xlsx"
        
        filepath = generator.create_excel(products, filename)
        
        if not filepath:
            raise HTTPException(status_code=500, detail="Excel 生成失败")
        
        # 调用真实上传接口
        uploader = Uploader(
            session=user_session['session'],
            headers=user_session['session'].headers
        )
        
        # 设置 Authorization header
        uploader.headers['Authorization'] = f'Bearer {token}'
        
        upload_success = uploader.upload_excel(filepath)
        
        if not upload_success:
            raise HTTPException(status_code=500, detail="上传失败")
        
        return PublishResponse(
            success=True,
            message=f"成功发布 {len(products)} 个产品",
            excel_path=filepath,
            count=len(products)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 发布异常:{e}")
        raise HTTPException(status_code=500, detail=f"发布失败:{str(e)}")

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "自动发布机器人 API",
        "version": "2.0 (真实接口)",
        "base_url": BASE_URL
    }

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用自动发布机器人 API（真实接口版）",
        "docs": "/docs",
        "health": "/api/health"
    }

# ========== 主程序 ==========

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 自动发布机器人 API 服务 v2.0")
    print("=" * 60)
    print()
    print("📡 服务地址:http://localhost:8000")
    print("📚 API 文档:http://localhost:8000/docs")
    print()
    print("🔧 接口配置:")
    print(f"   BASE_URL: {BASE_URL}")
    print(f"   LOGIN_API: {LOGIN_API}")
    print(f"   UPLOAD_API: {UPLOAD_API}")
    print()
    print("🚀 启动服务...")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
