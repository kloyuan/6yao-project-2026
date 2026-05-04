"""
T4B: NaJia + Time Context RuleEngine
Pure functions, no IO. All calculations are deterministic.
"""
from __future__ import annotations

import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# ─── Branch / Stem constants ──────────────────────────────────────────────────

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

BRANCH_INDEX = {b: i for i, b in enumerate(BRANCHES)}

BRANCH_ELEMENT = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

# Clash: each branch clashes with the one 6 positions away
CLASH_MAP = {b: BRANCHES[(i + 6) % 12] for i, b in enumerate(BRANCHES)}

# Six harmonies (六合)
SIX_COMBINE = {
    "子": "丑", "丑": "子",
    "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯",
    "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳",
    "午": "未", "未": "午",
}

# Five element generation and control
_GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
_CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# ─── NaJia (纳甲) mapping ─────────────────────────────────────────────────────
# Jing Fang tradition: each trigram name → list of 3 branches for lines 1-3 (lower)
# or lines 4-6 (upper), indexed as [line4_branch, line5_branch, line6_branch]

_LOWER_NAJIA: dict[str, list[str]] = {
    "乾": ["子", "寅", "辰"],
    "坤": ["未", "巳", "卯"],
    "震": ["子", "寅", "辰"],
    "巽": ["丑", "亥", "酉"],
    "坎": ["寅", "子", "戌"],
    "离": ["卯", "丑", "亥"],
    "艮": ["寅", "子", "戌"],
    "兑": ["巳", "卯", "丑"],
}

_UPPER_NAJIA: dict[str, list[str]] = {
    "乾": ["午", "申", "戌"],
    "坤": ["丑", "亥", "酉"],
    "震": ["戌", "申", "午"],
    "巽": ["卯", "巳", "未"],
    "坎": ["申", "午", "辰"],
    "离": ["酉", "未", "巳"],
    "艮": ["申", "午", "辰"],
    "兑": ["亥", "酉", "未"],
}


def get_najia(trigrams: list[str], line_number: int) -> tuple[str, str]:
    """
    Return (branch, element) for a given line of a hexagram.
    trigrams = [upper_trigram_name, lower_trigram_name] (as stored in hexagrams.json)
    line_number: 1-6 (1=bottom, 6=top)
    """
    if not 1 <= line_number <= 6:
        raise ValueError(f"line_number must be 1-6, got {line_number}")
    upper_name, lower_name = trigrams[0], trigrams[1]
    if line_number <= 3:
        branch = _LOWER_NAJIA[lower_name][line_number - 1]
    else:
        branch = _UPPER_NAJIA[upper_name][line_number - 4]
    return branch, BRANCH_ELEMENT[branch]


# ─── Ganzhi (干支) day calculation ───────────────────────────────────────────
# Reference: 2000-01-01 = 甲戌日 = cycle index 10
_REF_DATE = datetime.date(2000, 1, 1)
_REF_INDEX = 10  # 甲戌 in the 60-cycle (甲子=0)


def _date_to_ganzhi_index(date: datetime.date) -> int:
    days_diff = (date - _REF_DATE).days
    return (days_diff + _REF_INDEX) % 60


def _ganzhi_index_to_stem_branch(index: int) -> tuple[str, str]:
    return STEMS[index % 10], BRANCHES[index % 12]


# ─── Solar term (节气) month branch table ────────────────────────────────────
# Approximate dates; accurate to ±1-2 days for years 2000-2050.
# Format: (month, day) is the approximate start date of the new 月建.
_JIEQI: list[tuple[tuple[int, int], str]] = [
    ((1, 1), "子"),   # continuing from 大雪
    ((1, 6), "丑"),   # 小寒
    ((2, 4), "寅"),   # 立春
    ((3, 6), "卯"),   # 惊蛰
    ((4, 5), "辰"),   # 清明
    ((5, 6), "巳"),   # 立夏
    ((6, 6), "午"),   # 芒种
    ((7, 7), "未"),   # 小暑
    ((8, 7), "申"),   # 立秋
    ((9, 8), "酉"),   # 白露
    ((10, 8), "戌"),  # 寒露
    ((11, 7), "亥"),  # 立冬
    ((12, 7), "子"),  # 大雪
]


def _get_month_branch(date: datetime.date) -> str:
    current = "子"
    key = (date.month, date.day)
    for (m, d), branch in _JIEQI:
        if key >= (m, d):
            current = branch
    return current


# ─── Public API ───────────────────────────────────────────────────────────────

def compute_time_context(cast_datetime: str, timezone: str) -> dict:
    """
    TimeContextEngine: derive 月建 / 日干支 / 旬空 from ISO 8601 datetime + IANA timezone.
    Returns:
        month_branch:    str  e.g. "寅"
        day_stem_branch: str  e.g. "甲子"
        day_branch:      str  e.g. "子"
        void_branches:   list[str]  e.g. ["戌", "亥"]
    """
    try:
        tz = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, Exception):
        tz = ZoneInfo("UTC")

    dt = datetime.datetime.fromisoformat(cast_datetime)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    local_dt = dt.astimezone(tz)
    local_date = local_dt.date()

    idx = _date_to_ganzhi_index(local_date)
    stem, branch = _ganzhi_index_to_stem_branch(idx)

    # 旬空: the decade (旬) starts at floor(idx/10)*10; its last branch index
    decade_start = (idx // 10) * 10
    start_branch_idx = decade_start % 12
    end_branch_idx = (start_branch_idx + 9) % 12
    void1 = BRANCHES[(end_branch_idx + 1) % 12]
    void2 = BRANCHES[(end_branch_idx + 2) % 12]

    return {
        "month_branch": _get_month_branch(local_date),
        "day_stem_branch": stem + branch,
        "day_branch": branch,
        "void_branches": [void1, void2],
    }


def compute_line_time_state(
    branch: str,
    month_branch: str,
    day_branch: str,
    void_branches: list[str],
    is_changing: bool,
) -> dict:
    """
    TimeStateCalculator: derive LineTimeState fields at runtime.
    All inputs are Earthly Branch strings (地支).
    """
    line_element = BRANCH_ELEMENT[branch]
    month_element = BRANCH_ELEMENT[month_branch]

    is_void = branch in void_branches
    is_month_broken = CLASH_MAP.get(branch) == month_branch
    is_day_clashed = CLASH_MAP.get(branch) == day_branch
    is_day_combined = SIX_COMBINE.get(branch) == day_branch
    is_day_matched = branch == day_branch
    # 暗动: static line clashed by day branch
    is_secretly_moving = (not is_changing) and is_day_clashed

    # 旺相休囚死
    if line_element == month_element:
        strength = "旺"
    elif _GENERATES.get(month_element) == line_element:
        strength = "相"
    elif _GENERATES.get(line_element) == month_element:
        strength = "休"
    elif _CONTROLS.get(line_element) == month_element:
        strength = "囚"
    else:
        strength = "死"

    # Build time_triggers hints
    triggers: list[str] = []
    if is_void:
        clash_of_void = CLASH_MAP.get(branch)
        triggers.append(f"出空之日（{branch}出空）")
        if clash_of_void:
            triggers.append(f"冲空之日（逢{clash_of_void}）")
    if is_month_broken:
        triggers.append("月破，力量受损")
    if is_secretly_moving:
        triggers.append("暗动（被日辰冲）")

    return {
        "branch": branch,
        "element": line_element,
        "is_void": is_void,
        "is_month_broken": is_month_broken,
        "is_day_clashed": is_day_clashed,
        "is_day_combined": is_day_combined,
        "is_day_matched": is_day_matched,
        "is_secretly_moving": is_secretly_moving,
        "strength_by_month": strength,
        "time_triggers": triggers,
    }
