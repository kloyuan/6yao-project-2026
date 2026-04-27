import json
from pathlib import Path
from typing import Dict

_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "hexagrams.json"


def _load() -> tuple[Dict[int, dict], Dict[str, dict]]:
    with open(_DATA_PATH, encoding="utf-8") as f:
        records = json.load(f)
    by_id: Dict[int, dict] = {r["hexagram_id"]: r for r in records}
    by_binary: Dict[str, dict] = {r["binary_code"]: r for r in records}
    return by_id, by_binary


_BY_ID, _BY_BINARY = _load()


def get_hexagram_by_id(hexagram_id: int) -> dict:
    """按编号（1-64）查询卦象数据。"""
    if hexagram_id not in _BY_ID:
        raise ValueError(f"hexagram_id {hexagram_id!r} out of range (1-64)")
    return _BY_ID[hexagram_id]


def get_hexagram_by_binary(binary_code: str) -> dict:
    """按 6 位 0/1 字符串查询卦象数据。"""
    if binary_code not in _BY_BINARY:
        raise ValueError(f"binary_code {binary_code!r} not found in hexagram data")
    return _BY_BINARY[binary_code]
