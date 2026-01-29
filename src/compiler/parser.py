from typing import List

from compiler import my_ast
from compiler.tokenizer import SourceLocation, Token, TokenType

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
    # saves the last consumed Token, used when parsing blocks and semicolons
    last_consumed: Token | None = None

    def peek() -> Token:
        """Returns the next Token on the token list, or the last Token on the list with type=END if there are no more tokens."""
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(
                source_loc=tokens[-1].source_loc,
                type=TokenType.END,
                text="",
            )

    def consume(expected: str | list[str] | None = None) -> Token:
        """Same as peek(), but also moves to the next Token on the list (= increases pos by 1)."""
        nonlocal pos
        nonlocal last_consumed
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.source_loc}: expected "{expected}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(
                f'{token.source_loc}: expected one of: {comma_separated}')
        pos += 1
        last_consumed = token
        return token

    def parse_int_literal() -> my_ast.Literal:
        if peek().type != TokenType.INT_LITERAL:
            raise Exception(
                f'{peek().source_loc}: expected an integer literal')
        token = consume()
        return my_ast.Literal(token.source_loc, int(token.text))

    def parse_identifier() -> my_ast.Identifier | my_ast.Function:
        if peek().type != TokenType.IDENTIFIER:
            raise Exception(
                f'{peek().source_loc}: expected an identifier')
        token = consume()
        # check if this is the start of a function
        if peek().text == "(":
            return parse_function(token.text)
        return my_ast.Identifier(token.source_loc, token.text)

    def parse_expression(allow_vars: bool = False) -> my_ast.Expression:
        """"""
        level_index = 0
        left = parse_term(0, allow_vars)
        for precedence_level in left_associative_binary_operators[level_index:]:
            while peek().text in precedence_level:
                operator_token = consume()
                operator = operator_token.text
                new_level_index = left_associative_binary_operators.index(
                    precedence_level)
                right = parse_term(new_level_index)
                left = my_ast.BinaryOp(left.source_loc,
                                       left,
                                       operator,
                                       right
                                       )
        return left

    def parse_term(level_index: int, allow_vars: bool = False) -> my_ast.Expression:
        """"""
        left = parse_factor(allow_vars)
        for precedence_level in left_associative_binary_operators[level_index:]:
            while peek().text in precedence_level:
                operator_token = consume()
                operator = operator_token.text
                new_level_index = left_associative_binary_operators.index(
                    precedence_level)
                right = parse_term(new_level_index)
                left = my_ast.BinaryOp(left.source_loc,
                                       left,
                                       operator,
                                       right
                                       )
        return left

    def parse_factor(allow_vars: bool = False) -> my_ast.Expression:
        if peek().text == '(':
            return parse_parenthesized()
        elif peek().text == "{":
            return parse_block()
        elif peek().text == "if":
            return parse_conditional()
        elif peek().text in ["not", "-"]:
            return parse_unary()
        elif allow_vars and peek().text == "var":
            return parse_variable_declaration()

        if peek().type == TokenType.INT_LITERAL:
            return parse_int_literal()
        elif peek().type == TokenType.IDENTIFIER:
            return parse_identifier()
        else:
            raise Exception(
                f'{peek().source_loc}: expected an integer literal or an identifier, but got "{peek().text}"')

    def parse_parenthesized() -> my_ast.Expression:
        """Called when parse_factor() sees that an opening parenthesis is the next token."""
        consume('(')
        expr = parse_expression()
        consume(')')
        return expr

    def parse_block() -> my_ast.Block:
        consume("{")
        expressions = []
        result_expr: my_ast.Expression | my_ast.Literal = my_ast.Literal(
            SourceLocation(any=True), None)

        while peek().text != "}":
            expression = parse_expression(True)
            expressions.append(expression)

            if peek().text != ";":
                if (last_consumed and last_consumed.text == "}") and peek().text != "}":
                    # NOTE: might cause issues later??
                    continue

                # this is the last expression inside the block
                result_expr = expressions[-1]
                break
            consume(";")

        consume("}")
        # if the result_expr was not found inside the loop, is is set to Literal(None)
        return my_ast.Block(*expressions, result_expr=result_expr)

    def parse_conditional() -> my_ast.IfThenElse | my_ast.IfThen:
        consume("if")
        if_expr = parse_expression()
        consume("then")
        then_expr = parse_expression()
        if peek().text == "else":
            consume("else")
            else_expr = parse_expression()
            return my_ast.IfThenElse(if_expr.source_loc, if_expr, then_expr, else_expr)
        return my_ast.IfThen(if_expr.source_loc, if_expr, then_expr)

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
            not_token = consume("not")
            target = parse_expression()
            return my_ast.UnaryOp(not_token.source_loc, "not", target)
        elif peek().text == "-":
            minus_token = consume("-")
            target = parse_expression()
            return my_ast.UnaryOp(minus_token.source_loc, "-", target)
        raise Exception(
            f'{peek().source_loc}: expected "not" or "-", but got "{peek().text}"')

    def parse_variable_declaration() -> my_ast.Variable:
        var_token = consume("var")
        if peek().type == TokenType.IDENTIFIER:
            name = parse_identifier()
            if isinstance(name, my_ast.Function):
                raise Exception(
                    "f'{peek().source_loc}: got function when identifier was required")
        else:
            raise Exception(
                f'{peek().source_loc}: expected the name of the variable, but got "{peek().text}"')

        consume("=")
        value = parse_expression()

        return my_ast.Variable(var_token.source_loc, name.name, value)

    output = parse_expression(True)
    if peek().type != TokenType.END:
        raise Exception(
            f'{peek().source_loc}: invalid token "{peek().text}"')
    return output


print(my_ast.Literal(SourceLocation(any=True), 1) ==
      my_ast.Literal(SourceLocation(0, 0), 1))
