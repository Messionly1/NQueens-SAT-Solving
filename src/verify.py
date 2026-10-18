def is_valid_placement(cols, n: int) -> bool:
    if not cols or len(cols) != n:
        return False
    if any(c is None or not 0 <= c < n for c in cols):
        return False
    return (len(set(cols)) == n
            and len({cols[r] - r for r in range(n)}) == n
            and len({cols[r] + r for r in range(n)}) == n)


def model_to_columns(model, n: int):
    if not model:
        return None
    cols = [None] * n
    for lit in model:
        if 0 < lit <= n * n:
            r, c = divmod(lit - 1, n)
            if cols[r] is not None:
                return None
            cols[r] = c
    return None if None in cols else cols


def verify_sat_model(model, n: int) -> bool:
    return is_valid_placement(model_to_columns(model, n), n)
