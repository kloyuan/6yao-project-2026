# 六爻在线起卦与解读平台

六爻（Liu Yao）是一种基于《易经》的占卜体系。本平台将传统三钱起卦流程数字化，提供结构化白话解读与 Follow-up 追问能力。

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Next.js 14 (App Router) |
| 后端 | FastAPI (Python 3.11+) |
| 数据库 | Supabase PostgreSQL |
| 主 LLM | Claude (Anthropic) |
| 备用 LLM | DeepSeek |

---

## 前置依赖

- Node.js >= 18
- Python >= 3.11
- [uv](https://github.com/astral-sh/uv) 或 pip（后端包管理）
- Supabase 项目（免费 tier 可用）
- Anthropic API key
- DeepSeek API key（可选，用于 LLM 备用）

---

## 本地启动

### 1. 克隆仓库

```bash
git clone <repo-url>
cd 6yao-project-2026
```

### 2. 配置环境变量

**后端**

```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入真实的 Supabase URL、API keys
```

**前端**

```bash
cp frontend/.env.example frontend/.env.local
# 编辑 frontend/.env.local，填入 NEXT_PUBLIC_API_URL 与 Supabase 公开 key
```

### 3. 初始化数据库

在 Supabase SQL Editor 中执行：

```bash
# 复制并执行以下文件内容
backend/migrations/001_create_tables.sql
```

### 4. 启动后端

```bash
cd backend

# 安装依赖（首次）
pip install -r requirements.txt
# 或使用 uv：uv sync

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

后端健康检查：`GET http://localhost:8000/health` 应返回 `{"status": "ok"}`

### 5. 启动前端

```bash
cd frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

前端访问：`http://localhost:3000`

---

## 验证联调

1. 浏览器打开 `http://localhost:3000`
2. 点击「立即起卦」，填写问题并提交
3. 完成 6 次抛掷后查看结果页
4. 在结果页追问

浏览器 Network 面板中，对 `localhost:8000` 的请求应返回 2xx，无 CORS 报错。

---

## 目录结构

```
6yao-project-2026/
├── backend/               # FastAPI 应用
│   ├── app/
│   │   ├── api/           # 路由层
│   │   ├── core/          # RuleEngine、LLMProvider、ContextLoader 等
│   │   ├── services/      # DivinationService、InterpretationService、FollowupService
│   │   └── main.py
│   ├── data/
│   │   └── hexagrams.json # 64 卦静态参考数据
│   ├── migrations/
│   │   └── 001_create_tables.sql
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── frontend/              # Next.js 应用
│   ├── app/               # App Router 页面
│   ├── components/
│   ├── styles/
│   ├── .env.example
│   └── package.json
└── specs/                 # 产品与技术规范文档
```

---

## 免责声明

本平台提供的六爻解读内容仅供娱乐与参考，不构成任何法律、医疗、财务或其他专业建议。使用者应自行判断并承担相关决策的责任。
