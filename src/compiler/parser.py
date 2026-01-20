from compiler import my_ast
from compiler.tokenizer import SourceLocation, Token, TokenType


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

    def parse_identifier() -> my_ast.Identifier:
        if peek().type != TokenType.IDENTIFIER:
            raise Exception(
                f'{peek().source_location}: expected an identifier')
        token = consume()
        return my_ast.Identifier(token.text)

    def parse_expression() -> my_ast.Expression:
        """Terms (left and right) can be either int literals or * / operators."""
        left = parse_term()
        while peek().text in ['+', '-']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_term()
            left = my_ast.BinaryOp(
                left,
                operator,
                right
            )
        return left

    def parse_term() -> my_ast.Expression:
        """Factors (left and right) can be either int literals or identifiers."""
        left = parse_factor()
        while peek().text in ['*', '/']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_factor()
            left = my_ast.BinaryOp(
                left,
                operator,
                right
            )
        return left

    def parse_factor() -> my_ast.Expression:
        if peek().text == '(':
            return parse_parenthesized()
        if peek().text == "if":
            return parse_conditional()

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

    output = parse_expression()
    if peek().type != TokenType.END:
        raise Exception(
            f'{peek().source_location}: invalid token')
    return output
