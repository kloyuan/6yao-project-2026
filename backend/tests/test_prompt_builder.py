from app.core.prompt_builder import build_interpretation_prompt, build_followup_prompt
from app.core.hexagram_data import get_hexagram_by_id


def _make_ctx(changing_lines=None):
    base = get_hexagram_by_id(1)   # 乾
    changed = get_hexagram_by_id(2) if changing_lines else None
    return {
        "question": "工作是否顺利？",
        "category": "事业",
        "timeframe": None,
        "base_hexagram": 1,
        "changed_hexagram": 2 if changing_lines else 1,
        "changing_lines": changing_lines or [],
        "base_hexagram_data": base,
        "changed_hexagram_data": changed,
        "lines": [
            {"line_number": i, "line_type": "少阳", "is_changing": False}
            for i in range(1, 7)
        ],
    }


def test_interpretation_system_prompt_has_json_schema():
    system, _ = build_interpretation_prompt(_make_ctx())
    assert "summary" in system
    assert "base_reading" in system
    assert "action_advice" in system


def test_interpretation_user_message_contains_hexagram_name():
    system, user = build_interpretation_prompt(_make_ctx())
    assert "乾" in system or "乾" in user
    assert len(user) > 0


def test_interpretation_prompt_no_changing_lines():
    system, user = build_interpretation_prompt(_make_ctx(changing_lines=[]))
    assert "无动爻" in user


def test_interpretation_prompt_with_changing_lines():
    _, user = build_interpretation_prompt(_make_ctx(changing_lines=[1, 3]))
    assert "1" in user
    assert "3" in user


def test_followup_prompt_system_contains_hexagram():
    ctx = _make_ctx()
    ctx["messages"] = []
    system, messages = build_followup_prompt(ctx, "我该怎么做？")
    assert "乾" in system
    assert "以上解读基于本次卦象" in system


def test_followup_prompt_includes_user_message():
    ctx = _make_ctx()
    ctx["messages"] = []
    _, messages = build_followup_prompt(ctx, "具体分析一下？")
    assert messages[-1]["role"] == "user"
    assert "具体分析" in messages[-1]["content"]


def test_followup_prompt_includes_history():
    ctx = _make_ctx()
    ctx["messages"] = [
        {"role": "user", "content": "第一个问题"},
        {"role": "assistant", "content": "第一个回答"},
    ]
    _, messages = build_followup_prompt(ctx, "继续追问")
    assert len(messages) == 3
    assert messages[0]["content"] == "第一个问题"
