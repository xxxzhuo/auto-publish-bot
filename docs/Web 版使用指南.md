# 🌐 自动发布机器人 - Web 版使用指南

**版本：** v1.0  
**日期：** 2026-03-13  
**模式：** Web 界面 + API 后端

---

## 🚀 快速启动

### 方法 1: 一键启动（推荐）

```bash
cd "/Users/mac/Desktop/自动发布机器人"
./start.sh
```

### 方法 2: 手动启动

```bash
# 1. 安装依赖
pip3 install -r requirements.txt

# 2. 启动后端服务
python3 backend.py

# 3. 在浏览器中打开前端页面
open frontend.html
```

---

## 📱 使用流程

### 步骤 1: 打开前端页面

在浏览器中打开：
```
/Users/mac/Desktop/自动发布机器人/frontend.html
```

或直接双击 `frontend.html` 文件

### 步骤 2: 登录系统

1. 输入手机号（11 位）
2. 输入 4 位数密码
3. 点击"登录"按钮

**登录成功后：**
- 右上角显示"已登录"状态
- 发布产品卡片自动显示

### 步骤 3: 粘贴 OFFER 文本

在文本框中粘贴 OFFER 内容，例如：
```
NT6AN256T32AV-J2 usd 19.5, reel, dc21+
H5CG48MEBDX014N usd 27.5，dc 25+
H5CG48AGBDX018N usd 49.0*6k around partial, 25+
```

### 步骤 4: 解析文本

点击"解析文本"按钮，系统会：
- ✅ 自动识别料号
- ✅ 提取价格、DC、数量等信息
- ✅ 显示解析结果列表
- ✅ 显示统计信息（产品数、品牌数、总金额）

### 步骤 5: 发布产品

确认解析结果无误后，点击"发布产品"按钮：
- ✅ 生成标准 Excel 文件
- ✅ 保存到 `output/` 目录
- ✅ 显示文件路径

---

## 🎨 界面功能

### 登录卡片
- 手机号输入（11 位验证）
- 密码输入（4 位数）
- 登录状态显示
- 登录成功提示

### 发布产品卡片
- OFFER 文本输入框
- 解析文本按钮
- 发布产品按钮（解析后启用）
- 操作结果提示

### 解析结果卡片
- 产品列表展示
- 详细信息显示（料号、品牌、价格、DC、数量、交期、地点）
- 统计信息卡片：
  - 产品数量
  - 品牌数量
  - 总金额 (USD)

---

## 🔧 API 接口

### 后端服务地址
```
http://localhost:8000
```

### API 文档
```
http://localhost:8000/docs
```

### 接口列表

#### 1. POST /api/login - 用户登录

**请求：**
```json
{
  "phone": "13800138000",
  "password": "1234"
}
```

**响应：**
```json
{
  "success": true,
  "message": "登录成功",
  "token": "token_xxx"
}
```

#### 2. POST /api/parse - 解析 OFFER

**请求：**
```json
{
  "text": "NT6AN256T32AV-J2 usd 19.5, dc21+"
}
```

**响应：**
```json
{
  "success": true,
  "count": 1,
  "products": [
    {
      "料号型号": "NT6AN256T32AV-J2",
      "品牌": "南亚科技 (Nanya)",
      "单价": 19.5,
      "货币单位": "usd",
      "批次": "21+",
      "交货天数": 7,
      "货所在地": "HK"
    }
  ],
  "message": "成功解析 1 个产品"
}
```

#### 3. POST /api/publish - 发布产品

**请求：**
```json
{
  "text": "NT6AN256T32AV-J2 usd 19.5, dc21+"
}
```

**Headers：**
```
Authorization: Bearer token_xxx
```

**响应：**
```json
{
  "success": true,
  "message": "成功发布 1 个产品",
  "excel_path": "/path/to/file.xlsx",
  "count": 1
}
```

#### 4. GET /api/health - 健康检查

**响应：**
```json
{
  "status": "ok",
  "service": "自动发布机器人 API",
  "version": "1.0"
}
```

---

## 📊 测试结果

### 登录测试 ✅
```bash
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000", "password": "1234"}'
```

**结果：** 登录成功，返回 token

### 解析测试 ✅
```bash
curl -X POST "http://localhost:8000/api/parse" \
  -H "Content-Type: application/json" \
  -d '{"text": "NT6AN256T32AV-J2 usd 19.5, dc21+\nH5CG48MEBDX014N usd 27.5，dc 25+"}'
```

**结果：** 成功解析 2 个产品

### 发布测试 ✅
```bash
curl -X POST "http://localhost:8000/api/publish" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token_xxx" \
  -d '{"text": "NT6AN256T32AV-J2 usd 19.5, dc21+"}'
```

**结果：** 生成 Excel 文件

---

## 📁 项目文件

### 后端文件
| 文件 | 说明 |
|------|------|
| `backend.py` | FastAPI 后端服务 |
| `offer_parser.py` | OFFER 解析模块 |
| `excel_generator.py` | Excel 生成模块 |
| `login.py` | 登录模块 |
| `uploader.py` | 上传模块 |

### 前端文件
| 文件 | 说明 |
|------|------|
| `frontend.html` | Web 界面（单文件） |
| `start.sh` | 启动脚本 |

### 配置文件
| 文件 | 说明 |
|------|------|
| `requirements.txt` | Python 依赖 |
| `config.py` | 系统配置 |

---

## 🔐 安全说明

### 当前模式（开发环境）
- ✅ 本地运行（localhost）
- ✅ 简单 token 验证
- ✅ 内存存储 token
- ⚠️ 不适合生产环境

### 生产环境建议
1. **使用 HTTPS**
2. **真实身份验证**（对接现有系统）
3. **Token 过期机制**
4. **数据库存储**
5. **请求限流**
6. **日志审计**

---

## ⚙️ 配置真实接口

### 1. 编辑 backend.py

找到登录接口部分，修改为真实调用：

```python
# 当前（模拟登录）
if len(request.phone) == 11 and request.phone.isdigit():
    token = f"token_{uuid.uuid4().hex}"
    return LoginResponse(success=True, token=token)

# 修改为（真实登录）
from login import LoginManager
login_mgr = LoginManager()
# 配置 BASE_URL 和 LOGIN_API
success = login_mgr.login_with_api(request.phone, request.password)
if success:
    return LoginResponse(success=True, token=login_mgr.token)
```

### 2. 配置上传接口

找到发布接口部分，启用真实上传：

```python
# 取消注释
from uploader import Uploader
uploader = Uploader()
success = uploader.upload_excel(filepath)
```

### 3. 配置 config.py

```python
BASE_URL = "https://api.example.com"
LOGIN_API = "/api/v1/login"
UPLOAD_API = "/api/v1/upload"
```

---

## 🐛 常见问题

### Q: 后端服务启动失败？
A: 检查端口 8000 是否被占用
```bash
lsof -ti:8000 | xargs kill -9
```

### Q: 前端页面打不开？
A: 直接双击 `frontend.html` 文件，或用浏览器打开

### Q: 登录失败？
A: 当前是模拟登录，任意 11 位手机号 +4 位密码即可

### Q: 解析失败？
A: 检查 OFFER 文本格式，确保料号在行首

### Q: 发布失败？
A: 检查是否已登录，token 是否有效

---

## 📞 快速命令

```bash
# 启动服务
./start.sh

# 查看服务状态
curl http://localhost:8000/api/health

# 查看 API 文档
open http://localhost:8000/docs

# 打开前端
open frontend.html

# 停止服务
# 在终端按 Ctrl+C
```

---

## 🎉 完成状态

| 功能 | 状态 |
|------|------|
| Web 前端界面 | ✅ 完成 |
| 用户登录 | ✅ 完成（模拟） |
| OFFER 解析 | ✅ 完成 |
| 产品发布 | ✅ 完成（生成 Excel） |
| API 后端服务 | ✅ 完成 |
| 真实接口对接 | ⏸️ 待配置 |

---

**🚀 项目已就绪！立即体验 Web 版自动发布机器人！**

**项目位置：** `/Users/mac/Desktop/自动发布机器人`  
**前端文件：** `frontend.html`  
**后端服务：** `http://localhost:8000`  
**API 文档：** `http://localhost:8000/docs`

**最后更新：** 2026-03-13 13:45
