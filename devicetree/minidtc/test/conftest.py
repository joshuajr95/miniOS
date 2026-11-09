


import pytest
import sys

from ..compiler import Tokenizer


@pytest.fixture
def tok():
    """Yields a tokenizer object and resets it after each test"""
    tokenizer = Tokenizer()
    yield tokenizer
    tokenizer.resetTokenization()



