def build_interpretation_prompt(ctx: dict) -> tuple[str, str]:
    base = ctx["base_hexagram_data"]
    changed = ctx["changed_hexagram_data"]
    changing_lines = ctx.get("changing_lines") or []
    has_changes = bool(changing_lines)

    system = (
        "你是一位精通《易经》六爻的专业解卦师，以白话文为用户解卦。\n"
        "请严格按照以下 JSON 格式返回解读，不得添加任何 Markdown 标记或额外文字：\n"
        "{\n"
        '  "summary": "总体解读（3-5句）",\n'
        '  "base_reading": "本卦详细解读",\n'
        '  "changing_lines_analysis": "动爻逐爻分析（无动爻时填空字符串）",\n'
        '  "changed_hexagram_trend": "变卦趋势（无动爻时填空字符串）",\n'
        f'  "category_advice": "针对【{ctx["category"]}】方向的具体建议",\n'
        '  "action_advice": ["行动建议一", "行动建议二", "行动建议三"]\n'
        "}"
    )

    line_desc = "\n".join(
        f"  第{l['line_number']}爻：{l['line_type']}{'（动爻）' if l['is_changing'] else ''}"
        for l in ctx.get("lines", [])
    )

    timeframe_note = f"（时间范围：{ctx['timeframe']}）" if ctx.get("timeframe") else ""
    changed_note = (
        f"变卦：{changed['name']}卦（{changed['meaning']}）"
        if changed
        else f"变卦：{base['name']}卦（与本卦相同，无动爻）"
    )
    changing_note = (
        f"动爻：第{'、'.join(str(l) for l in changing_lines)}爻"
        if has_changes
        else "动爻：无"
    )

    user = (
        f"问题：{ctx['question']}{timeframe_note}\n"
        f"关注方向：{ctx['category']}\n\n"
        f"本卦：{base['name']}卦（{base['meaning']}）\n"
        f"{changed_note}\n"
        f"{changing_note}\n\n"
        f"各爻情况：\n{line_desc}\n\n"
        "请给出完整的六爻白话解读。"
    )

    return system, user


def build_followup_prompt(ctx: dict, user_message: str) -> tuple[str, list[dict]]:
    base = ctx["base_hexagram_data"]
    changed = ctx["changed_hexagram_data"]
    base_name = base["name"]
    changed_name = changed["name"] if changed else base["name"]
    changing_lines = ctx.get("changing_lines") or []

    changing_note = (
        f"第{'、'.join(str(l) for l in changing_lines)}爻"
        if changing_lines
        else "无动爻"
    )

    system = (
        "你是一位精通《易经》六爻的专业解卦师。本次起卦记录：\n"
        f"- 问题：{ctx['question']}\n"
        f"- 关注方向：{ctx['category']}\n"
        f"- 本卦：《{base_name}》— {base['meaning']}\n"
        f"- 变卦：《{changed_name}》\n"
        f"- 动爻：{changing_note}\n\n"
        "你的所有回答必须严格基于本次卦象，不得偏离卦象语境作通用回答。\n"
        f"每次回答末尾须附注（固定格式）：「以上解读基于本次卦象：本卦《{base_name}》变《{changed_name}》」"
    )

    history = ctx.get("messages") or []
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": user_message})

    return system, messages
