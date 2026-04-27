from app.core.hexagram_data import _BY_BINARY

# coin_sum → (line_type, is_yang, is_changing)
_COIN_MAP: dict[int, tuple[str, bool, bool]] = {
    6: ("老阴", False, True),   # all tails → changing yin
    7: ("少阳", True,  False),  # static yang
    8: ("少阴", False, False),  # static yin
    9: ("老阳", True,  True),   # all heads → changing yang
}


def map_coin(coin_sum: int) -> tuple[str, bool]:
    """Map a coin sum (6/7/8/9) to (line_type, is_changing).

    Raises ValueError for any other value.
    """
    if coin_sum not in _COIN_MAP:
        raise ValueError(
            f"coin_sum must be 6, 7, 8, or 9; got {coin_sum!r}"
        )
    line_type, _, is_changing = _COIN_MAP[coin_sum]
    return line_type, is_changing


def generate_hexagram(coin_sums: list[int]) -> dict:
    """Compute base/changed hexagram from 6 coin sums (line 1 first, line 6 last).

    Returns:
        {
            "base_hexagram":    int,   # hexagram_id 1-64
            "changed_hexagram": int,   # hexagram_id 1-64
            "changing_lines":   list[int],  # 1-indexed positions of dynamic yao
        }

    Raises ValueError if coin_sums length != 6 or any value is invalid.
    """
    if len(coin_sums) != 6:
        raise ValueError(f"Expected 6 coin sums, got {len(coin_sums)}")

    base_bits: list[str] = []
    changed_bits: list[str] = []
    changing_lines: list[int] = []

    for i, cs in enumerate(coin_sums):
        if cs not in _COIN_MAP:
            raise ValueError(f"coin_sums[{i}] must be 6/7/8/9, got {cs!r}")
        _, is_yang, is_changing = _COIN_MAP[cs]

        base_bit = "1" if is_yang else "0"
        base_bits.append(base_bit)

        if is_changing:
            changed_bits.append("0" if is_yang else "1")
            changing_lines.append(i + 1)  # 1-indexed line number
        else:
            changed_bits.append(base_bit)

    base_code = "".join(base_bits)
    changed_code = "".join(changed_bits)

    return {
        "base_hexagram":    _BY_BINARY[base_code]["hexagram_id"],
        "changed_hexagram": _BY_BINARY[changed_code]["hexagram_id"],
        "changing_lines":   changing_lines,
    }
