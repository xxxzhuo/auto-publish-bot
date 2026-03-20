# 三星 (Samsung) 存储芯片料号规则

**更新日期：** 2026-03-13  
**数据来源：** 网络搜索 + 实盘 OFFER 分析  
**版本：** v1.0

---

## 品牌识别规则

| 前缀 | 品牌 | 类型 | 说明 |
|------|------|------|------|
| K4 | Samsung | DRAM/NAND | 三星存储芯片主系列 |
| K4A | Samsung | DDR4/LPDDR4 | DDR4/LPDDR4 系列 |
| K4B | Samsung | DDR3 | DDR3 系列 |
| K4F | Samsung | LPDDR4X | LPDDR4X 系列 |
| K4U | Samsung | LPDDR4X | LPDDR4X 高密度系列 |
| K3K | Samsung | LPDDR4X | LPDDR4X 堆叠系列 |
| KMF | Samsung | eMCP | eMCP 封装 |
| KLUD | Samsung | UFS | UFS 存储 |
| HN8T | Samsung | NAND | NAND Flash |
| H26T | Samsung | NAND | NAND Flash |
| THG | Samsung | eMCP | eMCP 封装 |
| K4AAG | Samsung | LPDDR4X | LPDDR4X 新系列 |

---

## 料号格式解析

### 示例 1: K4U6E3S4AA-MGCR0UT

| 字段 | 值 | 说明 |
|------|-----|------|
| 系列 | K4U | LPDDR4X |
| 密度 | 6E3S4 | 配置代码 |
| 版本 | AA | 版本 |
| 速度 | MGCR | 速度等级 |
| 包装 | 0UT | 包装类型 |

### 示例 2: K3KL9L900M-MFCT

| 字段 | 值 | 说明 |
|------|-----|------|
| 系列 | K3KL | LPDDR4X 堆叠 |
| 密度 | 9L900M | 配置代码 |
| 速度 | MFCT | 速度等级 |

### 示例 3: K4A8G165WG-BCWE000

| 字段 | 值 | 说明 |
|------|-----|------|
| 系列 | K4A | DDR4/LPDDR4 |
| 密度 | 8G16 | 8Gb x16 |
| 版本 | 5WG | 版本 |
| 速度 | BCWE | 速度等级 |
| 包装 | 000 | 标准包装 |

---

## 产品类型

| 系列 | 类型 | 应用 |
|------|------|------|
| K4A | DDR4/LPDDR4 | 手机/平板 |
| K4B | DDR3 | 传统设备 |
| K4F | LPDDR4X | 移动设备 |
| K4U | LPDDR4X | 高密度移动设备 |
| K3K | LPDDR4X 堆叠 | 高端手机 |
| KMF | eMCP | 嵌入式存储 |
| KLUD | UFS | 高速存储 |
| HN8T/H26T | NAND Flash | 大容量存储 |
| THG | eMCP | 嵌入式存储 |

---

## 速度等级识别

| 代码 | 速度 | 说明 |
|------|------|------|
| BCWE | 3200Mbps | DDR4-3200 |
| BCRC | 2666Mbps | DDR4-2666 |
| BCTD | 2400Mbps | DDR4-2400 |
| MGCR | 4266Mbps | LPDDR4X-4266 |
| MFCT | 3200Mbps | LPDDR4X-3200 |
| JFCT | 3200Mbps | LPDDR4X-3200 |
| JHCT | 4266Mbps | LPDDR4X-4266 |
| THCL | 2133Mbps | LPDDR4X-2133 |
| GFCL | 1866Mbps | LPDDR4X-1866 |
| MCTD | 2133Mbps | LPDDR4X-2133 |

---

## 解析示例

### 输入
```
K4U6E3S4AA-MGCR0UT 23+ 35U
K3KL9L900M-MFCT 25+ 170U
K4A8G165WG-BCWE000 25+ 29U
```

### 输出
```json
[
  {
    "料号型号": "K4U6E3S4AA-MGCR0UT",
    "品牌": "Samsung",
    "产品分类": "LPDDR4X",
    "单价": 35.0,
    "批次（DC）": "23+"
  },
  {
    "料号型号": "K3KL9L900M-MFCT",
    "品牌": "Samsung",
    "产品分类": "LPDDR4X",
    "单价": 170.0,
    "批次（DC）": "25+"
  },
  {
    "料号型号": "K4A8G165WG-BCWE000",
    "品牌": "Samsung",
    "产品分类": "LPDDR4X",
    "单价": 29.0,
    "批次（DC）": "25+"
  }
]
```

---

## 实盘数据分析

**数据来源：** 2026-03-13 香港现货 OFFER

**样本统计：**
- 总产品数：22 个
- Samsung 产品：18 个 (81.8%)
- Micron 产品：1 个 (4.5%)
- SK Hynix 产品：3 个 (13.6%)

**价格区间：**
- 最低：USD 6.0 (K4A4G165WF-BCTD000)
- 最高：USD 285.0 (MT62F2G32D4DS-023)
- 平均：USD 89.77

**DC 分布：**
- DC20+: 4 个
- DC21+: 1 个
- DC23+: 1 个
- DC24+: 1 个
- DC25+: 14 个
- DC26+: 1 个

---

## 规则维护

### 更新记录
- **2026-03-13:** 初始版本，基于 22 个实盘料号分析

### 待补充
- [ ] 更详细的速度等级对照表
- [ ] 密度代码解析规则
- [ ] 封装类型识别
- [ ] 温度等级标识

---

**最后更新：** 2026-03-13  
**数据来源：** 网络搜索 + 实盘 OFFER  
**状态：** ✅ 已应用至自动发布机器人
