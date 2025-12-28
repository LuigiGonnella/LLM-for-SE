import math

def is_simple_power(x: int, n: int) -> bool:
    if not isinstance(x, int) or not isinstance(n, int):
        return False
    if x == 1:
        return True
    if n in (0, 1):
        return x == 1
    log_result = math.log(x, n)
    return log_result.is_integer()