def any_int(x: float, y: float, z: float) -> bool:
    if not all(isinstance(i, int) for i in [x, y, z]):
        return False
    x, y, z = int(x), int(y), int(z)
    return x == y + z or y == x + z or z == x + y