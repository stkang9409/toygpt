from my_ai import catch_code_in_response
import pytest


def test_plain_text():
    response = catch_code_in_response("hello")
    assert response == "hello"


def test_code_block():
    response = catch_code_in_response("```hello```")
    assert response == "hello"
