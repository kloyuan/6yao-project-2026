# 六爻网站 - Spec Implementation v1.0

> 文档定位：将 Design 拆解为可执行的离散任务，明确每项任务的输入、输出与完成标准。  
> 上游依赖：SPEC_DESIGN.md（定义"如何构建"）  
> 下游产出：Execution Phase（按任务逐项交付、追踪进度）

---

## 约束条件（Constraints）

### 必须满足（Must）

- 沿用现有的 Next.js + FastAPI 架构
- 所有业务数据统一存储在 Supabase PostgreSQL 中
- Hexagram 参考数据以后端静态 JSON 文件存储，不进数据库
- 保持 RuleEngine 为确定性、无副作用的纯函数
- 每次提交单爻结果后，必须立即持久化
- 所有 Follow-up 消息必须绑定到某一次具体的起卦记录
- 每个页面（或页脚）必须展示法律免责声明

### 禁止事项（Must Not）

- 不得在前端计算爻象类型
- 不得让 Follow-up 退化为通用聊天机器人
- 不得改动 SPEC_REQUIREMENT FR-01 至 FR-05 所定义的核心 User Flow

### 本次不包含（Out of Scope）

- Redis
- TemplateFallback
- 多解读模式
- 用户认证
- 历史记录页
- 多语言支持
- SafetyCheck

### 当前状态（Current State）

| 项目 | 状态 |
|------|------|
| 前端 | Next.js |
| 后端 | FastAPI |
| 数据库 | Supabase PostgreSQL |
| 解读路径 | 仅 AI 解读 |
| 追问上限 | 20 轮 |

---

## 任务目录

### A. 后端实现

| Task | 说明 | 前置依赖 |
|------|------|---------|
| Task 1 — 环境配置与本地启动说明 | Supabase 连接、.env 变量说明（前后端）、LLM API Keys 配置、本地运行步骤 | 无 |
| Task 2 — 业务数据表结构初始化（DDL） | 建 Divination / DivinationLine / Interpretation / FollowupConversation / FollowupMessage 五张表，含索引 | Task 1 |
| Task 3 — Hexagram 静态参考数据文件 | 编写 64 卦 JSON，封装查询工具函数 | 无 |
| Task 4A — Implement core hexagram RuleEngine | CoinMapper（硬币→爻）、HexagramGen（爻→本卦 / 变卦）、动爻检测，含单元测试 | Task 3 |
| Task 4B — Implement NaJia and time context RuleEngine | NaJiaMapper（hexagram_id + line_number → branch / element）、TimeContextEngine（cast_datetime + timezone → 月建 / 日辰 / 旬空）、TimeStateCalculator（运行时派生 LineTimeState，不落库） | Task 3 |
| Task 5 — DivinationService 与起卦接口 | POST /divinations、POST /divinations/{id}/lines（首次抛币时记录 cast_datetime + timezone，服务端派生时间字段存库）、GET /divinations/{id}/result | Task 2、Task 4A、Task 4B |
| Task 6 — 解读共享能力实现（ContextLoader / PromptBuilder / LLMProvider） | ContextLoader（HexagramContext 含时间上下文 / ChatContext）、PromptBuilder（依赖 Task 4A/4B 输出结构）、LLMProvider（Claude 主 + DeepSeek 备用） | Task 2、Task 3、Task 4A、Task 4B |
| Task 7 — InterpretationService 与解读接口 | POST /divinations/{id}/interpret；LLM 不可用时返回错误 | Task 5、Task 6 |
| Task 8 — FollowupService 与追问接口 | ConversationManager（历史存取、20 轮计数）、POST /divinations/{id}/followup、GET /divinations/{id}/followup | Task 5、Task 6 |

### B. 前端实现

| Task | 说明 | 前置依赖 |
|------|------|---------|
| Task 9 — 前端：全局布局与法律免责声明 | 路由结构、页脚免责声明组件、响应式基础样式 | Task 1 |
| Task 10 — 前端：首页 | 平台介绍、立即起卦 CTA、了解六爻入口（FR-01） | Task 9 |
| Task 11 — 前端：提问页（FR-02） | 问题输入、分类选择、时间范围可选、提交至 POST /divinations | Task 9、Task 5 |
| Task 12 — 前端：起卦页（FR-03） | 6 次抛币交互、实时爻属性展示、起卦进度持久化、移动端触屏适配 | Task 11 |
| Task 13 — 前端：结果页（FR-04、FR-05） | 原始记录 + 本卦 + 变卦（盘面）、白话解读（LLM 失败时展示错误提示，盘面区块不受影响）、Follow-up 追问对话 | Task 9、Task 7、Task 8 |

### C. 联调与验证

| Task | 说明 | 前置依赖 |
|------|------|---------|
| Task 14 — 后端集成测试 | 覆盖全部 API 接口：起卦流程、解读、追问，含边界用例（无动爻、LLM 失败、达到追问上限） | Task 5、Task 7、Task 8 |
| Task 15 — 前后端联调与端到端验证 | 打通完整用户主流程（提问→起卦→盘面→解读→追问）；验证 FR-03 进度持久化、FR-04 URL 分享、FR-05 对话历史 | Task 14、Task 13 |

### D. P1 / 后续任务

| Task | 说明 | 前置依赖 |
|------|------|---------|
| Task P1-1 — 前端：规则说明页 | 六爻基本概念、三钱法映射规则可视化，面向零基础用户（FR-07） | Task 9 |

---

## 任务详情

### T1: Configure environment variables and local startup

**Dependencies:** None

**What:** 为前后端分别创建 `.env.example` 文件，列出所有必要变量（Supabase URL/key、Claude API key、DeepSeek API key、后端 API 地址）。示例文件只填占位值，不得提交真实 secrets。补充本地启动说明，涵盖前置依赖、安装步骤、前后端启动方式。

**Files:**
- `backend/.env.example`
- `frontend/.env.example`
- `.gitignore` — 确认 `.env` / `.env.local` 已排除
- `README.md` — 本地启动说明

**Tests:** N/A — 配置与文档任务，无自动化测试。

**Verify:**
- `backend/.env.example` 和 `frontend/.env.example` 存在，所有变量名已列出且填有占位值
- 将示例文件复制为 `.env` / `.env.local` 并填入真实值 → `uvicorn` 启动无报错，`GET /health` 返回 200
- `next dev` 启动无报错，`localhost:3000` 可访问
- 前端能连通后端：`NEXT_PUBLIC_API_URL` 正确配置 → 浏览器发出的请求命中 FastAPI，无 CORS 或连接错误

---

### T2: Initialize business database schema (DDL)

**Dependencies:** Task 1

**What:** 编写 DDL，创建 5 张业务表：`divinations`、`divination_lines`、`interpretations`、`followup_conversations`、`followup_messages`。包含主键、外键约束、枚举类型定义与常用查询字段的索引。字段定义与枚举约束须与 `SPEC_DESIGN.md` 第 4 章保持一致。`divinations` 表须包含时间上下文字段（`cast_datetime`、`timezone`、`month_branch`、`day_stem_branch`、`day_branch`、`void_branches`）；`divination_lines` 须包含纳甲字段（`branch`、`element`）。LineTimeState（`is_void` 等）为运行时派生，MVP 阶段**不落库**。将 migration 应用到 Supabase。

**Files:**
- `backend/migrations/001_create_tables.sql`

**Tests:**
- schema inspection：验证 5 张表的字段名、类型、可空性与 SPEC_DESIGN 4.1–4.5 一致
- foreign key validation：向 `divination_lines` 插入不存在的 `divination_id`，确认数据库报错
- enum constraint validation：向 `line_type` 插入非法值，确认被拒绝；`category` 同理
- index existence check：确认 `divination_lines.divination_id`、`interpretations.divination_id`、`followup_conversations.divination_id`、`followup_messages.conversation_id`、`divinations.session_token` 索引存在

**Verify:**
- `supabase db push`（或在 Supabase SQL editor 执行）无报错
- Supabase dashboard 中可见全部 5 张表及字段
- 手动插入一条 `divinations` 记录并查询回来，数据完整
- 在干净数据库环境中可从零完成 schema 初始化

---

### T3: Implement hexagram static data and lookup utilities

**Dependencies:** None

**What:** 编写包含 64 卦完整数据的 JSON 文件，字段按 `SPEC_DESIGN.md` 4.6 定义（`hexagram_id`、`name`、`trigrams`、`binary_code`、`palace`、`world_line`、`response_line`、`fortune_level`、`meaning`），并为每卦每爻补充纳甲映射数据（第 1–6 爻各自对应的地支 `branch` 与五行 `element`）。封装三个查询工具函数：按 `hexagram_id` 查询卦象、按 `binary_code` 查询卦象（供 HexagramGen 使用）、按 `hexagram_id + line_number` 查询纳甲地支（供 NaJiaMapper 使用）。JSON 文件在模块初始化时一次性加载，查询函数本身无 IO。

**Files:**
- `backend/data/hexagrams.json`
- `backend/app/core/hexagram_data.py`

**Tests:**
- data completeness：JSON 包含恰好 64 条记录，`hexagram_id` 覆盖 1–64 无重复无遗漏
- binary_code validity：64 个 `binary_code` 均为 6 位 `0/1` 字符串，且互不重复
- lookup by id：`get_hexagram_by_id(1)` 返回乾卦，`binary_code` 为 `"111111"`
- lookup by binary：`get_hexagram_by_binary("000000")` 返回坤卦
- invalid input：`get_hexagram_by_id(0)` 和 `get_hexagram_by_binary("999999")` 抛出明确异常

**Verify:**
- `pytest backend/tests/test_hexagram_data.py` 全部通过
- `python -c "from app.core.hexagram_data import get_hexagram_by_id; print(get_hexagram_by_id(1))"` 输出乾卦数据

---

### T4A: Implement core hexagram RuleEngine

**Dependencies:** Task 3

**What:** 实现 `CoinMapper`（硬币总和 → 爻类型）和 `HexagramGen`（6 爻 → 本卦 / 变卦）两个纯函数。`HexagramGen` 在模块初始化时从 Task 3 加载 binary_code 映射表，函数体内无 IO。输出字段：`base_hexagram`、`changed_hexagram`、`changing_lines`。

**Files:**
- `backend/app/core/rules_engine.py`
- `backend/tests/test_rules_engine.py`

**Tests:**
- coin mapping：`coin_sum` 6/7/8/9 分别映射到老阴/少阳/少阴/老阳，`is_changing` 正确
- invalid input：非法 `coin_sum` 抛出明确异常
- no changing lines：6 爻均为静爻 → `changed_hexagram == base_hexagram`，`changing_lines == []`
- with changing lines：含动爻 → `changed_hexagram` 正确，`changing_lines` 位置正确
- known case：6 爻全为老阳（9）→ `base_hexagram == 1`（乾卦）

**Verify:**
- `pytest backend/tests/test_rules_engine.py` 全部通过
- `RuleEngine` 函数无数据库调用、无文件 IO（可通过 mock 验证）

---

### T4B: Implement NaJia and time context RuleEngine

**Dependencies:** Task 3

**What:** 实现三个纯函数模块。`NaJiaMapper`：从 Task 3 加载纳甲映射表，按 (hexagram_id, line_number) 返回地支 `branch` 与五行 `element`。`TimeContextEngine`：接收 `cast_datetime`（ISO 8601）+ `timezone`，派生月建（`month_branch`）、日干支（`day_stem_branch`）、日辰（`day_branch`）、旬空（`void_branches`）。`TimeStateCalculator`：接收 `branch` + 时间上下文，计算 `LineTimeState`（`is_void`、`is_month_broken`、`is_day_clashed`、`is_day_combined`、`is_day_matched`、`is_secretly_moving`、`strength_by_month`、`time_triggers`）；所有计算为运行时派生，不写库。

**Files:**
- `backend/app/core/najia_engine.py`
- `backend/tests/test_najia_engine.py`

**Tests:**
- NaJiaMapper：已知卦象爻位返回正确地支（如乾卦初爻 → `子`）
- NaJiaMapper：非法 hexagram_id 或 line_number 抛出异常
- TimeContextEngine：给定 cast_datetime + timezone 返回正确月建、日辰、旬空
- TimeContextEngine：跨节气边界（节气当天）返回正确月建
- TimeStateCalculator：旬空爻 → `is_void == True`
- TimeStateCalculator：被日辰冲的静爻 → `is_secretly_moving == True`
- TimeStateCalculator：五行旺相休囚 → `strength_by_month` 值正确

**Verify:**
- `pytest backend/tests/test_najia_engine.py` 全部通过
- 全部函数无数据库调用、无文件 IO（可通过 mock 验证）
- LineTimeState 字段不出现在任何 DDL 或数据库写入路径中

---

### T5: Implement DivinationService and divination APIs

**Dependencies:** Task 2, Task 4

**What:** 实现 `DivinationService`，编排起卦流程。实现 3 个接口：`POST /divinations`（创建起卦记录，返回 `divination_id`）、`POST /divinations/{id}/lines`（提交单爻抛币结果，立即持久化，返回 `line_type` / `is_changing` / `branch` / `element`；第 1 爻请求须携带 `cast_datetime` 和 `timezone`，服务端调用 `TimeContextEngine` 派生时间字段并写入 `divinations` 表）、`GET /divinations/{id}/result`（返回完整盘面：`base_hexagram`、`changed_hexagram`、`changing_lines`、全部 6 条爻记录；每条爻附带运行时计算的 `LineTimeState`，不从数据库读取）。

**Files:**
- `backend/app/services/divination_service.py`
- `backend/app/api/divinations.py`
- `backend/tests/test_divination_api.py`

**Tests:**
- `POST /divinations`：合法请求创建记录，返回 `divination_id`
- `POST /divinations/{id}/lines`：提交合法 `coin_values`，返回正确 `line_type` / `is_changing`；行记录立即写入数据库
- `GET /divinations/{id}/result`：6 爻全部提交后返回完整盘面，`base_hexagram` 和 `changed_hexagram` 在 1–64 范围内
- `GET /divinations/{id}/result`：无动爻时 `changed_hexagram == base_hexagram`，`changing_lines == []`
- 无效 `divination_id` 返回 404

**Verify:**
- `pytest backend/tests/test_divination_api.py` 全部通过
- `POST /divinations/{id}/lines` 返回后，`divination_lines` 表中立即可查到对应行记录
- `GET /divinations/{id}/result` 返回结构符合 SPEC_DESIGN 3.1 接口定义

---

### T6: Implement Shared Components (ContextLoader / PromptBuilder / LLMProvider)

**Dependencies:** Task 2, Task 3, Task 4

**What:** 实现三个共享组件。`ContextLoader` 按调用方加载上下文：`HexagramContext`（供 InterpretationService 使用，含卦象元数据）、`ChatContext`（供 FollowupService 使用，含卦象 + 对话历史）。`PromptBuilder` 将 context 组装为 LLM system prompt + user message，prompt 中需包含本卦、变卦、动爻信息。`LLMProvider` 封装 Claude（主）和 DeepSeek（备用），Claude 失败时自动切换。

**Files:**
- `backend/app/core/context_loader.py`
- `backend/app/core/prompt_builder.py`
- `backend/app/core/llm_provider.py`
- `backend/tests/test_context_loader.py`
- `backend/tests/test_prompt_builder.py`

**Tests:**
- `HexagramContext`：包含 `base_hexagram`、`changed_hexagram`、`changing_lines` 及卦象元数据
- `ChatContext`：包含 `HexagramContext` 内容 + 对话历史列表
- `PromptBuilder`：system prompt 包含卦名和动爻信息，user message 非空
- `LLMProvider`：Claude 正常时返回响应；Claude 抛出异常时切换 DeepSeek 并返回响应

**Verify:**
- `pytest backend/tests/test_context_loader.py backend/tests/test_prompt_builder.py` 全部通过
- 手动调用 `PromptBuilder`，输出的 system prompt 中可见卦名和动爻位置

---

### T7: Implement InterpretationService and interpretation API

**Dependencies:** Task 5, Task 6

**What:** 实现 `InterpretationService`。`POST /divinations/{id}/interpret` 通过 `ContextLoader` 加载卦象上下文，经 `PromptBuilder` 组装 prompt 后调用 `LLMProvider` 生成解读，将结果持久化到 `interpretations` 表并返回。LLM 不可用时返回可读错误信息，不做模板兜底。每次起卦对应一条解读记录，重复调用返回已有结果。

**Files:**
- `backend/app/services/interpretation_service.py`
- `backend/app/api/interpretations.py`
- `backend/tests/test_interpretation_api.py`

**Tests:**
- LLM 成功：响应包含 `summary`、`base_reading`、`changing_lines_analysis`、`changed_hexagram_trend`、`category_advice`、`action_advice` 全部字段
- LLM 失败：返回用户可读的错误响应（非 500 / 非未处理异常）
- 重复调用：返回已有解读记录，不重复生成
- 无效 `divination_id`：返回 404

**Verify:**
- `pytest backend/tests/test_interpretation_api.py` 全部通过
- 成功调用后 `interpretations` 表中存在对应记录
- LLM 失败场景返回的错误信息对用户友好，包含提示文案

---

### T8: Implement FollowupService and followup APIs

**Dependencies:** Task 5, Task 6

**What:** 实现 `FollowupService` 与 `ConversationManager`。`POST /divinations/{id}/followup`：首次调用时创建 `FollowupConversation` 记录；将用户消息写入 `followup_messages`；通过 `ContextLoader` 加载 `ChatContext`（卦象 + 对话历史）；调用 `LLMProvider` 生成回复；将 assistant 消息写入表，`rounds_used` 加 1；返回回复内容。每条 assistant 回复须附注来源标注。超过 20 轮后拒绝新请求。`GET /divinations/{id}/followup` 返回完整对话历史。

**Files:**
- `backend/app/services/followup_service.py`
- `backend/app/core/conversation_manager.py`
- `backend/app/api/followup.py`
- `backend/tests/test_followup_api.py`

**Tests:**
- 首次追问：创建 `FollowupConversation`，`rounds_used` 从 0 变为 1
- 连续追问：`rounds_used` 随每轮递增
- 第 20 轮：正常返回回复，`rounds_used == 20`
- 第 21 轮：请求被拒绝，返回上限提示（4xx）
- `GET /followup`：消息按时间顺序返回，user / assistant 交替出现
- `GET /followup`：追问尚未开始时返回空列表（不返回 404）
- assistant 回复包含来源标注（含本卦 / 变卦卦名）

**Verify:**
- `pytest backend/tests/test_followup_api.py` 全部通过
- `POST /followup` 后 `followup_messages` 表中同时存在 user 和 assistant 两条消息
- 第 21 轮请求返回 4xx 状态码及可读提示文案

---

### T9: Build frontend global layout and legal disclaimer

**Dependencies:** Task 1

**What:** 搭建 Next.js 路由结构，创建全局 `layout.tsx`，在页脚放置法律免责声明组件。建立响应式基础样式，支持移动端（< 768px）、平板（768–1023px）、桌面（≥ 1024px）三个断点。

**Files:**
- `frontend/app/layout.tsx`
- `frontend/components/Footer.tsx`
- `frontend/styles/globals.css`

**Tests:**
- 法律免责声明文本与 SPEC_REQUIREMENT 第 6 章一致
- 三个断点下布局无溢出、无错位

**Verify:**
- 访问任意页面，页脚免责声明可见
- 移动端（375px）和桌面（1440px）视口下页面布局正常

---

### T10: Build homepage

**Dependencies:** Task 9

**What:** 实现首页，包含平台名称与简介、"立即起卦" CTA 按钮（跳转提问页）、"了解六爻"入口（跳转规则说明页）、3 步以内的使用流程说明（FR-01）。

**Files:**
- `frontend/app/page.tsx`

**Tests:**
- "立即起卦" 按钮跳转到 `/question`
- "了解六爻" 入口存在且可点击
- 使用流程说明不超过 3 步

**Verify:**
- 点击 "立即起卦" 跳转至 `/question`
- 页面在移动端和桌面端均正常渲染

---

### T11: Build question page (FR-02)

**Dependencies:** Task 9, Task 5

**What:** 实现提问页，包含问题文本输入（必填）、分类选择器（8 个选项，默认"其他"）、时间范围可选下拉（FR-02）。提交时调用 `POST /divinations`，成功后跳转至起卦页 `/divination/{id}`。

**Files:**
- `frontend/app/question/page.tsx`
- `frontend/components/QuestionForm.tsx`

**Tests:**
- 问题文本为空时提交按钮不可用
- 分类默认选中"其他"
- 提交成功后跳转至 `/divination/{id}`，URL 含真实 `divination_id`

**Verify:**
- 空问题无法提交
- 提交后 `divinations` 表中存在新记录
- 跳转目标 URL 含正确 `divination_id`

---

### T12: Build divination page (FR-03)

**Dependencies:** Task 11

**What:** 实现起卦页，逐爻引导用户完成 6 次抛掷。用户点击按钮随机生成三枚硬币结果，立即展示该爻属性（老阴 / 少阳 / 少阴 / 老阳）并更新进度（如"第 3 爻 / 共 6 爻"）。用户不可跳过或修改已完成的爻。每次抛掷完成后调用 `POST /divinations/{id}/lines` 持久化；**第 1 爻请求须同时携带 `cast_datetime`（抛币时刻的客户端 ISO 8601 时间戳）和 `timezone`（`Intl.DateTimeFormat().resolvedOptions().timeZone`）**。页面刷新后已完成爻从服务端恢复。第 6 爻提交后跳转至结果页。

**Files:**
- `frontend/app/divination/[id]/page.tsx`
- `frontend/components/CoinThrow.tsx`
- `frontend/components/LineDisplay.tsx`

**Tests:**
- 进度指示器随每次抛掷更新
- 抛掷后立即显示爻属性
- 已完成的爻展示只读，不可修改
- 刷新页面后已完成爻恢复，从下一爻继续
- 第 6 爻提交后跳转至 `/result/{id}`

**Verify:**
- 完成第 3 爻后刷新页面，前 3 爻记录可见，当前步骤为第 4 爻
- 第 6 爻提交后自动跳转结果页

---

### T13: Build result page (FR-04, FR-05)

**Dependencies:** Task 9, Task 7, Task 8

**What:** 实现结果页，包含四个区块：原始抛掷记录、本卦展示、变卦展示（无动爻时隐藏并显示提示语）、白话解读。解读区块独立加载，LLM 失败时展示错误提示，前三个区块不受影响。解读加载完成后，下方展示 Follow-up 追问对话；每条 assistant 回复附注来源标注；达到 20 轮后输入框禁用并显示上限提示。结果页 URL 含 `divination_id`，可通过链接直接访问。

**Files:**
- `frontend/app/result/[id]/page.tsx`
- `frontend/components/ThrowRecord.tsx`
- `frontend/components/HexagramDisplay.tsx`
- `frontend/components/InterpretationPanel.tsx`
- `frontend/components/FollowupChat.tsx`

**Tests:**
- 正常路径：四个区块均渲染完成
- 错误状态：模拟 LLM 失败 → 前三个区块正常，解读区块显示错误提示
- 无动爻：变卦区块隐藏，显示"本次无动爻，卦象稳定，变卦与本卦一致"
- Follow-up：发送追问后显示 assistant 回复及来源标注
- 第 20 轮后输入框禁用
- 刷新页面后对话历史可见

**Verify:**
- 在另一浏览器 tab 打开结果页 URL，四个区块正常加载
- LLM 失败时页面不崩溃，解读区块显示错误提示，其余区块不受影响
- Follow-up 对话在刷新后仍可见

---

### T14: Implement backend integration tests

**Dependencies:** Task 5, Task 7, Task 8

**What:** 编写覆盖全部后端 API 接口的集成测试，使用真实数据库（测试环境 Supabase 或本地 PostgreSQL）。覆盖正常路径与边界用例。

**Files:**
- `backend/tests/test_integration.py`

**Tests:**
- 完整起卦流程：`POST /divinations` → 6 次 `POST /lines` → `GET /result`，数据完整
- 无动爻场景：`changed_hexagram == base_hexagram`，`changing_lines == []`
- 解读正常路径：`POST /interpret` 返回完整解读字段
- 解读 LLM 失败：返回用户可读错误，不抛出 500
- 追问达到 20 轮：第 20 轮正常，第 21 轮返回 4xx
- 无效 ID：各接口返回 404

**Verify:**
- `pytest backend/tests/test_integration.py` 全部通过
- 测试运行后数据库无残留脏数据（测试数据已清理）

---

### T15: Verify end-to-end user flow

**Dependencies:** Task 13, Task 14

**What:** 在本地环境联调前后端，走通完整用户主流程。验证各持久化与分享场景是否符合 SPEC_REQUIREMENT 验收标准。

**Files:** 无新增文件，修复联调中发现的 bug。

**Tests:**
- 完整主流程：提问 → 起卦 → 盘面 → 解读 → 追问，全程无报错
- 进度持久化：起卦到第 4 爻时刷新页面，进度恢复，从第 5 爻继续
- URL 分享：复制结果页 URL 在新 tab 打开，四个区块正常加载
- 对话历史：追问 3 轮后刷新，历史消息可见

**Verify:**
- 上述 4 个场景均手动验证通过
- 浏览器 console 无未处理报错
- 移动端（375px）主流程可正常操作

---

### T P1-1: Build rules explanation page (FR-07)

**Dependencies:** Task 9

**What:** 实现规则说明页，面向零基础用户介绍六爻基本概念（什么是六爻、为什么用三枚硬币、如何看卦）。包含三钱法硬币→爻映射规则的可视化说明（对应 SPEC_REQUIREMENT BR-01、BR-02）。首页"了解六爻"入口指向本页。

**Files:**
- `frontend/app/rules/page.tsx`

**Tests:**
- 三钱法映射表展示正确（6→老阴、7→少阳、8→少阴、9→老阳）
- 首页"了解六爻"链接跳转至本页

**Verify:**
- 点击首页"了解六爻"成功进入规则说明页
- 映射规则与 SPEC_REQUIREMENT BR-01、BR-02 一致
- 页面在移动端和桌面端均正常渲染

---

## 更新日志

- **v1.1** (2026-04-30)：响应 SPEC_REQUIREMENT v1.5 / SPEC_DESIGN v1.2；T4 拆为 T4A（核心卦象）和 T4B（纳甲 + 时间上下文）；T2 DDL 新增时间字段与纳甲字段（LineTimeState 不落库）；T3 纳甲数据补充；T5 DivinationService 新增 cast_datetime/timezone 捕获；T12 起卦页新增时间字段采集
- **v1.0** (2026-04-26)：初版 Implementation Spec，确定约束条件与任务目录（A/B/C/D 四组，共 15 个 MVP Task + 1 个 P1 Task）
