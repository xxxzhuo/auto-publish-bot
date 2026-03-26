# 🦞 先搜精选自动发布系统 v4.0 - 升级说明

**升级日期：** 2026-03-26 14:50 (Asia/Shanghai)  
**升级类型：** 重大功能升级

---

## 📦 升级内容

### 1. ✅ 项目更名
- **原名：** 自动发布机器人
- **新名：** 先搜精选自动发布系统
- **路径：** `/Users/mac/Desktop/先搜精选自动发布系统/`

### 2. ✅ 动态手机号支持

**v3.0 (旧):**
```python
PHONE_NUMBER = "13798441628"  # 硬编码
SMS_CODE = "2222"
```

**v4.0 (新):**
```python
# 支持动态参数传入
def login(self, mobile: Optional[str] = None, sms_code: Optional[str] = None):
    mobile = mobile or DEFAULT_PHONE_NUMBER
    sms_code = sms_code or DEFAULT_SMS_CODE
```

**使用方式:**
```python
# 方式 1: API 调用
POST /api/publish
{
  "text": "K4UBE3D4AB-KFCL03V 25+ 90U",
  "mobile": "13798441628",  # 动态手机号
  "sms_code": "2222"
}

# 方式 2: Python SDK
from skills.xiansou_auto_publisher.publisher import publish_offer

result = publish_offer(
    mobile="13798441628",  # 动态传入
    offer_text="K4UBE3D4AB-KFCL03V 25+ 90U"
)
```

### 3. ✅ 品牌名映射（中文 → 英文）

**映射表:**
| 中文名 | 英文名 |
|--------|--------|
| 三星 | Samsung |
| 海力士 | SK Hynix |
| 镁光/美光 | Micron |
| 南亚 | Nanya |
| 金士顿 | Kingston |
| 兆易创新 | GigaDevice |
| 华邦 | Winbond |
| 晶存 | Puya |
| 英特尔 | Intel |

**实现位置:**
```python
# all_in_one.py
BRAND_NAME_MAPPING = {
    "三星": "Samsung",
    "海力士": "SK Hynix",
    ...
}

def map_brand_name(brand: str) -> str:
    return BRAND_NAME_MAPPING.get(brand, brand)
```

**效果:**
- 输入：`三星 K4UBE3D4AB` → 输出：`品牌：Samsung`
- 输入：`镁光 MT41J512M8` → 输出：`品牌：Micron`

### 4. ✅ OpenClaw 技能集成

**技能位置:** `~/.openclaw/workspace/skills/xiansou-auto-publisher/`

**触发词:**
- "使用先搜精选自动发布系统发布"
- "发布 OFFER 到鸿达"
- "自动发布"

**使用示例:**
```
用户：使用先搜精选自动发布系统发布，手机号 13798441628
OFFER:
K3KL9L900M-MFCT 25+ 170U
K4UBE3D4AB-KFCL03V 25+ 90U

助手：✅ 发布成功！共 2 个产品
```

**技能文件:**
- `SKILL.md` - 技能说明文档
- `publisher.py` - 发布器核心模块
- `workflow.py` - OpenClaw 工作流

---

## 🔧 技术改动

### 修改的文件

1. **all_in_one.py**
   - 添加 `BRAND_NAME_MAPPING` 和 `map_brand_name()` 函数
   - 修改 `LoginManager.login()` 支持动态手机号
   - 修改 `PublishRequest` 添加 `mobile` 和 `sms_code` 参数
   - 修改 `api_publish()` 支持动态手机号登录
   - 在所有品牌识别后调用 `map_brand_name()`

2. **README.md**
   - 更新为 v4.0 文档
   - 添加新特性说明
   - 添加 OpenClaw 使用示例

### 新增的文件

1. **OpenClaw 技能目录**
   ```
   ~/.openclaw/workspace/skills/xiansou-auto-publisher/
   ├── SKILL.md          # 技能说明
   ├── publisher.py      # 发布器核心
   └── workflow.py       # OpenClaw 工作流
   ```

---

## 📊 版本对比

| 特性 | v3.0 | v4.0 |
|------|------|------|
| 手机号 | 硬编码 | ✅ 动态参数 |
| 品牌名映射 | ❌ | ✅ 中文→英文 |
| OpenClaw 集成 | ❌ | ✅ 自然语言触发 |
| API 动态手机号 | ❌ | ✅ 支持 |
| 项目名 | 自动发布机器人 | ✅ 先搜精选自动发布系统 |

---

## 🎯 使用场景

### 场景 1: Web 界面手动发布
```
1. 启动服务：python3 all_in_one.py
2. 打开前端：open frontend.html
3. 输入手机号和 OFFER
4. 点击发布
```

### 场景 2: API 调用
```bash
curl -X POST http://localhost:8000/api/publish \
  -H "Content-Type: application/json" \
  -d '{
    "text": "K4UBE3D4AB-KFCL03V 25+ 90U",
    "mobile": "13798441628",
    "sms_code": "2222"
  }'
```

### 场景 3: OpenClaw 自然语言
```
用户：使用先搜精选自动发布系统发布，手机号 13798441628
OFFER:
香港现货 实单开价:
K3KL9L900M-MFCT 25+ 170U
K4UBE3D4AB-KFCL03V 25+ 90U
```

### 场景 4: Python SDK
```python
from skills.xiansou_auto_publisher.publisher import publish_offer

result = publish_offer(
    mobile="13798441628",
    offer_text="K4UBE3D4AB-KFCL03V 25+ 90U"
)

print(result)
# {
#   "success": True,
#   "message": "✅ 发布成功！共 1 个产品",
#   "products_count": 1,
#   "excel_file": "/Users/mac/Desktop/先搜精选自动发布系统/output/..."
# }
```

---

## ⚠️ 注意事项

### 1. 兼容性
- ✅ 向后兼容：不传手机号时使用默认值
- ✅ 旧 API 仍可使用 token 方式

### 2. 品牌名映射
- 仅映射中文品牌名，英文保持不变
- 映射发生在解析之后、上传之前

### 3. 手机号验证
- 支持 10-11 位手机号
- 格式错误时返回明确提示

---

## 📝 Git 提交记录

```bash
commit 103bc83
Author: OpenClaw Assistant
Date:   2026-03-26 14:50

    🦞 先搜精选 v4.0 - OpenClaw 集成版
    
    新特性:
    - 支持动态手机号传入（不再硬编码）
    - 品牌名映射（中文→英文）
    - OpenClaw 技能集成
    - 支持自然语言触发
```

**远程仓库:** https://github.com/xxxzhuo/auto-publish-bot  
**版本标签:** `xiansou-v4.0-20260326`

---

## 🎉 升级完成

**状态：** ✅ 已完成  
**测试：** 待用户验证  
**下一步：** 测试新功能

---

**升级时间：** 2026-03-26 14:50 (Asia/Shanghai)  
**执行人：** OpenClaw Assistant
