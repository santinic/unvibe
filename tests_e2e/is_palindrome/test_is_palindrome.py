import unvibe
from tests_e2e.is_palindrome.is_palindrome import Utils


class TestIsPalindrome(unvibe.TestCase):
    def test_is_palindrome(self):
        utils = Utils()
        self.assertTrue(utils.is_palindrome('racecar'))
        self.assertFalse(utils.is_palindrome('hello'))
