# Auto-generated from HumanEval (typed, additive, faithful)
import math
import unittest


# =========================================================
# HumanEval/39 — prime_fib
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



class TestPrime_fib(unittest.TestCase):
    """Tests for prime_fib"""

    # ---- ORIGINAL HumanEval TESTS ----
    def test_case_1(self): self.assertEqual(prime_fib(1), 2)
    def test_case_2(self): self.assertEqual(prime_fib(2), 3)
    def test_case_3(self): self.assertEqual(prime_fib(3), 5)
    def test_case_4(self): self.assertEqual(prime_fib(4), 13)
    def test_case_5(self): self.assertEqual(prime_fib(5), 89)
    def test_case_6(self): self.assertEqual(prime_fib(6), 233)
    def test_case_7(self): self.assertEqual(prime_fib(7), 1597)
    def test_case_8(self): self.assertEqual(prime_fib(8), 28657)
    def test_case_9(self): self.assertEqual(prime_fib(9), 514229)
    def test_case_10(self): self.assertEqual(prime_fib(10), 433494437)

    # ---- ADDED TYPE / DOMAIN TESTS ----
    def test_type_error(self):
        with self.assertRaises(TypeError):
            prime_fib(3.5)

    def test_value_error(self):
        with self.assertRaises(ValueError):
            prime_fib(0)


# =========================================================
# HumanEval/49 — modp
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



class TestModp(unittest.TestCase):
    """Tests for modp"""

    # ---- ORIGINAL HumanEval TESTS ----
    def test_case_1(self): self.assertEqual(modp(3, 5), 3)
    def test_case_2(self): self.assertEqual(modp(1101, 101), 2)
    def test_case_3(self): self.assertEqual(modp(0, 101), 1)
    def test_case_4(self): self.assertEqual(modp(3, 11), 8)
    def test_case_5(self): self.assertEqual(modp(100, 101), 1)
    def test_case_6(self): self.assertEqual(modp(30, 5), 4)
    def test_case_7(self): self.assertEqual(modp(31, 5), 3)

    # ---- ADDED TYPE / DOMAIN TESTS ----
    def test_type_error(self):
        with self.assertRaises(TypeError):
            modp(3.5, 5)

    def test_value_error(self):
        with self.assertRaises(ValueError):
            modp(-1, 5)


# =========================================================
# HumanEval/59 — largest_prime_factor
# =========================================================

def largest_prime_factor(n: int) -> int:
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n <= 1:
        raise ValueError("n must be greater than 1")

    def is_prime(k: int) -> bool:
        if k < 2:
            return False
        for i in range(2, int(math.sqrt(k)) + 1):
            if k % i == 0:
                return False
        return True

    largest = 1
    for j in range(2, n + 1):
        if n % j == 0 and is_prime(j):
            largest = j
    return largest



class TestLargest_prime_factor(unittest.TestCase):
    """Tests for largest_prime_factor"""

    # ---- ORIGINAL HumanEval TESTS ----
    def test_case_1(self): self.assertEqual(largest_prime_factor(15), 5)
    def test_case_2(self): self.assertEqual(largest_prime_factor(27), 3)
    def test_case_3(self): self.assertEqual(largest_prime_factor(63), 7)
    def test_case_4(self): self.assertEqual(largest_prime_factor(330), 11)
    def test_case_5(self): self.assertEqual(largest_prime_factor(13195), 29)

    # ---- ADDED TYPE / DOMAIN TESTS ----
    def test_type_error(self):
        with self.assertRaises(TypeError):
            largest_prime_factor(10.5)

    def test_value_error(self):
        with self.assertRaises(ValueError):
            largest_prime_factor(1)


# =========================================================
# HumanEval/76 — is_simple_power
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


class TestIs_simple_power(unittest.TestCase):
    """Tests for is_simple_power"""

    # ---- ORIGINAL HumanEval TESTS (ALL 10) ----
    def test_case_1(self): self.assertEqual(is_simple_power(16, 2), True)
    def test_case_2(self): self.assertEqual(is_simple_power(143214, 16), False)
    def test_case_3(self): self.assertEqual(is_simple_power(4, 2), True)
    def test_case_4(self): self.assertEqual(is_simple_power(9, 3), True)
    def test_case_5(self): self.assertEqual(is_simple_power(16, 4), True)
    def test_case_6(self): self.assertEqual(is_simple_power(24, 2), False)
    def test_case_7(self): self.assertEqual(is_simple_power(128, 4), False)
    def test_case_8(self): self.assertEqual(is_simple_power(12, 6), False)
    def test_case_9(self): self.assertEqual(is_simple_power(1, 1), True)
    def test_case_10(self): self.assertEqual(is_simple_power(1, 12), True)

    # ---- ADDED TYPE / DOMAIN TESTS ----
    def test_type_error(self):
        with self.assertRaises(TypeError):
            is_simple_power(4.0, 2)

    def test_value_error(self):
        with self.assertRaises(ValueError):
            is_simple_power(0, 2)


# =========================================================
# HumanEval/92 — any_int
# =========================================================

def any_int(x: float, y: float, z: float) -> bool:
    for v in (x, y, z):
        if not isinstance(v, (int, float)):
            raise TypeError("inputs must be numeric")

    if not all(isinstance(v, int) for v in (x, y, z)):
        return False

    return (x + y == z) or (x + z == y) or (y + z == x)


class TestAny_int(unittest.TestCase):
    """Tests for any_int"""

    # ---- ORIGINAL HumanEval TESTS ----
    def test_case_1(self): self.assertEqual(any_int(2, 3, 1), True)
    def test_case_2(self): self.assertEqual(any_int(2.5, 2, 3), False)
    def test_case_3(self): self.assertEqual(any_int(1.5, 5, 3.5), False)
    def test_case_4(self): self.assertEqual(any_int(2, 6, 2), False)
    def test_case_5(self): self.assertEqual(any_int(4, 2, 2), True)
    def test_case_6(self): self.assertEqual(any_int(2.2, 2.2, 2.2), False)
    def test_case_7(self): self.assertEqual(any_int(-4, 6, 2), True)
    def test_case_8(self): self.assertEqual(any_int(2, 1, 1), True)
    def test_case_9(self): self.assertEqual(any_int(3, 4, 7), True)
    def test_case_10(self): self.assertEqual(any_int(3.0, 4, 7), False)

    # ---- ADDED TYPE TEST ----
    def test_type_error(self):
        with self.assertRaises(TypeError):
            any_int("3", 2, 1)


if __name__ == "__main__":
    unittest.main()
