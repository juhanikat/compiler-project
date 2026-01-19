from compiler.tokenizer import SourceLocation, Token, TokenType, tokenize


def test_tokenizer_basics() -> None:
    assert tokenize("if  3\nwhile ") == [
        Token("if", TokenType.IDENTIFIER, SourceLocation(equal_to_all=True)),
        Token("3", TokenType.INT_LITERAL, SourceLocation(equal_to_all=True)),
        Token("while", TokenType.IDENTIFIER, SourceLocation(equal_to_all=True))]


def test_empty_code() -> None:
    assert tokenize("") == []
    assert tokenize("    \n    ") == []
    assert tokenize("""

                    """) == []


def test_operators() -> None:
    assert tokenize("2 + 2") == [
        Token("2", TokenType.INT_LITERAL, SourceLocation(equal_to_all=True)),
        Token("+", TokenType.OPERATOR, SourceLocation(equal_to_all=True)),
        Token("2", TokenType.INT_LITERAL, SourceLocation(equal_to_all=True))
    ]
    assert tokenize("2 + -2") == [
        Token("2", TokenType.INT_LITERAL, SourceLocation(equal_to_all=True)),
        Token("+", TokenType.OPERATOR, SourceLocation(equal_to_all=True)),
        Token("-", TokenType.OPERATOR, SourceLocation(equal_to_all=True)),
        Token("2", TokenType.INT_LITERAL, SourceLocation(equal_to_all=True))
    ]

    assert tokenize(">===<=<") == [
        Token(">=", TokenType.OPERATOR, SourceLocation(equal_to_all=True)),
        Token("==", TokenType.OPERATOR, SourceLocation(equal_to_all=True)),
        Token("<=", TokenType.OPERATOR, SourceLocation(equal_to_all=True)),
        Token("<", TokenType.OPERATOR, SourceLocation(equal_to_all=True))
    ]


def test_punctuation() -> None:
    assert tokenize("(hello world)") == [
        Token("(", TokenType.PUNCTUATION, SourceLocation(equal_to_all=True)),
        Token("hello", TokenType.IDENTIFIER,
              SourceLocation(equal_to_all=True)),
        Token("world", TokenType.IDENTIFIER,
              SourceLocation(equal_to_all=True)),
        Token(")", TokenType.PUNCTUATION, SourceLocation(equal_to_all=True))
    ]
    assert tokenize("\n{25};") == [
        Token("{", TokenType.PUNCTUATION, SourceLocation(equal_to_all=True)),
        Token("25", TokenType.INT_LITERAL, SourceLocation(equal_to_all=True)),
        Token("}", TokenType.PUNCTUATION, SourceLocation(equal_to_all=True)),
        Token(";", TokenType.PUNCTUATION, SourceLocation(equal_to_all=True)),
    ]


def test_comments() -> None:
    assert tokenize("# hello world") == []
    assert tokenize("#") == []
    assert tokenize("""# hello
                    while
                    world!""") == [
        Token("while", TokenType.IDENTIFIER,
              SourceLocation(equal_to_all=True)),
        Token("world", TokenType.IDENTIFIER,
              SourceLocation(equal_to_all=True)),
    ]
