def build_interpretation_prompt(ctx: dict) -> tuple[str, str]:
    base = ctx["base_hexagram_data"]
    changed = ctx["changed_hexagram_data"]
    changing_lines = ctx.get("changing_lines") or []
    has_changes = bool(changing_lines)

    category = ctx["category"]

    system = (
        "你是一位精通《易经》六爻的解卦师，同时也是一位有温度的倾听者。\n"
        "你的解读遵循「双层表达」原则：专业卦象依据须清晰呈现，同时将卦意落到问卦者的实际处境。\n"
        "注意边界：\n"
        "- 不使用恐吓、宿命、诅咒式表达。\n"
        "- 涉及健康、法律、投资等高风险问题时，应提醒用户结合专业意见。\n"
        "- 涉及他人内心、忠诚、爱意、背叛等问题时，避免替他人下绝对道德判断。\n\n"
        "请严格按照以下 JSON 格式返回解读，不得添加任何 Markdown 标记或额外文字：\n"
        "{\n"
        '  "summary": "先用1-2句回应用户的情绪或处境；再说明本卦名、动爻位置、变卦名；最后用温和语言概括总体趋势",\n'
        '  "base_reading": "先解释本卦卦象结构（上下卦、象义）；再给出六爻专业依据；最后用白话翻译映射到用户处境",\n'
        '  "changing_lines_analysis": "动爻逐爻分析（无动爻时填空字符串）",\n'
        '  "changed_hexagram_trend": "变卦趋势（无动爻时填空字符串）",\n'
        f'  "category_advice": "结合卦象依据，将卦意落到用户的【{category}】处境中，给出有针对性的分析",\n'
        '  "action_advice": ["根据卦象趋势给出3-4条具体行动方向"]\n'
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

    # Time context block
    time_parts = []
    if ctx.get("month_branch"):
        time_parts.append(f"月建：{ctx['month_branch']}（当月地支）")
    if ctx.get("day_stem_branch"):
        time_parts.append(f"日辰：{ctx['day_stem_branch']}")
    if ctx.get("void_branches"):
        time_parts.append(f"旬空：{'、'.join(ctx['void_branches'])}")
    time_note = "\n".join(time_parts)

    user = (
        f"问题：{ctx['question']}{timeframe_note}\n"
        f"关注方向：{ctx['category']}\n\n"
        f"本卦：{base['name']}卦（{base['meaning']}）\n"
        f"{changed_note}\n"
        f"{changing_note}\n\n"
        f"各爻情况：\n{line_desc}\n\n"
        + (f"起卦时间背景：\n{time_note}\n\n" if time_note else "")
        + "此人正在认真思考这个问题，请结合卦象给出有依据、有温度的解读。"
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
        "你是一位精通《易经》六爻的解卦师，同时也是一位有温度的倾听者。本次起卦记录：\n"
        f"- 问题：{ctx['question']}\n"
        f"- 关注方向：{ctx['category']}\n"
        f"- 本卦：《{base_name}》— {base['meaning']}\n"
        f"- 变卦：《{changed_name}》\n"
        f"- 动爻：{changing_note}\n\n"
        "回答要求：\n"
        "- 所有回答须严格基于本次卦象，不得作脱离卦象的通用回答。\n"
        "- 先回应用户问题的实质，再给出卦象依据；语气温和。\n"
        "- 不使用恐吓、宿命、诅咒式表达。\n"
        f"每次回答末尾须附注（固定格式）：「以上解读基于本次卦象：本卦《{base_name}》变《{changed_name}》」"
    )

    history = ctx.get("messages") or []
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": user_message})

    return system, messages
