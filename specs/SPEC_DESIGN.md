# 六爻网站 - Spec Design v0.1

> **文档定位**：描述系统**如何构建**（技术实现方案、接口契约、数据模型、架构决策）。  
> 上游依赖：[SPEC_REQUIREMENT.md](./SPEC_REQUIREMENT.md)（定义"做什么"）  
> 下游产出：[SPEC_IMPLEMENTATION.md]（具体代码、配置、部署脚本）

---

## 1. 系统架构概览

```
用户浏览器
    │
    ▼
前端 SPA (React / Next.js)
    │  REST API (JSON)
    ▼
后端 API 服务 (FastAPI / Express)
    ├── 规则引擎 (纯函数，无副作用)
    │       └── 爻象映射 → 卦象生成 → 解读模板
    ├── PostgreSQL  (持久化)
    └── Redis       (卦象数据缓存)
```

**核心路径**：`提问 → 起卦（×6次cast） → 服务端生成卦象 → 解读 → Follow-up 对话`

---

## 2. 后端 API 设计

### 2.1 端点列表

| Method | Path | 功能 |
|--------|------|------|
| POST | `/api/divination/create` | 创建起卦记录 |
| POST | `/api/divination/{id}/cast` | 记录一次抛币（×6） |
| GET  | `/api/divination/{id}/result` | 获取完整解读 |
| GET  | `/api/divinations/history` | 历史记录列表 |
| GET  | `/api/hexagrams/{number}` | 卦象详情 |
| GET  | `/api/rules/basic` | 六爻规则说明 |
| POST | `/api/divination/{id}/followup` | Follow-up 追问 |

---

### 2.2 端点详情

#### POST `/api/divination/create`

**请求体**:
```json
{
  "question": "string (required)",
  "category": "感情|事业|财运|学业|合作|健康|寻物|其他",
  "timeframe": "近期|一个月内|三个月内|半年内|自定义",
  "notes": "string (optional)",
  "language": "zh-CN|zh-TW|en"
}
```

**响应**:
```json
{
  "divination_id": "uuid",
  "question": "string",
  "category": "string",
  "created_at": "ISO8601",
  "language": "string"
}
```

---

#### POST `/api/divination/{divination_id}/cast`

前端传入三枚硬币面值，服务端自动推导爻类型（不依赖前端传 result）。

**请求体**:
```json
{
  "line_number": 1,
  "coin_values": [3, 2, 3]
}
```

> `coin_values`：三枚硬币各自面值，正面=3，反面=2。

**服务端推导规则**：
- sum=6 → 老阴（动爻）
- sum=7 → 少阳（静爻）
- sum=8 → 少阴（静爻）
- sum=9 → 老阳（动爻）

**响应**:
```json
{
  "divination_id": "uuid",
  "current_line": 1,
  "coin_sum": 8,
  "line_result": "少阴",
  "is_changing": false,
  "lines_completed": 1
}
```

---

#### GET `/api/divination/{divination_id}/result`

**响应**:
```json
{
  "divination_id": "uuid",
  "question": "string",
  "category": "string",
  "cast_records": [
    {
      "line_number": 1,
      "coin_values": [3, 2, 3],
      "coin_sum": 8,
      "line_result": "少阴",
      "is_changing": false
    }
  ],
  "original_hexagram": {
    "name": "乾",
    "code": "111111",
    "number": 1
  },
  "changing_lines": [1, 3],
  "future_hexagram": {
    "name": "坤",
    "code": "000000",
    "number": 2
  },
  "interpretation": {
    "summary": "string (3-5句白话总结)",
    "original_meaning": "string (本卦解读)",
    "changing_analysis": "string (动爻解读)",
    "future_trend": "string (变卦与趋势)",
    "world_response_analysis": "string (世应关系)",
    "category_specific_advice": "string (分类建议)",
    "recommendations": ["建议1", "建议2", "建议3"]
  },
  "created_at": "ISO8601"
}
```

---

#### GET `/api/divinations/history`

**查询参数**:
- `limit`: 10-100 (default: 20)
- `offset`: 0+
- `category`: optional filter

**响应**:
```json
{
  "total": "integer",
  "items": [
    {
      "divination_id": "uuid",
      "question": "string",
      "category": "string",
      "hexagram_name": "string",
      "created_at": "ISO8601",
      "summary": "string (前50字)"
    }
  ]
}
```

---

#### GET `/api/hexagrams/{hexagram_number}`

**响应**:
```json
{
  "number": 1,
  "name": "乾",
  "upper_trigram": "乾",
  "lower_trigram": "乾",
  "traditional_meaning": "string",
  "modern_interpretation": "string"
}
```

---

#### GET `/api/rules/basic`

**响应**:
```json
{
  "what_is_liuyao": "string",
  "why_ask_question": "string",
  "why_six_tosses": "string",
  "hexagram_basics": "string",
  "world_response": "string",
  "six_relatives": "string",
  "how_to_read_result": "string"
}
```

---

#### POST `/api/divination/{divination_id}/followup`

**请求体**:
```json
{
  "message": "string (required)",
  "conversation_id": "uuid (optional)"
}
```

**响应**:
```json
{
  "conversation_id": "uuid",
  "divination_id": "uuid",
  "reply": "string",
  "messages": [
    {
      "role": "user|assistant",
      "content": "string",
      "created_at": "ISO8601"
    }
  ]
}
```

---

### 2.3 统一错误响应格式

```json
{
  "error_code": "INVALID_COIN_VALUES",
  "message": "coin_values must be array of three values, each 2 or 3",
  "details": {}
}
```

---

## 3. 数据模型

### 3.1 核心表结构

#### `divinations` 表
```sql
CREATE TABLE divinations (
  id UUID PRIMARY KEY,
  user_id UUID,                          -- nullable for MVP
  question TEXT NOT NULL,
  category VARCHAR(50),
  timeframe VARCHAR(50),
  notes TEXT,
  language VARCHAR(10) DEFAULT 'zh-CN',
  original_hexagram_number INT,          -- 1-64
  changing_lines JSON,                   -- e.g., [1,3,5]
  future_hexagram_number INT,            -- 1-64
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

#### `divination_lines` 表
```sql
CREATE TABLE divination_lines (
  id UUID PRIMARY KEY,
  divination_id UUID NOT NULL,
  line_number INT NOT NULL,              -- 1-6
  coin_values JSON NOT NULL,             -- e.g., [3, 2, 3]
  coin_sum INT NOT NULL,                 -- 6 | 7 | 8 | 9
  result VARCHAR(20) NOT NULL,           -- '老阴'|'少阳'|'少阴'|'老阳'
  is_changing BOOLEAN NOT NULL,          -- TRUE if coin_sum is 6 or 9
  created_at TIMESTAMP
);
```

#### `hexagrams` 表
```sql
CREATE TABLE hexagrams (
  id INT PRIMARY KEY,                    -- 1-64
  name VARCHAR(50),
  upper_trigram VARCHAR(50),
  lower_trigram VARCHAR(50),
  binary_code CHAR(6),                   -- e.g., '111111'
  traditional_meaning TEXT,
  modern_interpretation TEXT
);
```

#### `interpretation_templates` 表
```sql
CREATE TABLE interpretation_templates (
  id UUID PRIMARY KEY,
  hexagram_number INT,
  category VARCHAR(50),
  language VARCHAR(10),
  template_text TEXT,                    -- 包含占位符 {world}, {response}, etc
  created_at TIMESTAMP
);
```

#### `followup_conversations` 表
```sql
CREATE TABLE followup_conversations (
  id UUID PRIMARY KEY,
  divination_id UUID NOT NULL UNIQUE,    -- 每次卦象最多 1 个对话
  created_at TIMESTAMP
);
```

#### `followup_messages` 表
```sql
CREATE TABLE followup_messages (
  id UUID PRIMARY KEY,
  conversation_id UUID NOT NULL,
  role VARCHAR(10) NOT NULL,             -- 'user' | 'assistant'
  content TEXT NOT NULL,
  created_at TIMESTAMP
);
```

---

## 4. 前端架构

### 4.1 路由结构

```
/                          → 首页
/ask                       → 提问页
/cast/:divination_id       → 起卦页
/result/:divination_id     → 结果页（含 Follow-up 区块）
/history                   → 历史记录（MVP 可选，需登录）
/rules                     → 规则说明页
/about                     → 关于我们
/faq                       → 常见问题
```

### 4.2 技术栈

| 层级 | 选型 |
|------|------|
| 框架 | Next.js (App Router) |
| 样式 | Tailwind CSS |
| 状态管理 | Zustand |
| HTTP 客户端 | axios / fetch |
| 动画 | Framer Motion（抛币动画） |
| 卦象渲染 | 自定义 SVG 组件 |

### 4.3 关键组件

```
HexagramDisplay       → 卦象可视化（本卦/变卦，含动爻标记）
CoinFlipPanel         → 抛币交互（单次 3 枚，×6 次）
CastRecord            → 原始抛掷记录表格
InterpretationCard    → 解读卡片
FollowUpChat          → Follow-up 对话区块
HistoryList           → 历史记录列表
```

---

## 5. 后端架构

### 5.1 技术栈

| 层级 | 选型 |
|------|------|
| 语言 | Python 3.11+ |
| 框架 | FastAPI |
| 数据库 | PostgreSQL 15 + Redis 7 |
| 部署 | Docker + docker-compose |

### 5.2 项目结构

```
backend/
├── app/
│   ├── api/
│   │   ├── divinations.py     (起卦相关 endpoints)
│   │   ├── hexagrams.py       (卦象查询)
│   │   ├── rules.py           (规则说明)
│   │   └── followup.py        (追问对话)
│   ├── core/
│   │   ├── rules_engine.py    (爻象推导、卦象生成，纯函数)
│   │   ├── hexagram_data.py   (64卦数据)
│   │   └── templates.py       (解读模板)
│   ├── models/
│   │   └── divination.py      (SQLAlchemy 模型)
│   └── main.py
├── tests/
├── requirements.txt
└── docker-compose.yml
```

---

## 6. 核心算法：卦象生成

```python
def derive_line_type(coin_values: list[int]) -> dict:
    """
    Input:  [3, 2, 3]  (三枚硬币面值，正面=3，反面=2)
    Output: { sum: 8, result: '少阴', is_changing: False }
    """
    s = sum(coin_values)
    mapping = {
        6: ('老阴', True),
        7: ('少阳', False),
        8: ('少阴', False),
        9: ('老阳', True),
    }
    result, is_changing = mapping[s]
    return { 'sum': s, 'result': result, 'is_changing': is_changing }


def generate_hexagram(line_results: list[str]) -> dict:
    """
    Input:  ['少阳', '少阴', '老阳', '少阳', '老阴', '少阳']
            index 0 = 初爻, index 5 = 上爻
    Output: { original: 11, changing_lines: [3, 5], future: 54 }
    """
    # 1. 阳=1，阴=0
    bits = ['1' if '阳' in r else '0' for r in line_results]

    # 2. 初爻在最低位，上爻在最高位 → 反转后转十进制查表
    original_code = ''.join(reversed(bits))
    original_num = HEXAGRAM_TABLE[original_code]   # code → 1-64

    # 3. 老爻位置
    changing = [i + 1 for i, r in enumerate(line_results) if '老' in r]

    # 4. 变卦：翻转老爻对应 bit
    future_bits = bits[:]
    for i in changing:
        future_bits[i - 1] = '0' if bits[i - 1] == '1' else '1'
    future_code = ''.join(reversed(future_bits))
    future_num = HEXAGRAM_TABLE[future_code]

    return {
        'original_hexagram': original_num,
        'changing_lines': changing,
        'future_hexagram': future_num,
    }
```

---

## 7. 64 卦对照表（六位二进制编码）

> 编码规则：位 0（最低位）= 初爻，位 5（最高位）= 上爻；阳=1，阴=0。

| # | 名称 | 上卦 | 下卦 | 二进制码 |
|---|------|------|------|---------|
| 1 | 乾 | 乾 | 乾 | 111111 |
| 2 | 坤 | 坤 | 坤 | 000000 |
| 3 | 屯 | 坎 | 震 | 010001 |
| 4 | 蒙 | 艮 | 坎 | 100010 |
| 5 | 需 | 坎 | 乾 | 010111 |
| 6 | 讼 | 乾 | 坎 | 111010 |
| 7 | 师 | 坤 | 坎 | 000010 |
| 8 | 比 | 坎 | 坤 | 010000 |
| 9 | 小畜 | 巽 | 乾 | 110111 |
| 10 | 履 | 乾 | 兑 | 111011 |
| 11 | 泰 | 坤 | 乾 | 000111 |
| 12 | 否 | 乾 | 坤 | 111000 |
| 13 | 同人 | 乾 | 离 | 111101 |
| 14 | 大有 | 离 | 乾 | 101111 |
| 15 | 谦 | 坤 | 艮 | 000100 |
| 16 | 豫 | 震 | 坤 | 001000 |
| 17 | 随 | 兑 | 震 | 011001 |
| 18 | 蛊 | 艮 | 巽 | 100110 |
| 19 | 临 | 坤 | 兑 | 000011 |
| 20 | 观 | 巽 | 坤 | 110000 |
| 21 | 噬嗑 | 离 | 震 | 101001 |
| 22 | 贲 | 艮 | 离 | 100101 |
| 23 | 剥 | 艮 | 坤 | 100000 |
| 24 | 复 | 坤 | 震 | 000001 |
| 25 | 无妄 | 乾 | 震 | 111001 |
| 26 | 大畜 | 艮 | 乾 | 100111 |
| 27 | 颐 | 艮 | 震 | 100001 |
| 28 | 大过 | 兑 | 巽 | 011110 |
| 29 | 坎 | 坎 | 坎 | 010010 |
| 30 | 离 | 离 | 离 | 101101 |
| 31 | 咸 | 兑 | 艮 | 011100 |
| 32 | 恒 | 震 | 巽 | 001110 |
| 33 | 遁 | 乾 | 艮 | 111100 |
| 34 | 大壮 | 震 | 乾 | 001111 |
| 35 | 晋 | 离 | 坤 | 101000 |
| 36 | 明夷 | 坤 | 离 | 000101 |
| 37 | 家人 | 巽 | 离 | 110101 |
| 38 | 睽 | 离 | 兑 | 101011 |
| 39 | 蹇 | 坎 | 艮 | 010100 |
| 40 | 解 | 震 | 坎 | 001010 |
| 41 | 损 | 艮 | 兑 | 100011 |
| 42 | 益 | 巽 | 震 | 110001 |
| 43 | 夬 | 兑 | 乾 | 011111 |
| 44 | 姤 | 乾 | 巽 | 111110 |
| 45 | 萃 | 兑 | 坤 | 011000 |
| 46 | 升 | 坤 | 巽 | 000110 |
| 47 | 困 | 兑 | 坎 | 011010 |
| 48 | 井 | 坎 | 巽 | 010110 |
| 49 | 革 | 兑 | 离 | 011101 |
| 50 | 鼎 | 离 | 巽 | 101110 |
| 51 | 震 | 震 | 震 | 001001 |
| 52 | 艮 | 艮 | 艮 | 100100 |
| 53 | 渐 | 巽 | 艮 | 110100 |
| 54 | 归妹 | 震 | 兑 | 001011 |
| 55 | 丰 | 震 | 离 | 001101 |
| 56 | 旅 | 离 | 艮 | 101100 |
| 57 | 巽 | 巽 | 巽 | 110110 |
| 58 | 兑 | 兑 | 兑 | 011011 |
| 59 | 涣 | 巽 | 坎 | 110010 |
| 60 | 节 | 坎 | 兑 | 010011 |
| 61 | 中孚 | 巽 | 兑 | 110011 |
| 62 | 小过 | 震 | 艮 | 001100 |
| 63 | 既济 | 坎 | 离 | 010101 |
| 64 | 未济 | 离 | 坎 | 101010 |

---

## 8. API 使用示例

```
1. POST /api/divination/create
   请求: { "question": "这次换工作能成功吗？", "category": "事业" }
   响应: { "divination_id": "abc-123" }

2. POST /api/divination/abc-123/cast  ×6
   第1次: { "line_number": 1, "coin_values": [3, 2, 3] }  → sum=8 少阴 静
   第2次: { "line_number": 2, "coin_values": [3, 3, 3] }  → sum=9 老阳 动
   ...
   第6次: { "line_number": 6, "coin_values": [2, 2, 3] }  → sum=7 少阳 静

3. GET /api/divination/abc-123/result
   响应: 完整解读（本卦 + 变卦 + 动爻分析 + 分类建议）

4. POST /api/divination/abc-123/followup
   请求: { "message": "关于事业转变，有什么具体建议？" }
   响应: { "conversation_id": "...", "reply": "基于本卦..." }
```

---

## 9. 开发阶段规划

### Phase 1: MVP (Week 1-3)

**后端**:
- [ ] 规则引擎：爻象推导 + 卦象生成
- [ ] 卦象数据库：64卦入库
- [ ] 核心 API：create、cast、result
- [ ] 基础解读引擎（卦义 + 分类映射）

**前端**:
- [ ] 首页、提问页、起卦页、结果页
- [ ] 响应式布局

**部署**:
- [ ] Docker Compose 本地环境

### Phase 2: 完善 (Week 4-5)

- [ ] Follow-up 追问对话
- [ ] 历史记录页面
- [ ] 规则说明页
- [ ] 错误处理与边界覆盖
- [ ] 前端性能优化

### Phase 3: 二期 (Week 6+)

- [ ] 用户认证（JWT）
- [ ] 多语言 i18n
- [ ] AI 解读接入
- [ ] 会员系统

---

## 更新日志

- **v0.1** (2026-04-12): 从 SPEC_REQUIREMENT v1.0 中提取 Design 内容，独立成文
