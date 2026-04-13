# 六爻网站 - Spec Requirement v1.0

## 1. 项目简述

**项目名称**: Liu Yao / 六爻在线起卦与解读平台

**目标**: 现代化六爻起卦 + 结构化解读工具平台

**核心路径**: 提问 → 起卦 → 生成盘面 → 解读 → 保存

**MVP范围**: 完整起卦流程 + 规则引擎 + 白话解读

---

## 2. MVP 核心功能清单

### 2.1 用户端 (Frontend)

| 功能模块 | 功能名称 | 状态 | 优先级 |
|---------|--------|------|-------|
| 首页 | 品牌介绍 + 快速入门 + CTA | MVP | P0 |
| 提问页 | 问题输入、分类、时间范围 | MVP | P0 |
| 起卦页 | 模拟抛币 + 显示结果 + 动爻记录 | MVP | P0 |
| 结果页 | 卦象展示 + 白话解读 + 建议 | MVP | P0 |
| 规则说明页 | 六爻基础知识 | MVP | P1 |
| 历史记录页 | 列表展示 + 查看详情 | MVP | P1 |
| 响应式设计 | 桌面 + 移动端适配 | MVP | P0 |

---

## 3. 后端 API 设计

### 3.1 核心 API 端点

#### POST `/api/divination/create`
**功能**: 创建一次起卦记录

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
**功能**: 添加一次抛币结果（共6次）

**请求体**:
```json
{
  "line_number": 1-6,  // 第几爻（从下到上）
  "result": "少阴|少阳|老阴|老阳"
}
```

**响应**:
```json
{
  "divination_id": "uuid",
  "current_line": "integer",
  "line_result": "少阴|少阳|老阴|老阳",
  "lines_completed": 0-6
}
```

---

#### GET `/api/divination/{divination_id}/result`
**功能**: 获取完整解读结果

**响应**:
```json
{
  "divination_id": "uuid",
  "question": "string",
  "category": "string",
  "original_hexagram": {
    "name": "string (e.g., 乾)",
    "code": "111111",  // 6个爻的编码
    "number": 1-64
  },
  "changing_lines": [1, 3],  // 老爻的位置
  "future_hexagram": {
    "name": "string (e.g., 坤)",
    "code": "000000",
    "number": 1-64
  },
  "interpretation": {
    "summary": "string (3-5句白话总结)",
    "original_meaning": "string (本卦解读)",
    "changing_analysis": "string (动爻解读)",
    "future_trend": "string (变卦与趋势)",
    "world_response_analysis": "string (世应关系)",
    "category_specific_advice": "string (分类建议：如感情、事业等)",
    "recommendations": ["建议1", "建议2", "建议3"]
  },
  "created_at": "ISO8601"
}
```

---

#### GET `/api/divinations/history`
**功能**: 获取历史记录列表（需登录）

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
**功能**: 获取卦象详细信息

**响应**:
```json
{
  "number": 1-64,
  "name": "string (e.g., 乾)",
  "upper_trigram": "string (乾)",
  "lower_trigram": "string (坤)",
  "traditional_meaning": "string",
  "modern_interpretation": "string"
}
```

---

#### GET `/api/rules/basic`
**功能**: 获取六爻规则说明

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

### 3.2 非功能性需求

- **鉴权**: JWT token（二期）
- **速率限制**: 免费用户每天5次，会员无限制（二期）
- **缓存**: 卦象数据Redis缓存
- **错误处理**: 统一错误响应格式
- **日志**: 所有请求/异常记录

---

## 4. 核心业务逻辑（后端规则引擎）

### 4.1 爻的映射规则

**抛币结果 → 爻象**:
- 两个正面 (2 heads) → 少阳 (阳)
- 两个反面 (2 tails) → 少阴 (阴)
- 一正一反 (1 head 1 tail) → 没有明确定义，建议设定为"少阳"或提示用户重新抛

**或者采用更常见的六枚硬币规则**:
- 硬币数值和为偶数 → 阴 (0)
- 硬币数值和为奇数 → 阳 (1)

建议选择前者（3枚硬币 × 6次）更符合传统。

### 4.2 卦象生成

```
Line 1 (初爻) → Bit 0
Line 2 (二爻) → Bit 1
...
Line 6 (上爻) → Bit 5

Example: 111100 → 60号卦（坎）
```

**老爻检测** (Changing lines):
- 少阴 → 无变化
- 少阳 → 无变化
- 老阳 → 变为少阴，记录为变爻
- 老阴 → 变为少阳，记录为变爻

### 4.3 解读模板（分层结构）

**第一层 - 卦义库**
```
每个卦象 (1-64) 包含:
- 传统名称 (name)
- 象义描述 (meaning)
- 吉凶评价 (fortune)
- 应用场景关键词 (keywords)
```

**第二层 - 问题分类映射**
```
感情 → 关注"应爻态度、世爻主动性、互动趋势"
事业 → 关注"机会信号、阻力因素、发展空间"
财运 → 关注"进财机制、成本压力、收益周期"
合作 → 关注"双方匹配、谈判难点、成局概率"
学业 → 关注"学习进度、理解深度、考试机会"
```

**第三层 - 动爻与趋势判断**
```
动爻位置 + 本卦 + 变卦 → 输出"顺/逆、快/慢、需调整"等判断
```

---

## 5. 数据模型

### 5.1 核心表结构

#### `divinations` 表
```sql
CREATE TABLE divinations (
  id UUID PRIMARY KEY,
  user_id UUID (nullable for MVP),
  question TEXT NOT NULL,
  category VARCHAR(50),
  timeframe VARCHAR(50),
  notes TEXT,
  language VARCHAR(10) DEFAULT 'zh-CN',
  original_hexagram_number INT (1-64),
  changing_lines JSON (e.g., [1,3,5]),
  future_hexagram_number INT (1-64),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

#### `divination_lines` 表
```sql
CREATE TABLE divination_lines (
  id UUID PRIMARY KEY,
  divination_id UUID,
  line_number INT (1-6),
  result VARCHAR(20) ('少阴'|'少阳'|'老阴'|'老阳'),
  created_at TIMESTAMP
);
```

#### `hexagrams` 表 (缓存/参考)
```sql
CREATE TABLE hexagrams (
  id INT PRIMARY KEY (1-64),
  name VARCHAR(50),
  upper_trigram VARCHAR(50),
  lower_trigram VARCHAR(50),
  traditional_meaning TEXT,
  modern_interpretation TEXT
);
```

#### `interpretations` 表 (预存解读模板)
```sql
CREATE TABLE interpretation_templates (
  id UUID PRIMARY KEY,
  hexagram_number INT,
  category VARCHAR(50),
  language VARCHAR(10),
  template_text TEXT,  -- 包含占位符 {world}, {response}, etc
  created_at TIMESTAMP
);
```

---

## 6. 前端架构建议

### 6.1 页面结构

```
/                          → 首页
/ask                       → 提问页
/cast/:divination_id       → 起卦页
/result/:divination_id     → 结果页
/history                   → 历史记录 (需登录，MVP可选)
/rules                     → 规则说明页
/about                     → 关于我们
/faq                       → 常见问题
```

### 6.2 技术栈建议

- **框架**: React / Vue 3 / Next.js
- **样式**: Tailwind CSS / SCSS
- **状态管理**: Zustand / Pinia / Context API
- **HTTP客户端**: axios / fetch
- **动画**: Framer Motion / GreenSock (抛币动画)
- **图表**: 自定义SVG (卦象) 或 ECharts

### 6.3 关键组件

```
HexagramDisplay     → 卦象可视化
CoinAnimation       → 抛币动画
InterpretationCard  → 解读卡片
HistoryList         → 历史记录列表
```

---

## 7. 后端架构建议

### 7.1 技术栈

- **语言**: Python / Node.js / Go
- **框架**: FastAPI / Express / Flask / Gin
- **数据库**: PostgreSQL (主) + Redis (缓存)
- **部署**: Docker + K8s / 云服务 (AWS/GCP/阿里云)

### 7.2 项目结构

```
backend/
├── app/
│   ├── api/
│   │   ├── divinations.py     (起卦相关)
│   │   ├── hexagrams.py       (卦象查询)
│   │   └── rules.py           (规则说明)
│   ├── core/
│   │   ├── rules_engine.py    (核心规则引擎)
│   │   ├── hexagram_data.py   (卦象数据库)
│   │   └── templates.py       (解读模板)
│   ├── models/
│   │   └── divination.py      (数据模型)
│   └── main.py
├── tests/
├── requirements.txt
└── docker-compose.yml
```

---

## 8. 开发优先级与阶段

### Phase 1: MVP (Week 1-3)

**后端**:
- [ ] 实现爻象生成逻辑
- [ ] 建立卦象数据库 (64个卦)
- [ ] 实现核心3个API: create, cast, get_result
- [ ] 基础解读引擎 (卦义 + 分类映射)

**前端**:
- [ ] 首页
- [ ] 提问页 (表单)
- [ ] 起卦页 (抛币交互)
- [ ] 结果页 (解读展示)
- [ ] 响应式设计

**部署**:
- [ ] Docker化
- [ ] 单环境部署测试

---

### Phase 2: 完善 (Week 4-5)

- [ ] 历史记录页面
- [ ] 规则说明页详细内容
- [ ] 错误处理与边界情况
- [ ] 前端性能优化
- [ ] 基础测试覆盖

---

### Phase 3: 二期功能准备 (Week 6+)

- [ ] 用户认证系统
- [ ] 多语言i18n集成
- [ ] AI解读API集成点预留
- [ ] 会员系统框架

---

## 9. 关键数据：64卦对照表

| # | 名称 | 上卦 | 下卦 | 代码 |
|---|------|------|------|------|
| 1 | 乾 | 乾 | 乾 | 111111 |
| 2 | 坤 | 坤 | 坤 | 000000 |
| 3 | 屯 | 坎 | 艮 | 010001 |
| ... | ... | ... | ... | ... |
| 64 | 未济 | 离 | 坎 | 101010 |

*(完整表单存储在数据库或JSON文件)*

---

## 10. 多语言支持计划

**MVP阶段**: 仅中文简体 (zh-CN)

**二期支持**:
- 中文繁体 (zh-TW)
- English (en)
- 日本語 (ja) - optional

**方案**: i18n文件 + 后端模板国际化

---

## 11. API 使用示例流程

```
1. POST /api/divination/create
   请求: { "question": "这次换工作能成功吗？", "category": "事业" }
   响应: { "divination_id": "abc-123" }

2. POST /api/divination/abc-123/cast (×6)
   第1次请求: { "line_number": 1, "result": "少阳" }
   ...
   第6次请求: { "line_number": 6, "result": "老阳" }

3. GET /api/divination/abc-123/result
   响应: 完整解读 (见第3部分)
```

---

## 12. 免责声明与法律

页面必须包含:

> 本工具仅供传统文化研究、娱乐参考之用，不替代医疗、法律、金融等专业建议。使用本工具所得结果不构成任何决策依据。

---

## 附录：后端核心逻辑伪代码

### 起卦逻辑
```python
def generate_hexagram(line_results: List[str]) -> Dict:
    """
    Input: ['少阳', '少阴', '老阳', '少阳', '老阴', '少阳']
    Output: {
        'original': 60,  # 坎卦
        'changing_lines': [3, 5],
        'future': 29  # 坎卦
    }
    """
    # 1. 转换为二进制: 阳=1, 阴=0
    binary_str = ''.join('1' if '阳' in r else '0' for r in line_results)
    
    # 2. 从下到上读取 (反转)
    original_num = int(binary_str[::-1], 2)  # 1-64
    
    # 3. 检测老爻 (老阳/老阴)
    changing_lines = [i for i, r in enumerate(line_results) if '老' in r]
    
    # 4. 生成变卦 (反转老爻)
    future_binary = list(binary_str)
    for i in changing_lines:
        future_binary[i] = '0' if binary_str[i] == '1' else '1'
    future_num = int(''.join(future_binary)[::-1], 2)
    
    return {
        'original_hexagram': original_num,
        'changing_lines': [i+1 for i in changing_lines],  # 1-6而不是0-5
        'future_hexagram': future_num
    }

def interpret(original: int, changing_lines: List[int], future: int, category: str) -> Dict:
    """
    生成白话解读
    """
    original_meaning = HEXAGRAM_DB[original]['meaning']
    future_meaning = HEXAGRAM_DB[future]['meaning']
    
    # 根据分类调用相应模板
    template = get_template(category, original, changing_lines, future)
    
    # 填充占位符
    interpretation = template.format(
        world_status=extract_world_status(original),
        response_status=extract_response_status(original),
        trend=future_meaning
    )
    
    return {
        'summary': interpretation,
        'original_meaning': original_meaning,
        'future_trend': future_meaning,
        ...
    }
```

---

## 更新日志

- **v1.0** (2026-04-13): 初版 Spec，确定MVP功能范围与API设计

