import unittest

STRING_VALUE = "Input must be a string"


# Task implementations (to be tested)
def count_vowels(s: str) -> int:
    """Count the number of vowels (a, e, i, o, u) in the input string, case-insensitive."""
    if not isinstance(s, str):
        raise TypeError(STRING_VALUE)
    vowels = set("aeiouAEIOU")
    return sum(1 for char in s if char in vowels)


def is_palindrome(s: str) -> bool:
    """Check if the input string is a palindrome (reads the same forwards and backwards), ignoring spaces, punctuation, and case."""
    if not isinstance(s, str):
        raise TypeError(STRING_VALUE)
    cleaned = "".join(char.lower() for char in s if char.isalnum())
    return cleaned == cleaned[::-1]


def compress_string(s: str) -> str:
    """Compress the string using run-length encoding. For example, 'aaabbbcc' becomes 'a3b3c2'. If the compressed string is not shorter than the original, return the original string."""
    if not isinstance(s, str):
        raise TypeError(STRING_VALUE)
    if not s:
        return s

    compressed = []
    count = 1
    current_char = s[0]

    for i in range(1, len(s)):
        if s[i] == current_char:
            count += 1
        else:
            compressed.append(current_char + str(count))
            current_char = s[i]
            count = 1

    compressed.append(current_char + str(count))
    result = "".join(compressed)

    return result if len(result) < len(s) else s


def longest_substring_without_repeating(s: str) -> int:
    """Find the length of the longest substring without repeating characters."""
    if not isinstance(s, str):
        raise TypeError(STRING_VALUE)
    char_map = {}
    left = 0
    max_length = 0

    for right in range(len(s)):
        if s[right] in char_map and char_map[s[right]] >= left:
            left = char_map[s[right]] + 1

        char_map[s[right]] = right
        max_length = max(max_length, right - left + 1)

    return max_length


def group_anagrams(strs: list[str]) -> list[list[str]]:
    """Group strings that are anagrams of each other. Return a list of lists where each inner list contains anagrams."""
    if not isinstance(strs, list):
        raise TypeError("Input must be a list")
    if not all(isinstance(s, str) for s in strs):
        raise TypeError("All elements in the list must be strings")
    anagram_groups = {}

    for word in strs:
        sorted_word = "".join(sorted(word))
        if sorted_word not in anagram_groups:
            anagram_groups[sorted_word] = []
        anagram_groups[sorted_word].append(word)

    return list(anagram_groups.values())


# ============================================================================
# TEST CLASSES
# ============================================================================


class TestCountVowels(unittest.TestCase):
    """Test cases for count_vowels function"""

    # VALID TESTS
    def test_basic_lowercase_vowels(self):
        """Test with basic lowercase string"""
        self.assertEqual(count_vowels("hello"), 2)

    def test_basic_uppercase_vowels(self):
        """Test with uppercase vowels"""
        self.assertEqual(count_vowels("HELLO"), 2)

    def test_mixed_case(self):
        """Test with mixed case string"""
        self.assertEqual(count_vowels("OpenAI ChatGPT"), 5)
        self.assertEqual(count_vowels("Hello World"), 3)

    def test_all_vowels(self):
        """Test string with all vowels"""
        self.assertEqual(count_vowels("aeiou"), 5)
        self.assertEqual(count_vowels("AEIOU"), 5)

    def test_no_vowels(self):
        """Test string with no vowels"""
        self.assertEqual(count_vowels("bcdfg"), 0)
        self.assertEqual(count_vowels("xyz"), 0)

    def test_with_numbers_and_special_chars(self):
        """Test string with numbers and special characters"""
        self.assertEqual(count_vowels("abc123!@#"), 1)
        self.assertEqual(count_vowels("a1e2i3o4u5"), 5)

    # BOUNDARY TESTS
    def test_empty_string(self):
        """Test with empty string"""
        self.assertEqual(count_vowels(""), 0)

    def test_single_vowel(self):
        """Test with single vowel"""
        self.assertEqual(count_vowels("a"), 1)
        self.assertEqual(count_vowels("E"), 1)

    def test_single_consonant(self):
        """Test with single consonant"""
        self.assertEqual(count_vowels("b"), 0)

    def test_very_long_string(self):
        """Test with very long string"""
        long_string = "a" * 1000 + "b" * 1000
        self.assertEqual(count_vowels(long_string), 1000)

    def test_only_spaces(self):
        """Test with only spaces"""
        self.assertEqual(count_vowels("     "), 0)

    def test_repeated_vowels(self):
        """Test with repeated vowels"""
        self.assertEqual(count_vowels("aaaaaeeeeeiiiiiooooouuuuu"), 25)

    # INVALID INPUT TESTS
    def test_non_string_input_integer(self):
        """Test with integer input"""
        with self.assertRaises(TypeError):
            count_vowels(123)

    def test_non_string_input_list(self):
        """Test with list input"""
        with self.assertRaises(TypeError):
            count_vowels(["a", "e", "i"])

    def test_non_string_input_none(self):
        """Test with None input"""
        with self.assertRaises(TypeError):
            count_vowels(None)

    def test_non_string_input_dict(self):
        """Test with dictionary input"""
        with self.assertRaises(TypeError):
            count_vowels({"a": 1})


class TestIsPalindrome(unittest.TestCase):
    """Test cases for is_palindrome function"""

    # VALID TESTS
    def test_simple_palindrome(self):
        """Test simple palindrome"""
        self.assertTrue(is_palindrome("racecar"))
        self.assertTrue(is_palindrome("level"))

    def test_palindrome_with_spaces(self):
        """Test palindrome with spaces"""
        self.assertTrue(is_palindrome("A man a plan a canal Panama"))
        self.assertTrue(is_palindrome("race car"))

    def test_palindrome_with_punctuation(self):
        """Test palindrome with punctuation"""
        self.assertTrue(is_palindrome("A man, a plan, a canal: Panama"))
        self.assertTrue(is_palindrome("Madam, I'm Adam"))

    def test_palindrome_case_insensitive(self):
        """Test palindrome is case insensitive"""
        self.assertTrue(is_palindrome("RaceCar"))
        self.assertTrue(is_palindrome("AbA"))

    def test_not_palindrome(self):
        """Test strings that are not palindromes"""
        self.assertFalse(is_palindrome("hello"))
        self.assertFalse(is_palindrome("python"))
        self.assertFalse(is_palindrome("world"))

    def test_numeric_palindrome(self):
        """Test palindrome with numbers"""
        self.assertTrue(is_palindrome("12321"))
        self.assertFalse(is_palindrome("12345"))

    # BOUNDARY TESTS
    def test_empty_string(self):
        """Test with empty string (considered palindrome)"""
        self.assertTrue(is_palindrome(""))

    def test_single_character(self):
        """Test with single character"""
        self.assertTrue(is_palindrome("a"))
        self.assertTrue(is_palindrome("Z"))

    def test_two_same_characters(self):
        """Test with two same characters"""
        self.assertTrue(is_palindrome("aa"))
        self.assertTrue(is_palindrome("BB"))

    def test_two_different_characters(self):
        """Test with two different characters"""
        self.assertFalse(is_palindrome("ab"))

    def test_only_special_characters(self):
        """Test with only special characters and spaces"""
        self.assertTrue(is_palindrome("!!!"))
        self.assertTrue(is_palindrome("!@#@!"))

    def test_very_long_palindrome(self):
        """Test with very long palindrome"""
        long_palindrome = "a" * 1000 + "b" + "a" * 1000
        self.assertTrue(is_palindrome(long_palindrome))

    def test_almost_palindrome(self):
        """Test strings that are almost palindromes"""
        self.assertFalse(is_palindrome("racecat"))
        self.assertFalse(is_palindrome("abccbd"))

    # INVALID INPUT TESTS
    def test_non_string_input_integer(self):
        """Test with integer input"""
        with self.assertRaises(TypeError):
            is_palindrome(12321)

    def test_non_string_input_list(self):
        """Test with list input"""
        with self.assertRaises(TypeError):
            is_palindrome(["r", "a", "c", "e", "c", "a", "r"])

    def test_non_string_input_none(self):
        """Test with None input"""
        with self.assertRaises(TypeError):
            is_palindrome(None)

    def test_non_string_input_boolean(self):
        """Test with boolean input"""
        with self.assertRaises(TypeError):
            is_palindrome(True)


class TestCompressString(unittest.TestCase):
    """Test cases for compress_string function"""

    # VALID TESTS
    def test_basic_compression(self):
        """Test basic string compression"""
        self.assertEqual(compress_string("aaabbbcc"), "a3b3c2")
        self.assertEqual(compress_string("aaaabbbbccc"), "a4b4c3")

    def test_no_compression_benefit(self):
        """Test when compression doesn't make string shorter"""
        self.assertEqual(compress_string("abcd"), "abcd")
        self.assertEqual(compress_string("abc"), "abc")

    def test_single_character_repeated(self):
        """Test with single character repeated"""
        self.assertEqual(compress_string("aaaaa"), "a5")
        self.assertEqual(compress_string("bbbbbb"), "b6")

    def test_alternating_characters(self):
        """Test with alternating characters"""
        self.assertEqual(compress_string("ababab"), "ababab")

    def test_long_runs(self):
        """Test with long character runs"""
        self.assertEqual(compress_string("aaaaaaaaaa"), "a10")
        self.assertEqual(compress_string("aaaaabbbbbccccc"), "a5b5c5")

    def test_mixed_run_lengths(self):
        """Test with different run lengths"""
        self.assertEqual(compress_string("aaabcccccddddde"), "a3b1c5d5e1")

    # BOUNDARY TESTS
    def test_empty_string(self):
        """Test with empty string"""
        self.assertEqual(compress_string(""), "")

    def test_single_character(self):
        """Test with single character"""
        self.assertEqual(compress_string("a"), "a")

    def test_two_same_characters(self):
        """Test with two same characters"""
        self.assertEqual(compress_string("aa"), "aa")  # 'a2' is same length

    def test_two_different_characters(self):
        """Test with two different characters"""
        self.assertEqual(compress_string("ab"), "ab")

    def test_all_unique_characters(self):
        """Test with all unique characters"""
        self.assertEqual(compress_string("abcdefgh"), "abcdefgh")

    def test_very_long_run(self):
        """Test with very long character run"""
        long_string = "a" * 100
        self.assertEqual(compress_string(long_string), "a100")

    def test_uppercase_characters(self):
        """Test with uppercase characters"""
        self.assertEqual(compress_string("AAABBB"), "A3B3")

    # INVALID INPUT TESTS
    def test_non_string_input_integer(self):
        """Test with integer input"""
        with self.assertRaises(TypeError):
            compress_string(12345)

    def test_non_string_input_list(self):
        """Test with list input"""
        with self.assertRaises(TypeError):
            compress_string(["a", "a", "a"])

    def test_non_string_input_none(self):
        """Test with None input"""
        with self.assertRaises(TypeError):
            compress_string(None)

    def test_non_string_input_tuple(self):
        """Test with tuple input"""
        with self.assertRaises(TypeError):
            compress_string(("a", "b", "c"))


class TestLongestSubstringWithoutRepeating(unittest.TestCase):
    """Test cases for longest_substring_without_repeating function"""

    # VALID TESTS
    def test_basic_case(self):
        """Test basic cases"""
        self.assertEqual(longest_substring_without_repeating("abcabcbb"), 3)  # 'abc'
        self.assertEqual(longest_substring_without_repeating("pwwkew"), 3)  # 'wke'

    def test_all_same_character(self):
        """Test with all same characters"""
        self.assertEqual(longest_substring_without_repeating("bbbbb"), 1)
        self.assertEqual(longest_substring_without_repeating("aaaa"), 1)

    def test_all_unique_characters(self):
        """Test with all unique characters"""
        self.assertEqual(longest_substring_without_repeating("abcdef"), 6)
        self.assertEqual(longest_substring_without_repeating("xyz"), 3)

    def test_repeated_at_different_positions(self):
        """Test with characters repeated at different positions"""
        self.assertEqual(longest_substring_without_repeating("abcabcbb"), 3)
        self.assertEqual(longest_substring_without_repeating("dvdf"), 3)  # 'vdf'

    def test_with_spaces(self):
        """Test with spaces"""
        self.assertEqual(
            longest_substring_without_repeating("a b c a"), 3
        )  # ' b c a' or 'a b c '

    def test_with_special_characters(self):
        """Test with special characters"""
        self.assertEqual(longest_substring_without_repeating("a!b@c#"), 6)
        self.assertEqual(longest_substring_without_repeating("a!b!c"), 3)

    # BOUNDARY TESTS
    def test_empty_string(self):
        """Test with empty string"""
        self.assertEqual(longest_substring_without_repeating(""), 0)

    def test_single_character(self):
        """Test with single character"""
        self.assertEqual(longest_substring_without_repeating("a"), 1)

    def test_two_same_characters(self):
        """Test with two same characters"""
        self.assertEqual(longest_substring_without_repeating("aa"), 1)

    def test_two_different_characters(self):
        """Test with two different characters"""
        self.assertEqual(longest_substring_without_repeating("ab"), 2)

    def test_very_long_string_all_unique(self):
        """Test with very long string of unique characters"""
        import string

        long_unique = string.ascii_lowercase + string.ascii_uppercase + string.digits
        self.assertEqual(
            longest_substring_without_repeating(long_unique), len(long_unique)
        )

    def test_longest_at_beginning(self):
        """Test when longest substring is at the beginning"""
        self.assertEqual(longest_substring_without_repeating("abcabcbb"), 3)

    def test_longest_at_end(self):
        """Test when longest substring is at the end"""
        self.assertEqual(longest_substring_without_repeating("aaabcdef"), 6)

    def test_longest_in_middle(self):
        """Test when longest substring is in the middle"""
        self.assertEqual(longest_substring_without_repeating("abcdefgaaaaa"), 7)

    # INVALID INPUT TESTS
    def test_non_string_input_integer(self):
        """Test with integer input"""
        with self.assertRaises(TypeError):
            longest_substring_without_repeating(123456)

    def test_non_string_input_list(self):
        """Test with list input"""
        with self.assertRaises(TypeError):
            longest_substring_without_repeating(["a", "b", "c"])

    def test_non_string_input_none(self):
        """Test with None input"""
        with self.assertRaises(TypeError):
            longest_substring_without_repeating(None)

    def test_non_string_input_float(self):
        """Test with float input"""
        with self.assertRaises(TypeError):
            longest_substring_without_repeating(3.14)


class TestGroupAnagrams(unittest.TestCase):
    """Test cases for group_anagrams function"""

    # VALID TESTS
    def test_basic_anagrams(self):
        """Test basic anagram grouping"""
        result = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
        # Sort each group and sort groups for comparison
        result_sorted = [sorted(group) for group in result]
        result_sorted.sort()
        expected = [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
        expected_sorted = [sorted(group) for group in expected]
        expected_sorted.sort()
        self.assertEqual(result_sorted, expected_sorted)

    def test_no_anagrams(self):
        """Test when there are no anagrams"""
        result = group_anagrams(["abc", "def", "ghi"])
        self.assertEqual(len(result), 3)
        self.assertTrue(all(len(group) == 1 for group in result))

    def test_all_anagrams(self):
        """Test when all strings are anagrams"""
        result = group_anagrams(["abc", "bca", "cab"])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 3)

    def test_different_length_strings(self):
        """Test with strings of different lengths"""
        result = group_anagrams(["a", "ab", "ba", "abc", "bca"])
        result_sorted = [sorted(group) for group in result]
        result_sorted.sort()
        # 'a' alone, 'ab' and 'ba' together, 'abc' and 'bca' together
        self.assertEqual(len(result), 3)

    def test_case_sensitive(self):
        """Test that grouping is case sensitive"""
        result = group_anagrams(["Ab", "bA", "ab", "ba"])
        # 'Ab' and 'bA' are anagrams, 'ab' and 'ba' are anagrams
        self.assertEqual(len(result), 2)

    def test_with_spaces(self):
        """Test strings with spaces"""
        result = group_anagrams(["a b", "b a", "ab", "ba"])
        # Each pair should be grouped differently
        self.assertEqual(len(result), 2)

    # BOUNDARY TESTS
    def test_empty_list(self):
        """Test with empty list"""
        result = group_anagrams([])
        self.assertEqual(result, [])

    def test_single_empty_string(self):
        """Test with single empty string"""
        result = group_anagrams([""])
        self.assertEqual(result, [[""]])

    def test_multiple_empty_strings(self):
        """Test with multiple empty strings"""
        result = group_anagrams(["", "", ""])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 3)

    def test_single_string(self):
        """Test with single string"""
        result = group_anagrams(["a"])
        self.assertEqual(result, [["a"]])

    def test_single_character_strings(self):
        """Test with multiple single character strings"""
        result = group_anagrams(["a", "b", "c", "a", "b"])
        result_sorted = [sorted(group) for group in result]
        result_sorted.sort()
        # 'a' appears twice, 'b' appears twice, 'c' once
        expected = [["a", "a"], ["b", "b"], ["c"]]
        expected_sorted = [sorted(group) for group in expected]
        expected_sorted.sort()
        self.assertEqual(result_sorted, expected_sorted)

    def test_very_long_strings(self):
        """Test with very long strings"""
        long1 = "a" * 100 + "b" * 100
        long2 = "b" * 100 + "a" * 100
        result = group_anagrams([long1, long2])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 2)

    def test_duplicate_strings(self):
        """Test with duplicate strings"""
        result = group_anagrams(["abc", "abc", "abc"])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 3)

    def test_numbers_in_strings(self):
        """Test with numbers in strings"""
        result = group_anagrams(["a1b", "b1a", "ab1", "1ab"])
        # All should be in the same group
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 4)

    # INVALID INPUT TESTS
    def test_non_list_input_string(self):
        """Test with string input instead of list"""
        with self.assertRaises(TypeError):
            group_anagrams("abc")

    def test_non_list_input_integer(self):
        """Test with integer input instead of list"""
        with self.assertRaises(TypeError):
            group_anagrams(123)

    def test_non_list_input_none(self):
        """Test with None input"""
        with self.assertRaises(TypeError):
            group_anagrams(None)

    def test_list_with_non_string_elements_integers(self):
        """Test with list containing integers"""
        with self.assertRaises(TypeError):
            group_anagrams(["abc", 123, "def"])

    def test_list_with_non_string_elements_mixed(self):
        """Test with list containing mixed non-string types"""
        with self.assertRaises(TypeError):
            group_anagrams(["abc", None, ["def"], "ghi"])

    def test_list_with_all_non_string_elements(self):
        """Test with list containing only non-string elements"""
        with self.assertRaises(TypeError):
            group_anagrams([1, 2, 3, 4])


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
