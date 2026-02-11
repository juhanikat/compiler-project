import re
from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    LITERAL = "literal"
    IDENTIFIER = "identifier"
    OPERATOR = "operator"
    PUNCTUATION = "punctuation"
    OTHER = "other"
    END = "end"


@dataclass
class SourceLocation:
    line: int = -1
    column: int = -1
    # if this is True, location is excluded when checking for equality of tokens / ast nodes
    any: bool = False

    def __repr__(self) -> str:
        if self.any:
            return f"(any=True)"
        return f"({self.line}, {self.column})"


@dataclass
class Token:
    """Class for a single Token.
    Contains the text of the token, the type of the token,
    and the line and column where the token appeared."""
    text: str
    type: TokenType
    source_loc: SourceLocation

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return NotImplemented
        return (self.text == other.text and
                self.type == other.type and
                (self.source_loc == other.source_loc or other.source_loc.any == True))

    def __str__(self) -> str:
        return f"Token text={self.text} type={self.type}"


def tokenize(source_code: str) -> list[Token]:
    literal_patterns = [
        re.compile(r"[0-9]+"),
        re.compile(r"false|true")
    ]

    identifier_patterns = [
        re.compile(r"[_a-zA-Z][_a-zA-Z0-9]*")  # also includes if, while etc.
    ]

    # these are ignored atm
    other_patterns = [
        re.compile(r"\s+"),
        re.compile(r"\n"),
        re.compile(r"#.*")  # Comments
    ]

    # (, ), {, }, ,, ;
    punctuation_patterns = [
        re.compile(r"\(|\)|\{|\}|\,|\;|:|=>")
    ]
    # +, -, *, /, %, =, ==, !=, <, <=, >, >=
    operator_patterns = [
        re.compile(r"==|!=|<=|>=|\<|\>|\+|\-|\*|\/|\%|\=")
    ]

    def look_for_matches(source_code: str) -> Token | None:
        for literal_pattern in literal_patterns:
            match = re.match(literal_pattern, source_code)
            if match:
                return Token(match.group(
                ), TokenType.LITERAL, SourceLocation(line, column))
        for identifier_pattern in identifier_patterns:
            match = re.match(identifier_pattern, source_code)
            if match:
                return Token(match.group(
                ), TokenType.IDENTIFIER, SourceLocation(line, column))
        # this is before the operator loop because of =>
        for punctuation_pattern in punctuation_patterns:
            match = re.match(punctuation_pattern, source_code)
            if match:
                return Token(match.group(
                ), TokenType.PUNCTUATION, SourceLocation(line, column))
        for operator_pattern in operator_patterns:
            match = re.match(operator_pattern, source_code)
            if match:
                return Token(match.group(
                ), TokenType.OPERATOR, SourceLocation(line, column))
        # this is before the punctuation loop because of \n
        for other_pattern in other_patterns:
            match = re.match(other_pattern, source_code)
            if match:
                return Token(match.group(
                ), TokenType.OTHER, SourceLocation(line, column))

        return None

    line = 1
    column = 1
    output = []
    match_token = look_for_matches(source_code)

    while match_token:
        if re.match(r"\n", match_token.text):
            line += 1
            column = 1
        else:
            column += len(match_token.text)

        if not match_token.type == TokenType.OTHER:
            # Do not add OTHER type tokens to the output
            output.append(match_token)

        if len(match_token.text) < len(source_code):
            source_code = source_code[len(match_token.text):]
            match_token = look_for_matches(source_code)
        else:
            break

    return output
