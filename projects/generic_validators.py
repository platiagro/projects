import re
from projects.exceptions import BadRequest


def raise_if_exceeded(max_chars_allowed, value):
    """
    Function that raises if len(value) is greater than maximum
    char amount

    Parameters
    ----------
    max_chars_allowed: int
    value: str
    Returns
    -------
    None
    """
    if len(value) > max_chars_allowed:
        raise BadRequest(
            code="ExceededCharAmount",
            message="Exceeded maximum character quantity allowed",
        )


def raise_if_forbidden_character(forbidden_char_regex, value):
    """
    Function that raises if value contains any forbidden char

    Parameters
    ----------
    forbidden_char_regex: str
        regex pattern with all non-allowed chars
    value: str
    Returns
    -------
    None
    """
    if re.findall(forbidden_char_regex, value):
        raise BadRequest(
            code="NotAllowedChar",
            message="Not allowed char",
        )


# This is necessary to mysql consider special character
# maybe this logic won't work on another database
# maybe we can refactor this!
def escaped_format(value):
    """
    This function will escape string so mysql database be able to read special characters.

    Parameters
    ----------
    value: str
    Returns
    -------
    str
        string escaped
    """
    escaped_string = ""
    # to avoid the trouble of identify every special character we gonna escape all!
    for character in value:
        if character.isalnum():
            escaped_string = escaped_string + character
        else:
            escaped_string = escaped_string + "\\" + character
    return escaped_string
