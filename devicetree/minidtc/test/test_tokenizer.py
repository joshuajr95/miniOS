"""
Author: Joshua Jacobs-Rebhun
Date: February 3, 2026

Unit tests for the device tree tokenizer.
"""

import pytest
from ..compiler import (
    Token,
    TokenType
)



testData = [
    ("uart0: uart@bfc04000 {}", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "uart0"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "uart"),
        Token(TokenType.AT_SYMBOL, "@"),
        Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, "bfc04000"),
        Token(TokenType.LEFT_CURLY_BRACE, "{"),
        Token(TokenType.RIGHT_CURLY_BRACE, "}"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("uart0: uart@bfc04000 { reg = <0xbfc04000 0x400>; };", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "uart0"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "uart"),
        Token(TokenType.AT_SYMBOL, "@"),
        Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, "bfc04000"),
        Token(TokenType.LEFT_CURLY_BRACE, "{"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "reg"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0xbfc04000"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x400"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.RIGHT_CURLY_BRACE, "}"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("/ {model = \"microchip,pic32mx795f512l\";}", [
        Token(TokenType.FORWARD_SLASH, "/"),
        Token(TokenType.LEFT_CURLY_BRACE, "{"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "model"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.STRING, "microchip,pic32mx795f512l"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.RIGHT_CURLY_BRACE, "}"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("dma_controller: dma-controller@ffe06000 {reg = <0xffe06000 0x1000>;};", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "dma_controller"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.NODE_OR_PROPERTY_NAME, "dma-controller"),
        Token(TokenType.AT_SYMBOL, "@"),
        Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, "ffe06000"),
        Token(TokenType.LEFT_CURLY_BRACE, "{"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "reg"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0xffe06000"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x1000"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.RIGHT_CURLY_BRACE, "}"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("cpu@0 {};", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "cpu"),
        Token(TokenType.AT_SYMBOL, "@"),
        Token(TokenType.DECIMAL_NUMBER, "0"),
        Token(TokenType.LEFT_CURLY_BRACE, "{"),
        Token(TokenType.RIGHT_CURLY_BRACE, "}"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("mouse {};", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "mouse"),
        Token(TokenType.LEFT_CURLY_BRACE, "{"),
        Token(TokenType.RIGHT_CURLY_BRACE, "}"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("deadbeef = <5>;", [
        Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, "deadbeef"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.DECIMAL_NUMBER, "5"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("compatible = \"nxp,s3842a\"", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "compatible"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.STRING, "nxp,s3842a"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("compatible = \"toradex,apalis_imx6q-ixora-v1.1\",\"toradex,apalis_imx6q-ixora\", \"toradex,apalis_imx6q\",\"fsl,imx6q\";", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "compatible"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.STRING, "toradex,apalis_imx6q-ixora-v1.1"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.STRING, "toradex,apalis_imx6q-ixora"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.STRING, "toradex,apalis_imx6q"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.STRING, "fsl,imx6q"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("reg = <0xbfc04000 0x400>;", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "reg"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0xbfc04000"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x400"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("hw-flow-control;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "hw-flow-control"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("local-mac-address = [00 00 12 34 56 78];", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "local-mac-address"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_SQUARE_BRACKET, "["),
        Token(TokenType.DECIMAL_NUMBER, "00"),
        Token(TokenType.DECIMAL_NUMBER, "00"),
        Token(TokenType.DECIMAL_NUMBER, "12"),
        Token(TokenType.DECIMAL_NUMBER, "34"),
        Token(TokenType.DECIMAL_NUMBER, "56"),
        Token(TokenType.DECIMAL_NUMBER, "78"),
        Token(TokenType.RIGHT_SQUARE_BRACKET, "]"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("local-mac-address = [00 00 a2 4b f6 78];", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "local-mac-address"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_SQUARE_BRACKET, "["),
        Token(TokenType.DECIMAL_NUMBER, "00"),
        Token(TokenType.DECIMAL_NUMBER, "00"),
        Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, "a2"),
        Token(TokenType.HEXADECIMAL_NUMBER, "4b"),
        Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, "f6"),
        Token(TokenType.DECIMAL_NUMBER, "78"),
        Token(TokenType.RIGHT_SQUARE_BRACKET, "]"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("weird-property = \"some-string\", <0x1 0x300 17>;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "weird-property"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.STRING, "some-string"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x1"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x300"),
        Token(TokenType.DECIMAL_NUMBER, "17"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("gpios = <((0x1 << 2) | 0x2) 44>;", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "gpios"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x1"),
        Token(TokenType.LEFT_SHIFT, "<<"),
        Token(TokenType.DECIMAL_NUMBER, "2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.BITWISE_OR, "|"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.DECIMAL_NUMBER, "44"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("reg = <(0xbfc0+0x4000) (0x600-0x200)>;", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "reg"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.HEXADECIMAL_NUMBER, "0xbfc0"),
        Token(TokenType.PLUS, "+"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x4000"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x600"),
        Token(TokenType.MINUS, "-"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x200"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("bitmask = <((~(0x3 << 2)) | (0x8 >> 2))>;", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "bitmask"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.BITWISE_NOT, "~"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x3"),
        Token(TokenType.LEFT_SHIFT, "<<"),
        Token(TokenType.DECIMAL_NUMBER, "2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.BITWISE_OR, "|"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x8"),
        Token(TokenType.RIGHT_SHIFT, ">>"),
        Token(TokenType.DECIMAL_NUMBER, "2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("result = <(0x2*0x4)>;", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "result"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x2"),
        Token(TokenType.MULTIPLY, "*"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x4"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("when-use-div = <(8/2)>;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "when-use-div"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.DECIMAL_NUMBER, "8"),
        Token(TokenType.FORWARD_SLASH, "/"),
        Token(TokenType.DECIMAL_NUMBER, "2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("mod-could-be-useful = <(0x44%3)>;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "mod-could-be-useful"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x44"),
        Token(TokenType.MODULUS, "%"),
        Token(TokenType.DECIMAL_NUMBER, "3"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("andmask = <(0xdeadbeef & 0x7)>;", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "andmask"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.HEXADECIMAL_NUMBER, "0xdeadbeef"),
        Token(TokenType.AMPERSAND, "&"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x7"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("ternary = <(CONFIG_ONE ? 0x2 : 0x4)>;", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "ternary"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "CONFIG_ONE"),
        Token(TokenType.QUESTION_MARK, "?"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x2"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x4"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("ternary-2 = <((VAR1<VAR2)?VAR1:VAR2)>;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "ternary-2"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.QUESTION_MARK, "?"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("ternary-2 = < ( ( VAR1 < VAR2 ) ? VAR1 : VAR2 ) > ;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "ternary-2"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.QUESTION_MARK, "?"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("ternary-3 = <((VAR1<=VAR2)?VAR1:VAR2)>;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "ternary-3"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.LESS_EQ, "<="),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.QUESTION_MARK, "?"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("ternary-4 = <((VAR1>VAR2)?VAR1:VAR2)>;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "ternary-4"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.QUESTION_MARK, "?"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("ternary-5 = <((VAR1>=VAR2)?VAR1:VAR2)>;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "ternary-5"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.GREATER_EQ, ">="),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.QUESTION_MARK, "?"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("ternary-5 = <((VAR1==VAR2)?0xffe0:0x1000)>;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "ternary-5"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.DOUBLE_EQUALS, "=="),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.QUESTION_MARK, "?"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0xffe0"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x1000"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("ternary-6 = <((VAR1!=VAR2)?0xffe0:0x1000)>;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "ternary-6"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.NOT_EQUALS, "!="),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.QUESTION_MARK, "?"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0xffe0"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x1000"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("ternary-7 = <((!VAR1)?0xffe0:0x1000)>;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "ternary-7"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.EXCLAMATION_POINT, "!"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.QUESTION_MARK, "?"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0xffe0"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x1000"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("ternary-8 = <((VAR1&&VAR2)?0xffe0:0x1000)>;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "ternary-8"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.LOGICAL_AND, "&&"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.QUESTION_MARK, "?"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0xffe0"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x1000"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("ternary-9 = <((VAR1||VAR2)?0xffe0:0x1000)>;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "ternary-9"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LEFT_PARENTHESIS, "("),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR1"),
        Token(TokenType.LOGICAL_OR, "||"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "VAR2"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.QUESTION_MARK, "?"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0xffe0"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.HEXADECIMAL_NUMBER, "0x1000"),
        Token(TokenType.RIGHT_PARENTHESIS, ")"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("interrupt-parent = <&intc>;", [
        Token(TokenType.NODE_OR_PROPERTY_NAME, "interrupt-parent"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.AMPERSAND, "&"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "intc"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("&uart2 {status = \"okay\";};", [
        Token(TokenType.AMPERSAND, "&"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "uart2"),
        Token(TokenType.LEFT_CURLY_BRACE, "{"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "status"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.STRING, "okay"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.RIGHT_CURLY_BRACE, "}"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("#interrupt-cells = <2>;", [
        Token(TokenType.HASHTAG, "#"),
        Token(TokenType.NODE_OR_PROPERTY_NAME, "interrupt-cells"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.DECIMAL_NUMBER, "2"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ]),
    ("soc { #address-cells = <1>; uart0: uart@bfc06000 { compatible = \"lol,uart\";};};", [
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "soc"),
        Token(TokenType.LEFT_CURLY_BRACE, "{"),
        Token(TokenType.HASHTAG, "#"),
        Token(TokenType.NODE_OR_PROPERTY_NAME, "address-cells"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.LEFT_ANGLE_BRACKET, "<"),
        Token(TokenType.DECIMAL_NUMBER, "1"),
        Token(TokenType.RIGHT_ANGLE_BRACKET, ">"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "uart0"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "uart"),
        Token(TokenType.AT_SYMBOL, "@"),
        Token(TokenType.HEX_NUMBER_NO_PREFIX_OR_LABEL_OR_NODE_OR_PROPERTY, "bfc06000"),
        Token(TokenType.LEFT_CURLY_BRACE, "{"),
        Token(TokenType.LABEL_OR_NODE_OR_PROPERTY_NAME, "compatible"),
        Token(TokenType.EQUALS, "="),
        Token(TokenType.STRING, "lol,uart"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.RIGHT_CURLY_BRACE, "}"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.RIGHT_CURLY_BRACE, "}"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.END_OF_FILE, "")
    ])
]


@pytest.mark.parametrize("testString, expectedTokens", testData)
def testTokenization(tok, testString, expectedTokens):

    i = 0
    tok.setStringToTokenize(testString)

    assert tok.currentStringIndex == 0

    tokens = []
    while ( currentToken := tok.getNextToken() ) != expectedTokens[-1]:
        tokens.append(currentToken)
        assert currentToken == expectedTokens[i], f"Expected {str(expectedTokens[i])}, but got {str(currentToken)}.\nInput: {testString}\nTokens: {[str(token) for token in tokens]}\n"
        i += 1



# TODO:
#   - Init tok at beginning of each iteration of test
#   - Can fixtures be run at the beginning and end of each test??


"""
Tests TODO:
===========
- Test / node definition DONE
- Test node name with '-' DONE
- Test node without unit address DONE
- Test node without label DONE
- Test property beginning with '#' DONE
- Test property of type string DONE
- Test property of type string array DONE
- Test property of type int array DONE
- Test property of type boolean (no value) DONE
- Test property of type byte array DONE
- Test property with mixed type (comma separated list of types) DONE
- Test properties with various different operators as types DONE
    - Arithmetic (+, -, *, /, %)
    - Bitwise (&, |, ^, ~, <<, >>)
    - Logical (&&, ||, !)
    - Relational (<, >, <=, >=, ==, !=)
    - Ternary
- Test various different node and property names
- Test node definition inside of other node definition DONE
- Test phandle override DONE
- Test phandle reference (interrupt-parent) DONE

- Test state before and after getNextToken
- Test state after each invocation of the state callback function
- Test line and column numbers


"""




