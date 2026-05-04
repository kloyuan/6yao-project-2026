-- ============================================================
-- 002_add_time_fields.sql
-- 新增时间上下文字段与纳甲字段（幂等，可重复执行）
-- ============================================================

-- ─── divinations 表：新增时间上下文字段 ────────────────────────

ALTER TABLE divinations
  ADD COLUMN IF NOT EXISTS cast_datetime   TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS timezone        VARCHAR(100),
  ADD COLUMN IF NOT EXISTS month_branch    VARCHAR(2),
  ADD COLUMN IF NOT EXISTS day_stem_branch VARCHAR(4),
  ADD COLUMN IF NOT EXISTS day_branch      VARCHAR(2),
  ADD COLUMN IF NOT EXISTS void_branches   VARCHAR(2)[];

-- ─── divination_lines 表：新增纳甲字段 ────────────────────────

ALTER TABLE divination_lines
  ADD COLUMN IF NOT EXISTS branch  VARCHAR(2),
  ADD COLUMN IF NOT EXISTS element VARCHAR(2);
