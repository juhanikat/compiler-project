from typing import List

from compiler import my_ast
from compiler.tokenizer import Token, TokenType

left_associative_binary_operators: List[List[str]] = [
    ['='],
    ['or'],
    ['and'],
    ['==', '!='],
    ['<', '<=', '>', '>='],
    ['+', '-'],
    ['*', '/', '%'],
    # all identifiers are in this spot
]


def parse(tokens: list[Token]) -> my_ast.Expression | None:
    """Returns an Expression parsed from a list of tokens, or None if if the list is empty."""
    if len(tokens) == 0:
        return None

    pos = 0

    def peek() -> Token:
        """Returns the next Token on the token list, or the last Token on the list with type=END if there are no more tokens."""
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(
                source_location=tokens[-1].source_location,
                type=TokenType.END,
                text="",
            )

    def consume(expected: str | list[str] | None = None) -> Token:
        """Same as peek(), but also moves to the next Token on the list (= increases pos by 1)."""
        nonlocal pos
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.source_location}: expected "{expected}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(
                f'{token.source_location}: expected one of: {comma_separated}')
        pos += 1
        return token

    def parse_int_literal() -> my_ast.Literal:
        if peek().type != TokenType.INT_LITERAL:
            raise Exception(
                f'{peek().source_location}: expected an integer literal')
        token = consume()
        return my_ast.Literal(int(token.text))

    def parse_identifier() -> my_ast.Identifier | my_ast.Function:
        if peek().type != TokenType.IDENTIFIER:
            raise Exception(
                f'{peek().source_location}: expected an identifier')
        token = consume()
        # check if this is the start of a function
        if peek().text == "(":
            return parse_function(token.text)
        return my_ast.Identifier(token.text)

    def parse_expression() -> my_ast.Expression:
        """"""
        level_index = 0
        left = parse_term(0)
        for precedence_level in left_associative_binary_operators[level_index:]:
            while peek().text in precedence_level:
                operator_token = consume()
                operator = operator_token.text
                new_level_index = left_associative_binary_operators.index(
                    precedence_level)
                right = parse_term(new_level_index)
                left = my_ast.BinaryOp(
                    left,
                    operator,
                    right
                )
        return left

    def parse_term(level_index: int) -> my_ast.Expression:
        """"""
        left = parse_factor()
        for precedence_level in left_associative_binary_operators[level_index:]:
            while peek().text in precedence_level:
                operator_token = consume()
                operator = operator_token.text
                new_level_index = left_associative_binary_operators.index(
                    precedence_level)
                right = parse_term(new_level_index)
                left = my_ast.BinaryOp(
                    left,
                    operator,
                    right
                )
        return left

    def parse_factor() -> my_ast.Expression:
        if peek().text == '(':
            return parse_parenthesized()
        elif peek().text == "if":
            return parse_conditional()
        elif peek().text in ["not", "-"]:
            return parse_unary()

        if peek().type == TokenType.INT_LITERAL:
            return parse_int_literal()
        elif peek().type == TokenType.IDENTIFIER:
            return parse_identifier()
        else:
            raise Exception(
                f'{peek().source_location}: expected an integer literal or an identifier, but got "{peek().text}"')

    def parse_parenthesized() -> my_ast.Expression:
        """Called when parse_factor() sees that an opening parenthesis is the next token."""
        consume('(')
        expr = parse_expression()
        consume(')')
        return expr

    def parse_conditional() -> my_ast.IfThenElse | my_ast.IfThen:
        consume("if")
        if_expr = parse_expression()
        consume("then")
        then_expr = parse_expression()
        if peek().text == "else":
            consume("else")
            else_expr = parse_expression()
            return my_ast.IfThenElse(if_expr, then_expr, else_expr)
        return my_ast.IfThen(if_expr, then_expr)

    def parse_function(name: str) -> my_ast.Function:
        consume("(")
        params = []
        params.append(parse_expression())
        while peek().text == ",":
            consume(",")
            params.append(parse_expression())
        consume(")")
        return my_ast.Function(name, *params)

    def parse_unary() -> my_ast.UnaryOp:
        if peek().text == "not":
            consume("not")
            target = parse_expression()
            return my_ast.UnaryOp("not", target)
        elif peek().text == "-":
            consume("-")
            target = parse_expression()
            return my_ast.UnaryOp("-", target)
        raise Exception(
            f'{peek().source_location}: expected "not" or "-", but got "{peek().text}"')

    output = parse_expression()
    if peek().type != TokenType.END:
        raise Exception(
            f'{peek().source_location}: invalid token "{peek().text}"')
    return output
