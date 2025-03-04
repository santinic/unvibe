def lisp(exp):
    # Tokenize the input string
    tokens = []
    current_token = []
    i = 0
    n = len(exp)

    while i < n:
        c = exp[i]
        if c == '(' or c == ')':
            tokens.append(c)
            i += 1
        elif c == "'":
            # String token, collect until next '
            j = i + 1
            while j < n and exp[j] != "'":
                j += 1
            tokens.append(exp[i:j])
            i = j + 1
        else:
            # Symbol or number
            if c in '()':
                continue
            current_token.append(c)
            i += 1
    # Handle the last token which might be incomplete
    if current_token:
        tokens.append(''.join(current_token))

    # Parse tokens into AST
    def parse(tokens):
        stack = []
        for token in tokens:
            if token == '(':
                stack.append([])
            elif token == ')':
                if not stack:
                    raise SyntaxError("Mismatched parentheses")
                stack[-1] = None  # Indicate end of list
            else:
                if isinstance(stack[-1], list) and stack[-1] is not None:
                    stack[-1].append(token)
        return stack[0]

    ast = parse(tokens)

    # Evaluate AST with variables and built-ins
    def evaluate(node, variables):
        if node is None:
            raise SyntaxError("Mismatched parentheses")
        if isinstance(node, list):
            evaluated = []
            for i, child in enumerate(node):
                evaluated_child = evaluate(child, variables)
                evaluated.append(evaluated_child)
            return evaluated
        elif isinstance(node, str):
            return node
        else:
            # Symbol or built-in function
            symbol = ''.join(node)
            if symbol in variables:
                func = variables[symbol]
                args = []
                for arg_node in node:
                    args.append(evaluate(arg_node, variables))
                return func(*args)
            else:
                raise NameError(f"Undefined variable: {symbol}")

    # Define built-in functions
    def car(lst):
        if isinstance(lst, list) and lst is not None:
            return lst[0]
        else:
            raise TypeError("Car requires a list")

    variables = {
        'car': car,
        'lisp': lambda x: x  # This function just returns its argument
    }

    result = evaluate(ast, variables)
    return result
