import unittest
from typing import List, Optional

# ============================================================================
# HELPER CLASSES
# ============================================================================

class TreeNode:
    """Definition for a binary tree node."""
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree_from_list(values: List) -> Optional[TreeNode]:
    """Build a binary tree from a level-order list representation."""
    if not values or values[0] is None:
        return None
    
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    
    while queue and i < len(values):
        node = queue.pop(0)
        
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    
    return root


# ============================================================================
# TASK IMPLEMENTATIONS 
# ============================================================================

def is_valid(s: str) -> bool:
    """Check if the input string of parentheses is valid."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in mapping:
            top_element = stack.pop() if stack else '#'
            if mapping[char] != top_element:
                return False
        elif char in '({[':
            stack.append(char)
    
    return not stack


def num_trees(n: int) -> int:
    """Given an integer n, return the number of structurally unique BST's which has exactly n nodes of unique values from 1 to n."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("Input must be an integer")
    if n < 0:
        raise ValueError("Input must be a non-negative integer")
    
    if n <= 1:
        return 1
    
    dp = [0] * (n + 1)
    dp[0], dp[1] = 1, 1
    
    for i in range(2, n + 1):
        for j in range(1, i + 1):
            dp[i] += dp[j - 1] * dp[i - j]
    
    return dp[n]


def length_of_lis(nums: List[int]) -> int:
    """Given an integer array nums, return the length of the longest strictly increasing subsequence."""
    if not isinstance(nums, list):
        raise TypeError("Input must be a list")
    if not all(isinstance(x, int) and not isinstance(x, bool) for x in nums):
        raise TypeError("All elements must be integers")
    
    if not nums:
        return 0
    
    dp = [1] * len(nums)
    
    for i in range(1, len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    
    return max(dp)


def find_median_sorted_arrays(nums1: List[int], nums2: List[int]) -> float:
    """Given two sorted arrays nums1 and nums2, return the median of the two sorted arrays."""
    if not isinstance(nums1, list) or not isinstance(nums2, list):
        raise TypeError("Both inputs must be lists")
    if not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums1 + nums2):
        raise TypeError("All elements must be numbers")
    
    merged = sorted(nums1 + nums2)
    n = len(merged)
    
    if n == 0:
        raise ValueError("Cannot find median of empty arrays")
    
    if n % 2 == 1:
        return float(merged[n // 2])
    else:
        return (merged[n // 2 - 1] + merged[n // 2]) / 2


def max_path_sum(root: Optional[TreeNode]) -> int:
    """Given the root of a binary tree, return the maximum path sum of any non-empty path."""
    if root is None:
        raise ValueError("Tree cannot be empty")
    if not isinstance(root, TreeNode):
        raise TypeError("Input must be a TreeNode")
    
    max_sum = float('-inf')
    
    def dfs(node):
        nonlocal max_sum
        if not node:
            return 0
        
        left_gain = max(dfs(node.left), 0)
        right_gain = max(dfs(node.right), 0)
        
        path_sum = node.val + left_gain + right_gain
        max_sum = max(max_sum, path_sum)
        
        return node.val + max(left_gain, right_gain)
    
    dfs(root)
    return max_sum


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestIsValid(unittest.TestCase):
    """Test cases for is_valid (Valid Parentheses) function"""
    
    # VALID TESTS
    def test_basic_valid_parentheses(self):
        """Test with basic valid parentheses"""
        self.assertTrue(is_valid('()'))
        self.assertTrue(is_valid('[]'))
        self.assertTrue(is_valid('{}'))
    
    def test_mixed_valid_parentheses(self):
        """Test with mixed valid parentheses"""
        self.assertTrue(is_valid('()[]{}'))
        self.assertTrue(is_valid('{[()]}'))
        self.assertTrue(is_valid('([{}])'))
    
    def test_nested_parentheses(self):
        """Test with nested parentheses"""
        self.assertTrue(is_valid('((()))'))
        self.assertTrue(is_valid('[[[]]]'))
        self.assertTrue(is_valid('{{{}}}'))
        self.assertTrue(is_valid('{[([])]}'))
    
    def test_invalid_closing_first(self):
        """Test with closing bracket first"""
        self.assertFalse(is_valid(')'))
        self.assertFalse(is_valid(']('))
        self.assertFalse(is_valid('}{'))
    
    def test_invalid_mismatched(self):
        """Test with mismatched brackets"""
        self.assertFalse(is_valid('(]'))
        self.assertFalse(is_valid('([)]'))
        self.assertFalse(is_valid('{[}]'))
    
    def test_invalid_unclosed(self):
        """Test with unclosed brackets"""
        self.assertFalse(is_valid('('))
        self.assertFalse(is_valid('(('))
        self.assertFalse(is_valid('(['))
        self.assertFalse(is_valid('{[('))
    
    # BOUNDARY TESTS
    def test_empty_string(self):
        """Test with empty string (should be valid)"""
        self.assertTrue(is_valid(''))
    
    def test_single_open_bracket(self):
        """Test with single open bracket"""
        self.assertFalse(is_valid('('))
        self.assertFalse(is_valid('['))
        self.assertFalse(is_valid('{'))
    
    def test_single_close_bracket(self):
        """Test with single close bracket"""
        self.assertFalse(is_valid(')'))
        self.assertFalse(is_valid(']'))
        self.assertFalse(is_valid('}'))
    
    def test_very_long_valid_string(self):
        """Test with very long valid string"""
        long_string = '()' * 1000
        self.assertTrue(is_valid(long_string))
    
    def test_very_long_nested_string(self):
        """Test with very long nested string"""
        long_string = '(' * 500 + ')' * 500
        self.assertTrue(is_valid(long_string))
    
    def test_alternating_types(self):
        """Test with alternating bracket types"""
        self.assertTrue(is_valid('([]){}'))
        self.assertFalse(is_valid('([)]'))
    
    # INVALID INPUT TESTS
    def test_non_string_input_integer(self):
        """Test with integer input"""
        with self.assertRaises(TypeError):
            is_valid(123)
    
    def test_non_string_input_list(self):
        """Test with list input"""
        with self.assertRaises(TypeError):
            is_valid(['(', ')'])
    
    def test_non_string_input_none(self):
        """Test with None input"""
        with self.assertRaises(TypeError):
            is_valid(None)
    
    def test_non_string_input_dict(self):
        """Test with dictionary input"""
        with self.assertRaises(TypeError):
            is_valid({'(': ')'})


class TestNumTrees(unittest.TestCase):
    """Test cases for num_trees (Unique Binary Search Trees) function"""
    
    # VALID TESTS
    def test_basic_cases(self):
        """Test basic cases from examples"""
        self.assertEqual(num_trees(3), 5)
        self.assertEqual(num_trees(1), 1)
    
    def test_small_values(self):
        """Test small values"""
        self.assertEqual(num_trees(0), 1)
        self.assertEqual(num_trees(2), 2)
        self.assertEqual(num_trees(4), 14)
        self.assertEqual(num_trees(5), 42)
    
    def test_catalan_numbers(self):
        """Test against known Catalan numbers"""
        # Catalan numbers: 1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862
        expected = [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862]
        for n, expected_val in enumerate(expected):
            self.assertEqual(num_trees(n), expected_val)
    
    def test_larger_values(self):
        """Test larger values"""
        self.assertEqual(num_trees(10), 16796)
        self.assertEqual(num_trees(12), 208012)
    
    # BOUNDARY TESTS
    def test_zero(self):
        """Test with n=0"""
        self.assertEqual(num_trees(0), 1)
    
    def test_one(self):
        """Test with n=1"""
        self.assertEqual(num_trees(1), 1)
    
    def test_large_n(self):
        """Test with larger n"""
        result = num_trees(15)
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)
    
    # INVALID INPUT TESTS
    def test_negative_integer(self):
        """Test with negative integer"""
        with self.assertRaises(ValueError):
            num_trees(-1)
    
    def test_non_integer_float(self):
        """Test with float input"""
        with self.assertRaises(TypeError):
            num_trees(3.5)
    
    def test_non_integer_string(self):
        """Test with string input"""
        with self.assertRaises(TypeError):
            num_trees("3")
    
    def test_non_integer_none(self):
        """Test with None input"""
        with self.assertRaises(TypeError):
            num_trees(None)
    
    def test_non_integer_list(self):
        """Test with list input"""
        with self.assertRaises(TypeError):
            num_trees([3])
    
    def test_boolean_input(self):
        """Test with boolean input"""
        with self.assertRaises(TypeError):
            num_trees(True)


class TestLengthOfLIS(unittest.TestCase):
    """Test cases for length_of_lis (Longest Increasing Subsequence) function"""
    
    # VALID TESTS
    def test_basic_cases(self):
        """Test basic cases from examples"""
        self.assertEqual(length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]), 4)
        self.assertEqual(length_of_lis([0, 1, 0, 3, 2, 3]), 4)
    
    def test_already_sorted(self):
        """Test with already sorted array"""
        self.assertEqual(length_of_lis([1, 2, 3, 4, 5]), 5)
        self.assertEqual(length_of_lis([1, 2, 3]), 3)
    
    def test_reverse_sorted(self):
        """Test with reverse sorted array"""
        self.assertEqual(length_of_lis([5, 4, 3, 2, 1]), 1)
        self.assertEqual(length_of_lis([3, 2, 1]), 1)
    
    def test_all_same_elements(self):
        """Test with all same elements"""
        self.assertEqual(length_of_lis([7, 7, 7, 7]), 1)
        self.assertEqual(length_of_lis([1, 1, 1]), 1)
    
    def test_alternating_values(self):
        """Test with alternating values"""
        self.assertEqual(length_of_lis([1, 3, 2, 4, 3, 5]), 4)  # 1,2,3,5 or 1,3,4,5 etc
    
    def test_with_negative_numbers(self):
        """Test with negative numbers"""
        self.assertEqual(length_of_lis([-2, -1, 0, 1, 2]), 5)
        self.assertEqual(length_of_lis([-5, -3, -1, 0, 2]), 5)
    
    def test_mixed_positive_negative(self):
        """Test with mixed positive and negative"""
        self.assertEqual(length_of_lis([-1, 3, -2, 4, 5]), 4)  # -1,3,4,5 or -2,4,5 etc
    
    # BOUNDARY TESTS
    def test_empty_array(self):
        """Test with empty array"""
        self.assertEqual(length_of_lis([]), 0)
    
    def test_single_element(self):
        """Test with single element"""
        self.assertEqual(length_of_lis([5]), 1)
        self.assertEqual(length_of_lis([0]), 1)
    
    def test_two_elements_increasing(self):
        """Test with two increasing elements"""
        self.assertEqual(length_of_lis([1, 2]), 2)
    
    def test_two_elements_decreasing(self):
        """Test with two decreasing elements"""
        self.assertEqual(length_of_lis([2, 1]), 1)
    
    def test_two_equal_elements(self):
        """Test with two equal elements"""
        self.assertEqual(length_of_lis([1, 1]), 1)
    
    def test_large_array(self):
        """Test with large array"""
        large_array = list(range(100))
        self.assertEqual(length_of_lis(large_array), 100)
    
    def test_large_reverse_array(self):
        """Test with large reverse array"""
        large_reverse = list(range(100, 0, -1))
        self.assertEqual(length_of_lis(large_reverse), 1)
    
    # INVALID INPUT TESTS
    def test_non_list_input_integer(self):
        """Test with integer input"""
        with self.assertRaises(TypeError):
            length_of_lis(123)
    
    def test_non_list_input_string(self):
        """Test with string input"""
        with self.assertRaises(TypeError):
            length_of_lis("123")
    
    def test_non_list_input_none(self):
        """Test with None input"""
        with self.assertRaises(TypeError):
            length_of_lis(None)
    
    def test_list_with_non_integer_string(self):
        """Test with list containing strings"""
        with self.assertRaises(TypeError):
            length_of_lis([1, "2", 3])
    
    def test_list_with_non_integer_float(self):
        """Test with list containing floats"""
        with self.assertRaises(TypeError):
            length_of_lis([1.5, 2.5, 3.5])
    
    def test_list_with_none(self):
        """Test with list containing None"""
        with self.assertRaises(TypeError):
            length_of_lis([1, None, 3])


class TestFindMedianSortedArrays(unittest.TestCase):
    """Test cases for find_median_sorted_arrays function"""
    
    # VALID TESTS
    def test_basic_cases(self):
        """Test basic cases from examples"""
        self.assertEqual(find_median_sorted_arrays([1, 3], [2]), 2.0)
        self.assertEqual(find_median_sorted_arrays([1, 2], [3, 4]), 2.5)
    
    def test_one_empty_array(self):
        """Test with one empty array"""
        self.assertEqual(find_median_sorted_arrays([], [1]), 1.0)
        self.assertEqual(find_median_sorted_arrays([2], []), 2.0)
        self.assertEqual(find_median_sorted_arrays([], [1, 2, 3]), 2.0)
    
    def test_different_sizes(self):
        """Test with arrays of different sizes"""
        self.assertEqual(find_median_sorted_arrays([1, 2], [3, 4, 5, 6]), 3.5)
        self.assertEqual(find_median_sorted_arrays([1], [2, 3, 4, 5, 6]), 3.5)
    
    def test_overlapping_arrays(self):
        """Test with overlapping value ranges"""
        self.assertEqual(find_median_sorted_arrays([1, 3, 5], [2, 4, 6]), 3.5)
        self.assertEqual(find_median_sorted_arrays([1, 2, 3], [1, 2, 3]), 2.0)
    
    def test_non_overlapping_arrays(self):
        """Test with non-overlapping arrays"""
        self.assertEqual(find_median_sorted_arrays([1, 2], [5, 6]), 3.5)
        self.assertEqual(find_median_sorted_arrays([1, 2, 3], [7, 8, 9]), 5.0)
    
    def test_with_negative_numbers(self):
        """Test with negative numbers"""
        self.assertEqual(find_median_sorted_arrays([-5, -3, -1], [0, 2, 4]), -0.5)
        self.assertEqual(find_median_sorted_arrays([-2, -1], [0, 1]), -0.5)
    
    def test_with_duplicates(self):
        """Test with duplicate values"""
        self.assertEqual(find_median_sorted_arrays([1, 1, 1], [1, 1, 1]), 1.0)
        self.assertEqual(find_median_sorted_arrays([1, 2, 2], [2, 3, 3]), 2.0)
    
    # BOUNDARY TESTS
    def test_single_element_each(self):
        """Test with single element in each array"""
        self.assertEqual(find_median_sorted_arrays([1], [2]), 1.5)
        self.assertEqual(find_median_sorted_arrays([1], [1]), 1.0)
    
    def test_two_elements_total(self):
        """Test with two elements total"""
        self.assertEqual(find_median_sorted_arrays([1], [3]), 2.0)
    
    def test_odd_total_elements(self):
        """Test with odd total number of elements"""
        self.assertEqual(find_median_sorted_arrays([1, 2], [3]), 2.0)
        self.assertEqual(find_median_sorted_arrays([1], [2, 3]), 2.0)
    
    def test_large_arrays(self):
        """Test with large arrays"""
        nums1 = list(range(0, 1000, 2))  # Even numbers
        nums2 = list(range(1, 1001, 2))  # Odd numbers
        self.assertEqual(find_median_sorted_arrays(nums1, nums2), 499.5)
    
    def test_both_empty_arrays(self):
        """Test with both arrays empty (should raise error)"""
        with self.assertRaises(ValueError):
            find_median_sorted_arrays([], [])
    
    # INVALID INPUT TESTS
    def test_non_list_input_first(self):
        """Test with non-list first input"""
        with self.assertRaises(TypeError):
            find_median_sorted_arrays(123, [1, 2])
    
    def test_non_list_input_second(self):
        """Test with non-list second input"""
        with self.assertRaises(TypeError):
            find_median_sorted_arrays([1, 2], "123")
    
    def test_non_list_input_both(self):
        """Test with non-list both inputs"""
        with self.assertRaises(TypeError):
            find_median_sorted_arrays(None, None)
    
    def test_list_with_non_numeric_string(self):
        """Test with list containing strings"""
        with self.assertRaises(TypeError):
            find_median_sorted_arrays([1, "2"], [3])
    
    def test_list_with_none(self):
        """Test with list containing None"""
        with self.assertRaises(TypeError):
            find_median_sorted_arrays([1, None], [3])
    
    def test_list_with_boolean(self):
        """Test with list containing boolean"""
        with self.assertRaises(TypeError):
            find_median_sorted_arrays([1, True], [3])


class TestMaxPathSum(unittest.TestCase):
    """Test cases for max_path_sum (Binary Tree Maximum Path Sum) function"""
    
    # VALID TESTS
    def test_basic_cases(self):
        """Test basic cases from examples"""
        # [1,2,3] -> tree with 1 as root, 2 left, 3 right
        root1 = build_tree_from_list([1, 2, 3])
        self.assertEqual(max_path_sum(root1), 6)
        
        # [-10,9,20,null,null,15,7]
        root2 = build_tree_from_list([-10, 9, 20, None, None, 15, 7])
        self.assertEqual(max_path_sum(root2), 42)
    
    def test_single_node(self):
        """Test with single node"""
        root = TreeNode(5)
        self.assertEqual(max_path_sum(root), 5)
        
        root_neg = TreeNode(-3)
        self.assertEqual(max_path_sum(root_neg), -3)
    
    def test_all_positive(self):
        """Test with all positive values"""
        root = build_tree_from_list([1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(max_path_sum(root), 18)  # 4+2+1+3+7 or similar
    
    def test_all_negative(self):
        """Test with all negative values"""
        root = build_tree_from_list([-1, -2, -3])
        self.assertEqual(max_path_sum(root), -1)  # Just the root
    
    def test_mixed_values(self):
        """Test with mixed positive and negative"""
        root = build_tree_from_list([2, -1, -2])
        self.assertEqual(max_path_sum(root), 2)
    
    def test_left_skewed_tree(self):
        """Test with left-skewed tree"""
        root = TreeNode(1)
        root.left = TreeNode(2)
        root.left.left = TreeNode(3)
        self.assertEqual(max_path_sum(root), 6)  # 1+2+3
    
    def test_right_skewed_tree(self):
        """Test with right-skewed tree"""
        root = TreeNode(1)
        root.right = TreeNode(2)
        root.right.right = TreeNode(3)
        self.assertEqual(max_path_sum(root), 6)  # 1+2+3
    
    def test_negative_root_positive_children(self):
        """Test with negative root but positive children"""
        root = build_tree_from_list([-10, 9, 20])
        self.assertEqual(max_path_sum(root), 20)  # Just 20, or 9 + (-10) + 20 = 19
    
    # BOUNDARY TESTS
    def test_two_nodes_positive(self):
        """Test with two positive nodes"""
        root = TreeNode(1)
        root.left = TreeNode(2)
        self.assertEqual(max_path_sum(root), 3)
    
    def test_two_nodes_negative(self):
        """Test with two negative nodes"""
        root = TreeNode(-1)
        root.left = TreeNode(-2)
        self.assertEqual(max_path_sum(root), -1)
    
    def test_large_values(self):
        """Test with large values"""
        root = build_tree_from_list([1000, 1000, 1000])
        self.assertEqual(max_path_sum(root), 3000)
    
    def test_zero_values(self):
        """Test with zero values"""
        root = build_tree_from_list([0, 0, 0])
        self.assertEqual(max_path_sum(root), 0)
    
    def test_path_not_through_root(self):
        """Test when max path doesn't go through root"""
        root = build_tree_from_list([-100, 50, 50, 25, 25, 25, 25])
        # Max path is in one of the subtrees
        self.assertGreater(max_path_sum(root), 0)
    
    # INVALID INPUT TESTS
    def test_none_input(self):
        """Test with None input"""
        with self.assertRaises(ValueError):
            max_path_sum(None)
    
    def test_non_treenode_input_integer(self):
        """Test with integer input"""
        with self.assertRaises(TypeError):
            max_path_sum(123)
    
    def test_non_treenode_input_list(self):
        """Test with list input"""
        with self.assertRaises(TypeError):
            max_path_sum([1, 2, 3])
    
    def test_non_treenode_input_string(self):
        """Test with string input"""
        with self.assertRaises(TypeError):
            max_path_sum("tree")
    
    def test_non_treenode_input_dict(self):
        """Test with dictionary input"""
        with self.assertRaises(TypeError):
            max_path_sum({'val': 1, 'left': None, 'right': None})


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)
