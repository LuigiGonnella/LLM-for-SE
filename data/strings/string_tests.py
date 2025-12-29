import pytest

STRING_VALUE = "Input must be a string"


# ============================================================================
# TEST FUNCTIONS - COUNT VOWELS
# ============================================================================


def count_vowels(s: str) -> int:
    """Count the number of vowels (a, e, i, o, u) in the input string, case-insensitive."""
    if not isinstance(s, str):
        raise TypeError(STRING_VALUE)
    vowels = set("aeiouAEIOU")
    return sum(1 for char in s if char in vowels)


class TestCountVowels:
    def test_basic_lowercase(self):
        assert count_vowels("hello") == 2

    def test_basic_uppercase(self):
        assert count_vowels("HELLO") == 2

    def test_mixed_case(self):
        assert count_vowels("OpenAI ChatGPT") == 5
        assert count_vowels("Hello World") == 3

    def test_all_vowels(self):
        assert count_vowels("aeiou") == 5
        assert count_vowels("AEIOU") == 5

    def test_no_vowels(self):
        assert count_vowels("bcdfg") == 0
        assert count_vowels("xyz") == 0

    def test_numbers_and_special_chars(self):
        assert count_vowels("abc123!@#") == 1
        assert count_vowels("a1e2i3o4u5") == 5

    def test_empty_string(self):
        assert count_vowels("") == 0

    def test_single_vowel(self):
        assert count_vowels("a") == 1
        assert count_vowels("E") == 1

    def test_single_consonant(self):
        assert count_vowels("b") == 0

    def test_very_long_string(self):
        long_string = "a" * 1000 + "b" * 1000
        assert count_vowels(long_string) == 1000

    def test_only_spaces(self):
        assert count_vowels("     ") == 0

    def test_repeated_vowels(self):
        assert count_vowels("aaaaaeeeeeiiiiiooooouuuuu") == 25

    def test_non_string_input_integer(self):
        with pytest.raises(TypeError):
            count_vowels(123)

    def test_non_string_input_list(self):
        with pytest.raises(TypeError):
            count_vowels(["a", "e", "i"])

    def test_non_string_input_none(self):
        with pytest.raises(TypeError):
            count_vowels(None)

    def test_non_string_input_dict(self):
        with pytest.raises(TypeError):
            count_vowels({"a": 1})


# ============================================================================
# TEST FUNCTIONS - IS PALINDROME
# ============================================================================


def is_palindrome(s: str) -> bool:
    """Check if the input string is a palindrome (reads the same forwards and backwards), ignoring spaces, punctuation, and case."""
    if not isinstance(s, str):
        raise TypeError(STRING_VALUE)
    cleaned = "".join(char.lower() for char in s if char.isalnum())
    return cleaned == cleaned[::-1]


class TestIsPalindrome:
    def test_simple(self):
        assert is_palindrome("racecar") is True
        assert is_palindrome("level") is True

    def test_with_spaces(self):
        assert is_palindrome("A man a plan a canal Panama") is True
        assert is_palindrome("race car") is True

    def test_with_punctuation(self):
        assert is_palindrome("A man, a plan, a canal: Panama") is True
        assert is_palindrome("Madam, I'm Adam") is True

    def test_case_insensitive(self):
        assert is_palindrome("RaceCar") is True
        assert is_palindrome("AbA") is True

    def test_not_palindrome(self):
        assert is_palindrome("hello") is False
        assert is_palindrome("python") is False
        assert is_palindrome("world") is False

    def test_numeric(self):
        assert is_palindrome("12321") is True
        assert is_palindrome("12345") is False

    def test_empty_string(self):
        assert is_palindrome("") is True

    def test_single_character(self):
        assert is_palindrome("a") is True
        assert is_palindrome("Z") is True

    def test_two_same_characters(self):
        assert is_palindrome("aa") is True
        assert is_palindrome("BB") is True

    def test_two_different_characters(self):
        assert is_palindrome("ab") is False

    def test_only_special_characters(self):
        assert is_palindrome("!!!") is True
        assert is_palindrome("!@#@!") is True

    def test_very_long_palindrome(self):
        long_palindrome = "a" * 1000 + "b" + "a" * 1000
        assert is_palindrome(long_palindrome) is True

    def test_almost_palindrome(self):
        assert is_palindrome("racecat") is False
        assert is_palindrome("abccbd") is False

    def test_non_string_input_integer(self):
        with pytest.raises(TypeError):
            is_palindrome(12321)

    def test_non_string_input_list(self):
        with pytest.raises(TypeError):
            is_palindrome(["r", "a", "c", "e", "c", "a", "r"])

    def test_non_string_input_none(self):
        with pytest.raises(TypeError):
            is_palindrome(None)

    def test_non_string_input_boolean(self):
        with pytest.raises(TypeError):
            is_palindrome(True)


# ============================================================================
# TEST FUNCTIONS - COMPRESS STRING
# ============================================================================


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


class TestCompressString:
    def test_basic(self):
        assert compress_string("aaabbbcc") == "a3b3c2"
        assert compress_string("aaaabbbbccc") == "a4b4c3"

    def test_no_compression_benefit(self):
        assert compress_string("abcd") == "abcd"
        assert compress_string("abc") == "abc"

    def test_single_character_repeated(self):
        assert compress_string("aaaaa") == "a5"
        assert compress_string("bbbbbb") == "b6"

    def test_alternating_characters(self):
        assert compress_string("ababab") == "ababab"

    def test_long_runs(self):
        assert compress_string("aaaaaaaaaa") == "a10"
        assert compress_string("aaaaabbbbbccccc") == "a5b5c5"

    def test_mixed_run_lengths(self):
        assert compress_string("aaabcccccddddde") == "a3b1c5d5e1"

    def test_empty_string(self):
        assert compress_string("") == ""

    def test_single_character(self):
        assert compress_string("a") == "a"

    def test_two_same_characters(self):
        assert compress_string("aa") == "aa"

    def test_two_different_characters(self):
        assert compress_string("ab") == "ab"

    def test_all_unique_characters(self):
        assert compress_string("abcdefgh") == "abcdefgh"

    def test_very_long_run(self):
        long_string = "a" * 100
        assert compress_string(long_string) == "a100"

    def test_uppercase_characters(self):
        assert compress_string("AAABBB") == "A3B3"

    def test_non_string_input_integer(self):
        with pytest.raises(TypeError):
            compress_string(12345)

    def test_non_string_input_list(self):
        with pytest.raises(TypeError):
            compress_string(["a", "a", "a"])

    def test_non_string_input_none(self):
        with pytest.raises(TypeError):
            compress_string(None)

    def test_non_string_input_tuple(self):
        with pytest.raises(TypeError):
            compress_string(("a", "b", "c"))


# ============================================================================
# TEST FUNCTIONS - LONGEST SUBSTRING WITHOUT REPEATING
# ============================================================================


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


class TestLongestSubstringWithoutRepeating:
    def test_basic_case(self):
        assert longest_substring_without_repeating("abcabcbb") == 3
        assert longest_substring_without_repeating("pwwkew") == 3

    def test_all_same_character(self):
        assert longest_substring_without_repeating("bbbbb") == 1
        assert longest_substring_without_repeating("aaaa") == 1

    def test_all_unique_characters(self):
        assert longest_substring_without_repeating("abcdef") == 6
        assert longest_substring_without_repeating("xyz") == 3

    def test_repeated_at_different_positions(self):
        assert longest_substring_without_repeating("abcabcbb") == 3
        assert longest_substring_without_repeating("dvdf") == 3

    def test_with_spaces(self):
        assert longest_substring_without_repeating("a b c a") == 3

    def test_with_special_characters(self):
        assert longest_substring_without_repeating("a!b@c#") == 6
        assert longest_substring_without_repeating("a!b!c") == 3

    def test_empty_string(self):
        assert longest_substring_without_repeating("") == 0

    def test_single_character(self):
        assert longest_substring_without_repeating("a") == 1

    def test_two_same_characters(self):
        assert longest_substring_without_repeating("aa") == 1

    def test_two_different_characters(self):
        assert longest_substring_without_repeating("ab") == 2

    def test_very_long_string_all_unique(self):
        import string

        long_unique = string.ascii_lowercase + string.ascii_uppercase + string.digits
        assert longest_substring_without_repeating(long_unique) == len(long_unique)

    def test_longest_at_beginning(self):
        assert longest_substring_without_repeating("abcabcbb") == 3

    def test_longest_at_end(self):
        assert longest_substring_without_repeating("aaabcdef") == 6

    def test_longest_in_middle(self):
        assert longest_substring_without_repeating("abcdefgaaaaa") == 7

    def test_non_string_input_integer(self):
        with pytest.raises(TypeError):
            longest_substring_without_repeating(123456)

    def test_non_string_input_list(self):
        with pytest.raises(TypeError):
            longest_substring_without_repeating(["a", "b", "c"])

    def test_non_string_input_none(self):
        with pytest.raises(TypeError):
            longest_substring_without_repeating(None)

    def test_non_string_input_float(self):
        with pytest.raises(TypeError):
            longest_substring_without_repeating(3.14)


# ============================================================================
# TEST FUNCTIONS - GROUP ANAGRAMS
# ============================================================================


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


class TestGroupAnagrams:
    def test_basic(self):
        result = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
        result_sorted = [sorted(group) for group in result]
        result_sorted.sort()
        expected = [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
        expected_sorted = [sorted(group) for group in expected]
        expected_sorted.sort()
        assert result_sorted == expected_sorted

    def test_no_anagrams(self):
        result = group_anagrams(["abc", "def", "ghi"])
        assert len(result) == 3
        assert all(len(group) == 1 for group in result)

    def test_all_anagrams(self):
        result = group_anagrams(["abc", "bca", "cab"])
        assert len(result) == 1
        assert len(result[0]) == 3

    def test_different_length_strings(self):
        result = group_anagrams(["a", "ab", "ba", "abc", "bca"])
        result_sorted = [sorted(group) for group in result]
        result_sorted.sort()
        assert len(result) == 3

    def test_case_sensitive(self):
        result = group_anagrams(["Ab", "bA", "ab", "ba"])
        assert len(result) == 2

    def test_with_spaces(self):
        result = group_anagrams(["a b", "b a", "ab", "ba"])
        assert len(result) == 2

    def test_empty_list(self):
        result = group_anagrams([])
        assert result == []

    def test_single_empty_string(self):
        result = group_anagrams([""])
        assert result == [[""]]

    def test_multiple_empty_strings(self):
        result = group_anagrams(["", "", ""])
        assert len(result) == 1
        assert len(result[0]) == 3

    def test_single_string(self):
        result = group_anagrams(["a"])
        assert result == [["a"]]

    def test_single_character_strings(self):
        result = group_anagrams(["a", "b", "c", "a", "b"])
        result_sorted = [sorted(group) for group in result]
        result_sorted.sort()
        expected = [["a", "a"], ["b", "b"], ["c"]]
        expected_sorted = [sorted(group) for group in expected]
        expected_sorted.sort()
        assert result_sorted == expected_sorted

    def test_very_long_strings(self):
        long1 = "a" * 100 + "b" * 100
        long2 = "b" * 100 + "a" * 100
        result = group_anagrams([long1, long2])
        assert len(result) == 1
        assert len(result[0]) == 2

    def test_duplicate_strings(self):
        result = group_anagrams(["abc", "abc", "abc"])
        assert len(result) == 1
        assert len(result[0]) == 3

    def test_numbers_in_strings(self):
        result = group_anagrams(["a1b", "b1a", "ab1", "1ab"])
        assert len(result) == 1
        assert len(result[0]) == 4

    def test_non_list_input_string(self):
        with pytest.raises(TypeError):
            group_anagrams("abc")

    def test_non_list_input_integer(self):
        with pytest.raises(TypeError):
            group_anagrams(123)

    def test_non_list_input_none(self):
        with pytest.raises(TypeError):
            group_anagrams(None)

    def test_list_with_non_string_elements_integers(self):
        with pytest.raises(TypeError):
            group_anagrams(["abc", 123, "def"])

    def test_list_with_non_string_elements_mixed(self):
        with pytest.raises(TypeError):
            group_anagrams(["abc", None, ["def"], "ghi"])

    def test_list_with_all_non_string_elements(self):
        with pytest.raises(TypeError):
            group_anagrams([1, 2, 3, 4])