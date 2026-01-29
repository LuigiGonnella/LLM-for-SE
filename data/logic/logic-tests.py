import pytest

# ============================================================================
# TEST FUNCTIONS - FIZZBUZZ
# ============================================================================


def fizz_buzz(n: int) -> list:
    """Return a list of strings from 1 to n where: multiples of 3 are 'Fizz', multiples of 5 are 'Buzz',
    multiples of both are 'FizzBuzz', and other numbers are their string representation.
    """
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n < 1:
        raise ValueError("Input must be a positive integer")

    result = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result


class TestFizzBuzz:
    def test_fizzbuzz_basic(self):
        """Test basic FizzBuzz up to 15"""
        expected = [
            "1",
            "2",
            "Fizz",
            "4",
            "Buzz",
            "Fizz",
            "7",
            "8",
            "Fizz",
            "Buzz",
            "11",
            "Fizz",
            "13",
            "14",
            "FizzBuzz",
        ]
        assert fizz_buzz(15) == expected

    def test_fizzbuzz_up_to_5(self):
        """Test FizzBuzz up to 5"""
        expected = ["1", "2", "Fizz", "4", "Buzz"]
        assert fizz_buzz(5) == expected

    def test_fizzbuzz_with_multiple_15s(self):
        """Test that multiples of 15 are FizzBuzz"""
        result = fizz_buzz(30)
        assert result[14] == "FizzBuzz"  # 15
        assert result[29] == "FizzBuzz"  # 30

    def test_fizzbuzz_multiples_of_3(self):
        """Test that multiples of 3 (not 15) are Fizz"""
        result = fizz_buzz(10)
        assert result[2] == "Fizz"  # 3
        assert result[5] == "Fizz"  # 6
        assert result[8] == "Fizz"  # 9

    def test_fizzbuzz_multiples_of_5(self):
        """Test that multiples of 5 (not 15) are Buzz"""
        result = fizz_buzz(10)
        assert result[4] == "Buzz"  # 5
        assert result[9] == "Buzz"  # 10

    def test_fizzbuzz_n_equals_1(self):
        """Test with n = 1"""
        assert fizz_buzz(1) == ["1"]

    def test_fizzbuzz_large_n(self):
        """Test with large n"""
        result = fizz_buzz(100)
        assert len(result) == 100
        assert result[99] == "Buzz"  # 100

    def test_fizzbuzz_non_integer(self):
        """Test with non-integer input"""
        with pytest.raises(TypeError):
            fizz_buzz("15")

    def test_fizzbuzz_zero(self):
        """Test with zero"""
        with pytest.raises(ValueError):
            fizz_buzz(0)

    def test_fizzbuzz_negative(self):
        """Test with negative number"""
        with pytest.raises(ValueError):
            fizz_buzz(-5)


# ============================================================================
# TEST FUNCTIONS - SUDOKU VALIDATOR
# ============================================================================


def is_valid_sudoku(board: list[list[str]]) -> bool:
    """Determine if a 9x9 Sudoku board is valid. Only filled cells (1-9) need to be validated.
    Empty cells are represented by '.'. Each row, column, and 3x3 sub-box must contain digits
    1-9 without repetition."""
    if not isinstance(board, list) or len(board) != 9:
        raise ValueError("Board must be a 9x9 list")

    for row in board:
        if not isinstance(row, list) or len(row) != 9:
            raise ValueError("Each row must be a list of 9 elements")

    # Check rows
    for row in board:
        seen = set()
        for cell in row:
            if cell != "." and (cell in seen or cell not in "123456789"):
                return False
            if cell != ".":
                seen.add(cell)

    # Check columns
    for col in range(9):
        seen = set()
        for row in range(9):
            cell = board[row][col]
            if cell != "." and (cell in seen or cell not in "123456789"):
                return False
            if cell != ".":
                seen.add(cell)

    # Check 3x3 sub-boxes
    for box_row in range(3):
        for box_col in range(3):
            seen = set()
            for i in range(3):
                for j in range(3):
                    cell = board[box_row * 3 + i][box_col * 3 + j]
                    if cell != "." and (cell in seen or cell not in "123456789"):
                        return False
                    if cell != ".":
                        seen.add(cell)

    return True


class TestIsValidSudoku:
    def test_valid_sudoku_partial(self):
        """Test with a valid partially filled Sudoku"""
        board = [
            ["5", "3", ".", ".", "7", ".", ".", ".", "."],
            ["6", ".", ".", "1", "9", "5", ".", ".", "."],
            [".", "9", "8", ".", ".", ".", ".", "6", "."],
            ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
            ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
            ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
            [".", "6", ".", ".", ".", ".", "2", "8", "."],
            [".", ".", ".", "4", "1", "9", ".", ".", "5"],
            [".", ".", ".", ".", "8", ".", ".", "7", "9"],
        ]
        assert is_valid_sudoku(board) is True

    def test_invalid_sudoku_duplicate_in_row(self):
        """Test with duplicate in row"""
        board = [
            ["8", "3", ".", ".", "7", ".", ".", ".", "."],
            ["6", ".", ".", "1", "9", "5", ".", ".", "."],
            [".", "9", "8", ".", ".", ".", ".", "6", "."],
            ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
            ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
            ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
            [".", "6", ".", ".", ".", ".", "2", "8", "."],
            [".", ".", ".", "4", "1", "9", ".", ".", "5"],
            [".", ".", ".", ".", "8", ".", ".", "7", "9"],
        ]
        assert is_valid_sudoku(board) is False

    def test_valid_empty_sudoku(self):
        """Test with completely empty Sudoku"""
        board = [
            [".", ".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", ".", "."],
        ]
        assert is_valid_sudoku(board) is True

    def test_sudoku_wrong_size(self):
        """Test with wrong board size"""
        board = [
            ["5", "3", ".", ".", "7", ".", ".", "."],
            ["6", ".", ".", "1", "9", "5", ".", "."],
        ]
        with pytest.raises(ValueError):
            is_valid_sudoku(board)


# ============================================================================
# TEST FUNCTIONS - NEXT PERMUTATION
# ============================================================================


def next_permutation(nums: list[int]) -> list[int]:
    """Rearrange numbers into the lexicographically next greater permutation.
    If no such permutation exists, return the lowest possible order (sorted in ascending order).
    Modify the list in-place and return it."""
    if not isinstance(nums, list):
        raise TypeError("Input must be a list")

    if not all(isinstance(x, int) for x in nums):
        raise TypeError("All elements must be integers")

    # Find the first decreasing element from the right
    i = len(nums) - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i -= 1

    if i >= 0:
        # Find the smallest element greater than nums[i] from the right
        j = len(nums) - 1
        while nums[j] <= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]

    # Reverse the suffix
    nums[i + 1 :] = reversed(nums[i + 1 :])
    return nums


class TestNextPermutation:
    def test_next_permutation_basic(self):
        """Test basic next permutation"""
        assert next_permutation([1, 2, 3]) == [1, 3, 2]
        assert next_permutation([1, 3, 2]) == [2, 1, 3]

    def test_next_permutation_descending(self):
        """Test with descending order (wraps to ascending)"""
        assert next_permutation([3, 2, 1]) == [1, 2, 3]

    def test_next_permutation_with_duplicates(self):
        """Test with duplicate elements"""
        assert next_permutation([1, 1, 5]) == [1, 5, 1]
        assert next_permutation([1, 5, 1]) == [5, 1, 1]

    def test_next_permutation_single_element(self):
        """Test with single element"""
        assert next_permutation([1]) == [1]

    def test_next_permutation_two_elements(self):
        """Test with two elements"""
        assert next_permutation([1, 2]) == [2, 1]
        assert next_permutation([2, 1]) == [1, 2]

    def test_next_permutation_non_list(self):
        """Test with non-list input"""
        with pytest.raises(TypeError):
            next_permutation("123")

    def test_next_permutation_non_integers(self):
        """Test with non-integer elements"""
        with pytest.raises(TypeError):
            next_permutation([1, "2", 3])


# ============================================================================
# TEST FUNCTIONS - N-QUEENS
# ============================================================================


def solve_n_queens(n: int) -> list[list[str]]:
    """Solve the N-Queens puzzle: place n queens on an n x n chessboard so no two queens attack each other.
    Return all distinct solutions where each solution contains board configurations with 'Q'
    for queen and '.' for empty space."""
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n < 1:
        raise ValueError("Input must be a positive integer")

    def is_safe(board, row, col):
        # Check column
        for i in range(row):
            if board[i] == col:
                return False

        # Check diagonal (upper left)
        for i in range(1, row + 1):
            if row - i >= 0 and col - i >= 0:
                if board[row - i] == col - i:
                    return False

        # Check diagonal (upper right)
        for i in range(1, row + 1):
            if row - i >= 0 and col + i < n:
                if board[row - i] == col + i:
                    return False

        return True

    def solve(row, board):
        if row == n:
            # Convert board to required format
            solution = []
            for queen_col in board:
                row_str = "." * queen_col + "Q" + "." * (n - queen_col - 1)
                solution.append(row_str)
            solutions.append(solution)
            return

        for col in range(n):
            if is_safe(board, row, col):
                board[row] = col
                solve(row + 1, board)
                board[row] = -1

    solutions = []
    solve(0, [-1] * n)
    return solutions


class TestSolveNQueens:
    def test_n_queens_4(self):
        """Test 4-Queens problem"""
        result = solve_n_queens(4)
        assert len(result) == 2
        expected = [[".Q..", "...Q", "Q...", "..Q."], ["..Q.", "Q...", "...Q", ".Q.."]]
        assert result[0] in expected
        assert result[1] in expected

    def test_n_queens_1(self):
        """Test 1-Queen problem"""
        result = solve_n_queens(1)
        assert result == [["Q"]]

    def test_n_queens_2(self):
        """Test 2-Queens problem (no solution)"""
        result = solve_n_queens(2)
        assert result == []

    def test_n_queens_3(self):
        """Test 3-Queens problem (no solution)"""
        result = solve_n_queens(3)
        assert result == []

    def test_n_queens_8(self):
        """Test 8-Queens problem (should have 92 solutions)"""
        result = solve_n_queens(8)
        assert len(result) == 92

    def test_n_queens_non_integer(self):
        """Test with non-integer input"""
        with pytest.raises(TypeError):
            solve_n_queens("4")

    def test_n_queens_zero(self):
        """Test with zero"""
        with pytest.raises(ValueError):
            solve_n_queens(0)

    def test_n_queens_negative(self):
        """Test with negative number"""
        with pytest.raises(ValueError):
            solve_n_queens(-1)


# ============================================================================
# TEST FUNCTIONS - EXPRESSION EVALUATOR
# ============================================================================


def evaluate_expression(expression: str) -> bool:
    """Given a string expression with parentheses, AND ('&'), OR ('|'), and NOT ('!') operators,
    and boolean values ('t' for true, 'f' for false), evaluate the expression and return the result.
    Parentheses indicate evaluation order."""
    if not isinstance(expression, str):
        raise TypeError("Input must be a string")

    def parse(index):
        if expression[index] == "t":
            return True, index + 1
        if expression[index] == "f":
            return False, index + 1

        op = expression[index]
        index += 2  # Skip operator and '('

        values = []
        while expression[index] != ")":
            if expression[index] == ",":
                index += 1
            else:
                value, index = parse(index)
                values.append(value)

        index += 1  # Skip ')'

        if op == "!":
            return not values[0], index
        elif op == "&":
            return all(values), index
        elif op == "|":
            return any(values), index

    result, _ = parse(0)
    return result


class TestEvaluateExpression:
    def test_evaluate_simple_not(self):
        """Test simple NOT operation"""
        assert evaluate_expression("!(f)") is True
        assert evaluate_expression("!(t)") is False

    def test_evaluate_simple_or(self):
        """Test simple OR operation"""
        assert evaluate_expression("|(f,t)") is True
        assert evaluate_expression("|(f,f)") is False
        assert evaluate_expression("|(t,t)") is True

    def test_evaluate_simple_and(self):
        """Test simple AND operation"""
        assert evaluate_expression("&(t,f)") is False
        assert evaluate_expression("&(t,t)") is True
        assert evaluate_expression("&(f,f)") is False

    def test_evaluate_nested(self):
        """Test nested expression"""
        assert evaluate_expression("|(&(t,f,t),!(t))") is False

    def test_evaluate_multiple_or(self):
        """Test OR with multiple operands"""
        assert evaluate_expression("|(f,f,t)") is True
        assert evaluate_expression("|(f,f,f)") is False

    def test_evaluate_multiple_and(self):
        """Test AND with multiple operands"""
        assert evaluate_expression("&(t,t,t)") is True
        assert evaluate_expression("&(t,t,f)") is False

    def test_evaluate_complex(self):
        """Test complex nested expression"""
        assert evaluate_expression("!(&(f,t))") is True
        assert evaluate_expression("|(!(f),&(t,t))") is True

    def test_evaluate_non_string(self):
        """Test with non-string input"""
        with pytest.raises(TypeError):
            evaluate_expression(123)
