'''
Author: Joshua Jacobs-Rebhun
Date: February 3, 2026

Unit tests for the device tree tokenizer.
'''

import pytest
import sys

sys.path.insert(0, '..')
from tokenizer import *

@pytest.fixture
def tok():
    '''Yields a tokenizer object and resets it after each test'''
    tokenizer = Tokenizer()
    yield tokenizer
    tokenizer.resetTokenization()



def test_node_definition(tok):
    inputString = "uart0: uart@bfc04000 {}"
    expectedTokens = [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "uart0"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "uart"),
        Token(TokenType.AT_SYMBOL, "@"),
        Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, "bfc04000"),
        Token(TokenType.LEFT_CURLY_BRACE, "{"),
        Token(TokenType.RIGHT_CURLY_BRACE, "}"),
        Token(TokenType.END_OF_FILE, "")
    ]

    i = 0
    tok.initializeTokenization(inputString)
    while ( currentToken := tok.getNextToken() ) != expectedTokens[-1]:
        assert currentToken == expectedTokens[i], f"Expected {str(expectedTokens[i])}, but got {str(currentToken)}"
        i += 1


'''
Tests TODO:
===========
- Test / node definition
- Test node name with '-'
- Test property with '#' and <>
- Test various different node and property names
- Test property inside of node
- Test node definition inside of other node definition
- Test phandle override


'''




