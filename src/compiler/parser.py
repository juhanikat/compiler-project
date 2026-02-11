from typing import List

from compiler import my_ast, my_types
from compiler.tokenizer import Token, TokenType

left_associative_binary_operators: List[List[str]] = [
    ["="],
    ['or'],
    ['and'],
    ['==', '!='],
    ['<', '<=', '>', '>='],
    ['+', '-'],
    ['*', '/', '%'],
    # all identifiers are in this spot
]


def parse(tokens: list[Token]) -> my_ast.Expression:
    """Returns an Expression parsed from a list of tokens, or None if if the list is empty."""
    if len(tokens) == 0:
        return my_ast.EmptyExpression()

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
        """Same as peek(), but also moves to the next Token on the list (= increases pos by 1).
        If <expected> is given, the next token has to match the given string/list, otherwise this will throw an error."""
        nonlocal pos
        nonlocal last_consumed
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(
                f'{token.source_loc}: expected "{expected}", but got "{token.text}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(
                f'{token.source_loc}: expected one of: {comma_separated}')
        pos += 1
        last_consumed = token
        return token

    def parse_expression(allow_vars: bool = False) -> my_ast.Expression:
        level_index = 0
        left = parse_term(0, allow_vars)
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
                    right,
                    source_loc=left.source_loc
                )
        return left

    def parse_term(level_index: int, allow_vars: bool = False) -> my_ast.Expression:
        left = parse_factor(allow_vars)
        # NOTE: ????? it works
        if left_associative_binary_operators[level_index] != ["="]:
            level_index += 1

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
                    right,
                    source_loc=left.source_loc
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

        elif peek().text == "while":
            return parse_while_do()
        elif allow_vars and peek().text == "var":
            return parse_variable_declaration()

        if peek().type == TokenType.LITERAL:
            return parse_literal()
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
        block_start_token = consume("{")
        expressions = []
        returns_last = False

        while peek().text != "}":
            expression = parse_expression(True)
            expressions.append(expression)

            if peek().text != ";":
                if (last_consumed and last_consumed.text == "}") and peek().text != "}":
                    # NOTE: might cause issues later??
                    continue

                # this expression is returned from the block
                returns_last = True
                break
            consume(";")

        consume("}")
        return my_ast.Block(*expressions, returns_last=returns_last, source_loc=block_start_token.source_loc)

    def parse_top_level() -> my_ast.Expression | my_ast.TopLevel:
        """Will return either a single Expresison (if there is only one top level expression), or a TopLevel otherwise."""
        expressions: list[my_ast.Expression] = []
        expressions.append(parse_expression(True))
        returns_last = True

        while peek().text == ";":
            consume(";")
            returns_last = False
            if peek().type != TokenType.END:
                expressions.append(parse_expression(True))
                if peek().type == TokenType.END:
                    returns_last = True

        if peek().type != TokenType.END:
            raise Exception(
                f'{peek().source_loc}: invalid token "{peek().text}"')

        # if there is only a single expression that IS NOT FOLLOWED BY A SEMICOLON, only return the expression, else return a TopLevel
        if len(expressions) == 1 and returns_last:
            return expressions[0]
        return my_ast.TopLevel(*expressions, returns_last=returns_last, source_loc=expressions[0].source_loc)

    def parse_conditional() -> my_ast.IfThenElse | my_ast.IfThen:
        if_token = consume("if")
        if_expr = parse_expression()
        consume("then")
        then_expr = parse_expression()
        if peek().text == "else":
            consume("else")
            else_expr = parse_expression()
            return my_ast.IfThenElse(if_expr, then_expr, else_expr, source_loc=if_token.source_loc)
        return my_ast.IfThen(if_expr, then_expr, source_loc=if_token.source_loc)

    def parse_function(name: str) -> my_ast.Function:
        consume("(")
        params = []
        # check if the function has any parameters
        if peek().text != ")":
            first_param = parse_expression()
            params.append(first_param)

            while peek().text == ",":
                consume(",")
                param = parse_expression()
                params.append(param)

        consume(")")
        return my_ast.Function(name, *tuple(params))

    def parse_unary() -> my_ast.UnaryOp:
        if peek().text == "not":
            not_token = consume("not")
            target = parse_expression()
            return my_ast.UnaryOp("not", target, source_loc=not_token.source_loc)
        elif peek().text == "-":
            minus_token = consume("-")
            target = parse_expression()
            return my_ast.UnaryOp("-", target, source_loc=minus_token.source_loc)
        raise Exception(
            f'{peek().source_loc}: expected "not" or "-", but got "{peek().text}"')

    def parse_variable_declaration() -> my_ast.Variable:
        def parse_type() -> my_types.BasicType:
            type: my_types.BasicType | None = None
            match peek().text:
                case "Int":
                    type = my_types.Int()
                case "Bool":
                    type = my_types.Bool()
                case "Unit":
                    type = my_types.Unit()
                case _:
                    raise Exception(
                        f"{peek().source_loc}: Expected Int, Bool or Unit as type, but got {peek().text}")
            # consume the type token
            consume(["Int", "Bool", "Unit"])
            return type

        var_token = consume("var")
        var_type: my_types.Type | None = None

        if peek().type == TokenType.IDENTIFIER:
            name = parse_identifier()
        else:
            raise Exception(
                f'{peek().source_loc}: expected the name of the variable, but got "{peek().text}"')

        if peek().text == ":":
            # found typing information
            consume(":")
            if peek().text == "(":
                # found function typing information
                consume("(")
                param_types = []
                first_type = parse_type()
                param_types.append(first_type)
                while peek().text == ",":
                    consume(",")
                    param_type = parse_type()
                    param_types.append(param_type)
                consume(")")
                consume("=>")  # might not work due to =
                return_type = parse_type()
                var_type = my_types.FunType(
                    *param_types, return_type=return_type)
            else:
                var_type = parse_type()

        consume("=")
        value = parse_expression()
        if isinstance(name, my_ast.Function):
            if not isinstance(value, my_ast.Block):
                raise Exception(f"Function value can only be a Block")
            if var_type:
                return my_ast.Variable(name, value, type=var_type, source_loc=var_token.source_loc)
            return my_ast.Variable(name, value, source_loc=var_token.source_loc)
        if var_type:
            return my_ast.Variable(name.name, value, type=var_type, source_loc=var_token.source_loc)
        return my_ast.Variable(name.name, value, source_loc=var_token.source_loc)

    def parse_while_do() -> my_ast.WhileDo:
        while_token = consume("while")
        condition = parse_expression()
        consume("do")
        do_expr = parse_expression()
        return my_ast.WhileDo(condition, do_expr, source_loc=while_token.source_loc)

    def parse_literal() -> my_ast.Literal:
        if peek().type != TokenType.LITERAL:
            raise Exception(
                f'{peek().source_loc}: expected a literal')
        token = consume()
        if token.text == "true":
            return my_ast.Literal(True, source_loc=token.source_loc)
        elif token.text == "false":
            return my_ast.Literal(False, source_loc=token.source_loc)
        return my_ast.Literal(int(token.text), source_loc=token.source_loc)

    def parse_identifier() -> my_ast.Identifier | my_ast.Function:
        if peek().type != TokenType.IDENTIFIER:
            raise Exception(
                f'{peek().source_loc}: expected an identifier, but got "{peek().text}"')
        token = consume()
        # check if this is the start of a function
        if peek().text == "(":
            return parse_function(token.text)
        return my_ast.Identifier(token.text, source_loc=token.source_loc)

    output = parse_top_level()
    return output
