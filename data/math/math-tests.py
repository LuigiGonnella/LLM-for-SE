# Auto-generated from HumanEval (typed, additive, faithful)
import math
import pytest

# =========================================================
# TEST FUNCTIONS - PRIME FIB
# =========================================================


def prime_fib(n: int) -> int:
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n <= 0:
        raise ValueError("n must be positive")

    def is_prime(p: int) -> bool:
        if p < 2:
            return False
        for k in range(2, int(math.sqrt(p)) + 1):
            if p % k == 0:
                return False
        return True

    f = [0, 1]
    while True:
        f.append(f[-1] + f[-2])
        if is_prime(f[-1]):
            n -= 1
        if n == 0:
            return f[-1]


class TestPrimeFib:
    """Tests for prime_fib"""

    # ---- ORIGINAL HumanEval TESTS ----
    def test_case_1(self):
        assert prime_fib(1) == 2

    def test_case_2(self):
        assert prime_fib(2) == 3

    def test_case_3(self):
        assert prime_fib(3) == 5

    def test_case_4(self):
        assert prime_fib(4) == 13

    def test_case_5(self):
        assert prime_fib(5) == 89

    def test_case_6(self):
        assert prime_fib(6) == 233

    def test_case_7(self):
        assert prime_fib(7) == 1597

    def test_case_8(self):
        assert prime_fib(8) == 28657

    def test_case_9(self):
        assert prime_fib(9) == 514229

    def test_case_10(self):
        assert prime_fib(10) == 433494437

    # ---- ADDED TYPE / DOMAIN TESTS ----
    def test_type_error(self):
        with pytest.raises(TypeError):
            prime_fib(3.5)

    def test_value_error(self):
        with pytest.raises(ValueError):
            prime_fib(0)


# =========================================================
# TEST FUNCTIONS - MODP
# =========================================================


def modp(n: int, p: int) -> int:
    if not isinstance(n, int) or not isinstance(p, int):
        raise TypeError("n and p must be integers")
    if n < 0 or p <= 0:
        raise ValueError("n must be >= 0 and p must be > 0")

    ret = 1
    for _ in range(n):
        ret = (2 * ret) % p
    return ret


class TestModp:
    """Tests for modp"""

    # ---- ORIGINAL HumanEval TESTS ----
    def test_case_1(self):
        assert modp(3, 5) == 3

    def test_case_2(self):
        assert modp(1101, 101) == 2

    def test_case_3(self):
        assert modp(0, 101) == 1

    def test_case_4(self):
        assert modp(3, 11) == 8

    def test_case_5(self):
        assert modp(100, 101) == 1

    def test_case_6(self):
        assert modp(30, 5) == 4

    def test_case_7(self):
        assert modp(31, 5) == 3

    # ---- ADDED TYPE / DOMAIN TESTS ----
    def test_type_error(self):
        with pytest.raises(TypeError):
            modp(3.5, 5)

    def test_value_error(self):
        with pytest.raises(ValueError):
            modp(-1, 5)


# =========================================================
# TEST FUNCTIONS - LARGEST PRIME FACTOR
# =========================================================


def largest_prime_factor(n: int) -> int:
    largest_prime = 0
    factor = 2

    while n > 1:
        if n % factor == 0:
            largest_prime = factor
            while n % factor == 0:
                n //= factor
        factor += 1

    return largest_prime


class TestLargestPrimeFactor:
    """Tests for largest_prime_factor"""

    # ---- ORIGINAL HumanEval TESTS ----
    def test_case_1(self):
        assert largest_prime_factor(15) == 5

    def test_case_2(self):
        assert largest_prime_factor(27) == 3

    def test_case_3(self):
        assert largest_prime_factor(63) == 7

    def test_case_4(self):
        assert largest_prime_factor(330) == 11

    def test_case_5(self):
        assert largest_prime_factor(13195) == 29

    # ---- ADDED TYPE / DOMAIN TESTS ----
    def test_type_error(self):
        with pytest.raises(TypeError):
            largest_prime_factor(10.5)

    def test_value_error(self):
        with pytest.raises(ValueError):
            largest_prime_factor(1)


# =========================================================
# TEST FUNCTIONS - IS SIMPLE POWER
# =========================================================


def is_simple_power(x: int, n: int) -> bool:
    if not isinstance(x, int) or not isinstance(n, int):
        raise TypeError("x and n must be integers")
    if x < 1 or n < 1:
        raise ValueError("x and n must be positive integers")

    if n == 1:
        return x == 1

    power = 1
    while power < x:
        power *= n
    return power == x


class TestIsSimplePower:
    """Tests for is_simple_power"""

    # ---- ORIGINAL HumanEval TESTS (ALL 10) ----
    def test_case_1(self):
        assert is_simple_power(16, 2) is True

    def test_case_2(self):
        assert is_simple_power(143214, 16) is False

    def test_case_3(self):
        assert is_simple_power(4, 2) is True

    def test_case_4(self):
        assert is_simple_power(9, 3) is True

    def test_case_5(self):
        assert is_simple_power(16, 4) is True

    def test_case_6(self):
        assert is_simple_power(24, 2) is False

    def test_case_7(self):
        assert is_simple_power(128, 4) is False

    def test_case_8(self):
        assert is_simple_power(12, 6) is False

    def test_case_9(self):
        assert is_simple_power(1, 1) is True

    def test_case_10(self):
        assert is_simple_power(1, 12) is True

    # ---- ADDED TYPE / DOMAIN TESTS ----
    def test_type_error(self):
        with pytest.raises(TypeError):
            is_simple_power(4.0, 2)

    def test_value_error(self):
        with pytest.raises(ValueError):
            is_simple_power(0, 2)


# =========================================================
# TEST FUNCTIONS - ANY INT
# =========================================================


def any_int(x: float, y: float, z: float) -> bool:
    for v in (x, y, z):
        if not isinstance(v, (int, float)):
            raise TypeError("inputs must be numeric")

    if not all(isinstance(v, int) for v in (x, y, z)):
        return False

    return (x + y == z) or (x + z == y) or (y + z == x)


class TestAnyInt:
    """Tests for any_int"""

    # ---- ORIGINAL HumanEval TESTS ----
    def test_case_1(self):
        assert any_int(2, 3, 1) is True

    def test_case_2(self):
        assert any_int(2.5, 2, 3) is False

    def test_case_3(self):
        assert any_int(1.5, 5, 3.5) is False

    def test_case_4(self):
        assert any_int(2, 6, 2) is False

    def test_case_5(self):
        assert any_int(4, 2, 2) is True

    def test_case_6(self):
        assert any_int(2.2, 2.2, 2.2) is False

    def test_case_7(self):
        assert any_int(-4, 6, 2) is True

    def test_case_8(self):
        assert any_int(2, 1, 1) is True

    def test_case_9(self):
        assert any_int(3, 4, 7) is True

    def test_case_10(self):
        assert any_int(3.0, 4, 7) is False

    # ---- ADDED TYPE TEST ----
    def test_type_error(self):
        with pytest.raises(TypeError):
            any_int("3", 2, 1)
