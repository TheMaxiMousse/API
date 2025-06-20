import pytest

from app.utility.string_utils import sanitize_username


@pytest.mark.parametrize(
    "input_username,expected",
    [
        ("validUser_123", "validUser_123"),
        ("user.name", "user_name"),
        ("user-name", "user_name"),
        ("user name", "user_name"),
        ("user@domain.com", "user_domain_com"),
        ("user!$%^&*()", "user________"),
        ("", ""),
        ("___", "___"),
        ("user__name", "user__name"),
        ("user\nname", "user_name"),
        ("user\tname", "user_name"),
        ("user/\\name", "user__name"),
    ],
)
def test_sanitize_username(input_username, expected):
    assert sanitize_username(input_username) == expected
