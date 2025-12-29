from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def max_path_sum_helper(node: Optional[TreeNode]) -> (int, int):
    if node is None:
        return (0, 0)
    
    left_incl, left_excl = max_path_sum_helper(node.left)
    right_incl, right_excl = max_path_sum_helper(node.right)
    
    incl = node.val + max(0, left_incl) + max(0, right_incl)
    excl = max(left_incl, left_excl) + max(right_incl, right_excl)
    
    return (incl, excl)

def maxPathSum(root: Optional[TreeNode]) -> int:
    if root is None:
        return 0
    
    incl, excl = max_path_sum_helper(root)
    return max(incl, excl)