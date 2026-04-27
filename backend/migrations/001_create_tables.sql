-- ============================================================
-- 001_create_tables.sql
-- 六爻平台业务表结构初始化（幂等，可重复执行）
-- ============================================================

-- ─── Enum 类型 ───────────────────────────────────────────────

DO $$ BEGIN
  CREATE TYPE category_type AS ENUM (
    '感情', '事业', '财运', '学业', '合作', '健康', '寻物', '其他'
  );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE line_type AS ENUM ('老阴', '少阳', '少阴', '老阳');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE generated_by_type AS ENUM ('ai');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE message_role AS ENUM ('user', 'assistant');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ─── 4.1 divinations（起卦记录）────────────────────────────────

CREATE TABLE IF NOT EXISTS divinations (
  id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  question          TEXT        NOT NULL,
  category          category_type NOT NULL,
  timeframe         TEXT,
  session_token     TEXT        NOT NULL,
  base_hexagram     INTEGER     CHECK (base_hexagram BETWEEN 1 AND 64),
  changed_hexagram  INTEGER     CHECK (changed_hexagram BETWEEN 1 AND 64),
  changing_lines    INTEGER[]   NOT NULL DEFAULT '{}',
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_divinations_session_token
  ON divinations (session_token);

-- ─── 4.2 divination_lines（单爻记录）───────────────────────────

CREATE TABLE IF NOT EXISTS divination_lines (
  id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  divination_id  UUID        NOT NULL REFERENCES divinations (id) ON DELETE CASCADE,
  line_number    INTEGER     NOT NULL CHECK (line_number BETWEEN 1 AND 6),
  coin_values    INTEGER[]   NOT NULL,
  coin_sum       INTEGER     NOT NULL CHECK (coin_sum IN (6, 7, 8, 9)),
  line_type      line_type   NOT NULL,
  is_changing    BOOLEAN     NOT NULL,
  UNIQUE (divination_id, line_number)
);

CREATE INDEX IF NOT EXISTS idx_divination_lines_divination_id
  ON divination_lines (divination_id);

-- ─── 4.3 interpretations（解读结果）────────────────────────────

CREATE TABLE IF NOT EXISTS interpretations (
  id                      UUID               PRIMARY KEY DEFAULT gen_random_uuid(),
  divination_id           UUID               NOT NULL UNIQUE
                                             REFERENCES divinations (id) ON DELETE CASCADE,
  language                VARCHAR(10)        NOT NULL DEFAULT 'zh-CN',
  summary                 TEXT,
  base_reading            TEXT,
  changing_lines_analysis TEXT,
  changed_hexagram_trend  TEXT,
  category_advice         TEXT,
  action_advice           TEXT[],
  generated_by            generated_by_type  NOT NULL DEFAULT 'ai',
  provider                VARCHAR(50),
  created_at              TIMESTAMPTZ        NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_interpretations_divination_id
  ON interpretations (divination_id);

-- ─── 4.4 followup_conversations（追问对话）─────────────────────

CREATE TABLE IF NOT EXISTS followup_conversations (
  id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  divination_id  UUID        NOT NULL UNIQUE
                             REFERENCES divinations (id) ON DELETE CASCADE,
  rounds_used    INTEGER     NOT NULL DEFAULT 0 CHECK (rounds_used >= 0),
  rounds_limit   INTEGER     NOT NULL DEFAULT 20,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_followup_conversations_divination_id
  ON followup_conversations (divination_id);

-- ─── 4.5 followup_messages（追问消息）─────────────────────────

CREATE TABLE IF NOT EXISTS followup_messages (
  id               UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id  UUID          NOT NULL
                                 REFERENCES followup_conversations (id) ON DELETE CASCADE,
  role             message_role  NOT NULL,
  content          TEXT          NOT NULL,
  created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_followup_messages_conversation_id
  ON followup_messages (conversation_id);
