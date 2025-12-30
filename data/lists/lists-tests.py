import pytest
from typing import List, Tuple

LIST_ERROR = "Input must be a list"

# ============================================================================
# TEST FUNCTIONS - BELOW ZERO
# ============================================================================


def below_zero(operations: List[int]) -> bool:
    """You're given a list of deposit and withdrawal operations on a bank account that starts with zero balance.
    Your task is to detect if at any point the balance of account falls below zero, and at that point function should return True.
    Otherwise it should return False.
    """

    if not isinstance(operations, list):
        raise TypeError(LIST_ERROR)

    balance = 0

    for op in operations:
        if not isinstance(op, int):
            raise ValueError("List elements must be integers")

        balance += op
        if balance < 0:
            return True

    return False


class TestBelowZero:
    """Tests for below_zero function"""

    # VALID TESTS
    def test_case_1(self):
        assert below_zero([1, 2, -3, 1, 2, -3]) is False

    def test_case_2(self):
        assert below_zero([1, 2, -4, 5, 6]) is True

    def test_case_3(self):
        assert below_zero([1, -1, 2, -2, 5, -5, 4, -4]) is False

    def test_case_4(self):
        assert below_zero([1, -1, 2, -2, 5, -5, 4, -5]) is True

    def test_case_5(self):
        assert below_zero([1, -2, 2, -2, 5, -5, 4, -4]) is True

    # BUONDARY TESTS
    def test_case_6(self):
        assert below_zero([]) is False

    def test_case_7(self):
        assert below_zero([0, 0, 0, 0]) is False

    def test_case_8(self):
        assert below_zero([-1]) is True

    def test_case_9(self):
        assert below_zero([1]) is False

    # INVALID INPUT TESTS
    def test_case_10(self):
        with pytest.raises(TypeError):
            below_zero("not a list")

    def test_case_11(self):
        with pytest.raises(ValueError):
            below_zero([1, 2, "3"])

    def test_case_12(self):
        with pytest.raises(ValueError):
            below_zero([1.5, 2])


# ============================================================================
# TEST FUNCTIONS - FIND CLOSEST ELEMENTS
# ============================================================================


def find_closest_elements(numbers: List[float]) -> Tuple[float, float]:
    """From a supplied list of numbers (of length at least two) select and return two that are the closest to each
    other and return them in order (smaller number, larger number).
    """
    if not isinstance(numbers, list):
        raise TypeError(LIST_ERROR)

    if len(numbers) < 2:
        raise ValueError("List must contain at least two elements")

    for elem in numbers:
        if not isinstance(elem, (int, float)):
            raise ValueError("List elements must be numbers")

    closest_pair = None
    distance = None

    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                if distance is None:
                    distance = abs(elem - elem2)
                    closest_pair = tuple(sorted([elem, elem2]))
                else:
                    new_distance = abs(elem - elem2)
                    if new_distance < distance:
                        distance = new_distance
                        closest_pair = tuple(sorted([elem, elem2]))

    return closest_pair


class TestFindClosestElements:
    """Tests for find_closest_elements function"""

    # VALID TESTS
    def test_case_1(self):
        assert find_closest_elements([1.0, 2.0, 3.9, 4.0, 5.0, 2.2]) == (3.9, 4.0)

    def test_case_2(self):
        assert find_closest_elements([1.0, 2.0, 5.9, 4.0, 5.0]) == (5.0, 5.9)

    def test_case_3(self):
        assert find_closest_elements([1.0, 2.0, 3.0, 4.0, 5.0, 2.2]) == (2.0, 2.2)

    def test_case_4(self):
        assert find_closest_elements([1.0, 2.0, 3.0, 4.0, 5.0, 2.0]) == (2.0, 2.0)

    def test_case_5(self):
        assert find_closest_elements([1.1, 2.2, 3.1, 4.1, 5.1]) == (2.2, 3.1)

    def test_case_6(self):
        assert find_closest_elements([-1.0, -2.0, -1.1, -5.0]) == (-1.1, -1.0)

    # BOUNDARY TESTS
    def test_case_7(self):
        assert find_closest_elements([1.0, 10.0]) == (1.0, 10.0)

    def test_case_8(self):
        assert find_closest_elements([1.0, 1.0, 1.0, 1.0]) == (1.0, 1.0)

    def test_case_9(self):
        assert find_closest_elements([1.0, 1.000001, 2.0, 3.0]) == (1.0, 1.000001)

    def test_case_10(self):
        assert find_closest_elements([1, 2.5, 3, 10]) == (2.5, 3)

    # INVALID INPUT TESTS
    def test_case_11(self):
        with pytest.raises(TypeError):
            find_closest_elements("not a list")

    def test_case_12(self):
        with pytest.raises(ValueError):
            find_closest_elements([1.0])

    def test_case_13(self):
        with pytest.raises(ValueError):
            find_closest_elements([1.0, "2.0"])


# ============================================================================
# TEST FUNCTIONS - SEARCH
# ============================================================================


def search(lst: List[int]) -> int:
    """You are given a non-empty list of positive integers. Return the greatest integer that is greater than zero,
    and has a frequency greater than or equal to the value of the integer itself.
    The frequency of an integer is the number of times it appears in the list. If no such a value exist, return -1.
    """
    if not isinstance(lst, list):
        raise TypeError(LIST_ERROR)

    if not lst:
        raise ValueError("List cannot be empty")

    for i in lst:
        if not isinstance(i, int):
            raise ValueError("List elements must be integers")
        if i <= 0:
            raise ValueError("List elements must be positive integers")

    frq = [0] * (max(lst) + 1)
    for i in lst:
        frq[i] += 1

    ans = -1
    for i in range(1, len(frq)):
        if frq[i] >= i:
            ans = i

    return ans


class TestSearch:
    """Tests for search function"""

    # VALID TESTS
    def test_case_1(self):
        assert search([2, 3, 3, 2, 2]) == 2

    def test_case_2(self):
        assert search(
            [2, 7, 8, 8, 4, 8, 7, 3, 9, 6, 5, 10, 4, 3, 6, 7, 1, 7, 4, 10, 8, 1]
        ) == 1

    def test_case_3(self):
        assert search([3, 2, 8, 2]) == 2

    def test_case_4(self):
        assert search([8, 8, 3, 6, 5, 6, 4]) == -1

    def test_case_5(self):
        assert search([5, 5, 3, 9, 5, 6, 3, 2, 8, 5, 6, 10, 10, 6, 8, 4, 10, 7, 7, 10, 8]) == -1

    def test_case_6(self):
        assert search([10]) == -1

    # BOUNDARY TESTS
    def test_case_7(self):
        assert search([3, 3]) == -1

    def test_case_8(self):
        assert search([8, 8, 8, 8, 8, 8, 8, 8]) == 8

    def test_case_9(self):
        assert search([4, 1, 4, 1, 4, 4]) == 4

    def test_case_10(self):
        assert search([5, 5, 5, 5, 1]) == 1

    # INVALID INPUT TESTS
    def test_case_11(self):
        with pytest.raises(TypeError):
            search("not a list")

    def test_case_12(self):
        with pytest.raises(ValueError):
            search([])

    def test_case_13(self):
        with pytest.raises(ValueError):
            search([1, 2, "3"])

    def test_case_14(self):
        with pytest.raises(ValueError):
            search([1, 2, 0])

    def test_case_15(self):
        with pytest.raises(ValueError):
            search([1, 2, -1])


# ============================================================================
# TEST FUNCTIONS - TRIPLES SUM TO ZERO
# ============================================================================


def triples_sum_to_zero(numbers: List[int]) -> bool:
    """triples_sum_to_zero takes a list of integers as an input.
    It returns True if there are three distinct elements in the list that sum to zero, and False otherwise.
    """
    if not isinstance(numbers, list):
        raise TypeError(LIST_ERROR)

    for e in numbers:
        if not isinstance(e, int):
            raise ValueError("List elements must be integers")

    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            for k in range(j + 1, len(numbers)):
                if numbers[i] + numbers[j] + numbers[k] == 0:
                    return True

    return False


class TestTriplesSumToZero:
    """Tests for triples_sum_to_zero function"""

    # VALID TESTS
    def test_case_1(self):
        assert triples_sum_to_zero([1, 3, 5, 0]) is False

    def test_case_2(self):
        assert triples_sum_to_zero([1, 3, -2, 1]) is True

    def test_case_3(self):
        assert triples_sum_to_zero([1, 2, 3, 7]) is False

    def test_case_4(self):
        assert triples_sum_to_zero([2, 4, -5, 3, 9, 7]) is True

    def test_case_5(self):
        assert triples_sum_to_zero([1]) is False

    # BOUNDARY TESTS
    def test_case_6(self):
        assert triples_sum_to_zero([1, 3, 5, -100]) is False

    def test_case_7(self):
        assert triples_sum_to_zero([100, 3, 5, -100]) is False

    def test_case_8(self):
        assert triples_sum_to_zero([1, 2]) is False

    def test_case_9(self):
        assert triples_sum_to_zero([0, 0, 0]) is True

    def test_case_10(self):
        assert triples_sum_to_zero([-10, 5, 5]) is True

    def test_case_11(self):
        assert triples_sum_to_zero([1, 2, 3]) is False

    def test_case_12(self):
        assert triples_sum_to_zero([]) is False

    # INVALID INPUT TESTS
    def test_case_13(self):
        with pytest.raises(TypeError):
            triples_sum_to_zero("not a list")

    def test_case_14(self):
        with pytest.raises(ValueError):
            triples_sum_to_zero([1, 2, "3"])

    def test_case_15(self):
        with pytest.raises(ValueError):
            triples_sum_to_zero([1, 2, 3.5])


# ============================================================================
# TEST FUNCTIONS - MIN PATH
# ============================================================================


def minPath(grid: List[List[int]], k: int) -> List[int]:
    """
    Given a grid with N rows and N columns (N >= 2) and a positive integer k, each cell of the grid contains a value.
    Every integer in the range [1, N * N] inclusive appears exactly once on the cells of the grid.
    You have to find the minimum path of length k in the grid. You can start from any cell, and in each step you can move
    to any of the neighbor cells, in other words, you can go to cells which share an edge with you current cell.
    Please note that a path of length k means visiting exactly k cells (not necessarily distinct).
    You CANNOT go off the grid.
    A path A (of length k) is considered less than a path B (of length k) if after making the ordered lists of the values
    on the cells that A and B go through (let's call them lst_A and lst_B), lst_A is lexicographically less than lst_B,
    in other words, there exist an integer index i (1 <= i <= k) such that lst_A[i] < lst_B[i] and for any j (1 <= j < i)
    we have lst_A[j] = lst_B[j].
    It is guaranteed that the answer is unique.
    Return an ordered list of the values on the cells that the minimum path go through.
    """
    if not isinstance(grid, list):
        raise TypeError("Grid must be a list of lists")

    if not isinstance(k, int) or k <= 0:
        raise ValueError("k must be a positive integer")

    n = len(grid)
    if n < 2:
        raise ValueError("Grid size N must be at least 2")

    seen_values = set()
    for row in grid:
        if not isinstance(row, list):
            raise TypeError("Grid must be a list of lists")
        if len(row) != n:
            raise ValueError("Grid must be square (N x N)")
        for val in row:
            if not isinstance(val, int):
                raise ValueError("Grid elements must be integers")
            if val < 1 or val > n * n:
                raise ValueError(f"Grid values must be in range [1, {n*n}]")
            if val in seen_values:
                raise ValueError("Grid values must be unique")
            seen_values.add(val)

    val = n * n + 1
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 1:
                temp = []
                if i != 0:
                    temp.append(grid[i - 1][j])

                if j != 0:
                    temp.append(grid[i][j - 1])

                if i != n - 1:
                    temp.append(grid[i + 1][j])

                if j != n - 1:
                    temp.append(grid[i][j + 1])

                val = min(temp)

    ans = []
    for i in range(k):
        if i % 2 == 0:
            ans.append(1)
        else:
            ans.append(val)
    return ans


class TestMinPath:
    """Tests for minPath function"""

    # VALID TESTS
    def test_case_1(self):
        assert minPath([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 3) == [1, 2, 1]

    def test_case_2(self):
        assert minPath([[5, 9, 3], [4, 1, 6], [7, 8, 2]], 1) == [1]

    def test_case_3(self):
        assert minPath(
            [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]], 4
        ) == [1, 2, 1, 2]

    def test_case_4(self):
        assert minPath(
            [[8, 14, 9, 2], [6, 4, 13, 15], [5, 7, 1, 12], [3, 10, 11, 16]], 5
        ) == [1, 7, 1, 7, 1]

    def test_case_5(self):
        assert minPath([[2, 7, 4], [3, 1, 5], [6, 8, 9]], 8) == [
            1,
            3,
            1,
            3,
            1,
            3,
            1,
            3,
        ]

    # BOUNDARY TESTS
    def test_case_6(self):
        assert minPath([[1, 2], [3, 4]], 10) == [1, 2, 1, 2, 1, 2, 1, 2, 1, 2]

    def test_case_7(self):
        assert minPath([[1, 3], [4, 2]], 10) == [1, 3, 1, 3, 1, 3, 1, 3, 1, 3]

    # INVALID INPUT TESTS
    def test_case_8(self):
        with pytest.raises(TypeError):
            minPath("not a list", 3)

    def test_case_9(self):
        with pytest.raises(ValueError):
            minPath([[1]], 3)

    def test_case_10(self):
        with pytest.raises(ValueError):
            minPath([[1, 2], [3]], 3)

    def test_case_11(self):
        with pytest.raises(ValueError):
            minPath([[1, 2], [2, 4]], 3)

    def test_case_12(self):
        with pytest.raises(ValueError):
            minPath([[1, 2], [3, "4"]], 3)

    def test_case_13(self):
        with pytest.raises(ValueError):
            minPath([[1, 2], [3, 4]], 0)

    def test_case_14(self):
        with pytest.raises(ValueError):
            minPath([[1, 2], [3, 4]], -5)

    def test_case_15(self):
        with pytest.raises(ValueError):
            minPath([[1, 2], [3, 5]], 3)
