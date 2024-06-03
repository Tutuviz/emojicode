import re
import sys
import os
import argparse

token_specification = [
    ('PROGRAM_START', r'▶️'),
    ('PROGRAM_END', r'⏹️'),
    ('VARIABLE', r'(🧵|🔢|✳️)'),
    ('NUMBER', r'\d+'),
    ('IDENTIFIER', r'\w+'),
    ('ASSIGN', r'='),
    ('INPUT', r'📥'),
    ('OUTPUT', r'📤'),
    ('STRING', r'🌪️.*?🌪️'),
    ('BOOLEAN', r'(✅|❎)'),
    ('CONDITIONAL_IF', r'🍷🗿'),
    ('CONDITIONAL_ELSE', r'☝️🤓'),    
    ('BLOCK_START', r'🔓'),
    ('BLOCK_END', r'🔒'),
    ('OPERATION_AND', r'😍😍'),
    ('OPERATION_OR', r'😘🤨'),
    ('OPERATION', r'♊|♓|🐜|🐘|🐜🐞|🐘🦣'),
    ('EXPRESSION', r'🤰|🔫'),
    ('TERM', r'🙅‍♂️|🇦🇴'),
    ('WHILE_LOOP', r'🐳'),
    ('FOR_LOOP', r'🔂'),
    ('LOOP_TO', r'⛳'),
    ('SKIP', r'[ \t]+'),
    ('NEWLINE', r'\n'),
    ('MISMATCH', r'.'),
]

# TODO: calculate this automatically
token_type_to_emoji = {
    'PROGRAM_START': '▶️',
    'PROGRAM_END': '⏹️',
    'VARIABLE': '🧵|🔢|✳️',
    'IDENTIFIER': 'identifier',
    'ASSIGN': '=',
    'INPUT': '📥',
    'OUTPUT': '📤',
    'STRING': '🌪️...🌪️',
    'CONDITIONAL_IF': '🍷🗿',
    'BLOCK_START': '🔓',
    'BLOCK_END': '🔒',
    'NUMBER': 'number',
    'OPERATION': '😍😍|😘🤨|♊|♓|🐜|🐘|🐜🐞|🐘🦣',
    'EXPRESSION': '🤰|🔫',
    'TERM': '🙅‍♂️|🇦🇴',
    'WHILE_LOOP': '🐳',
    'FOR_LOOP': '🔂',
    'LOOP_TO': '⛳',
    'NEWLINE': 'newline',
    'SKIP': 'space or tab',
    'MISMATCH': 'mismatch',
}

def debug_print(text):
    if args.debug:
        print(text)

def tokenize(code):
    tokens = []
    for mo in re.finditer('|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification), code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':
            continue
        elif kind == 'NEWLINE':
            tokens.append(('NEWLINE', '\n'))
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character: >{value}<')
        else:
            tokens.append((kind, value))
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        self.consume('PROGRAM_START')
        body = self.parse_body()
        self.consume('PROGRAM_END')
        return body

    def parse_body(self):
        statements = []
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] not in {'PROGRAM_END', 'BLOCK_END'}:
            if self.tokens[self.pos][0] == 'NEWLINE':
                self.pos += 1
            else:
                statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        token = self.tokens[self.pos]
        if token[0] == 'VARIABLE':
            return self.parse_variable_declaration()
        elif token[0] == 'OUTPUT':
            return self.parse_output()
        elif token[0] == 'INPUT':
            return self.parse_input()
        elif token[0] == 'CONDITIONAL_IF':
            return self.parse_conditional()
        elif token[0] == 'WHILE_LOOP':
            return self.parse_while_loop()
        elif token[0] == 'FOR_LOOP':
            return self.parse_for_loop()
        else:
            raise RuntimeError(f'Unexpected token: {token}')

    def parse_variable_declaration(self):
        self.consume('VARIABLE')
        var_type = self.tokens[self.pos - 1][1]
        identifier = self.consume('IDENTIFIER')
        if not identifier[0].isalpha():
            raise RuntimeError(f'Variable name must start with an alphabetical character, but got: {identifier}')
        self.consume('ASSIGN')
        value = self.parse_expression()
        return ('variable_declaration', var_type, identifier, value)

    def parse_output(self):
        self.consume('OUTPUT')
        value = self.parse_expression()
        return ('output', value)

    def parse_input(self):
        self.consume('INPUT')
        value = self.parse_expression()
        return ('input', value)

    def parse_conditional(self):
        self.consume('CONDITIONAL_IF')
        condition = self.parse_expression()
        self.consume('BLOCK_START')
        body = self.parse_body()
        self.consume('BLOCK_END')

        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'CONDITIONAL_ELSE':
            self.consume('CONDITIONAL_ELSE')
            self.consume('BLOCK_START')
            else_body = self.parse_body()
            self.consume('BLOCK_END')
            return ('conditional', condition, body, else_body)

        return ('conditional', condition, body)

    def parse_while_loop(self):
        self.consume('WHILE_LOOP')
        condition = self.parse_expression()
        self.consume('BLOCK_START')
        body = self.parse_body()
        self.consume('BLOCK_END')
        return ('while_loop', condition, body)
    
    def parse_for_loop(self):
        self.consume('FOR_LOOP')
        variable = self.consume('IDENTIFIER')
        self.consume('LOOP_TO')
        end = self.consume('NUMBER')
        self.consume('BLOCK_START')
        body = self.parse_body()
        self.consume('BLOCK_END')
        return ('for_loop', variable, end, body)

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.match('OPERATION_OR'):
            operator = self.consume('OPERATION_OR')
            right = self.parse_and()
            left = ('operation', left, operator, right)
        return left

    def parse_and(self):
        left = self.parse_equality()
        while self.match('OPERATION_AND'):
            operator = self.consume('OPERATION_AND')
            right = self.parse_equality()
            left = ('operation', left, operator, right)
        return left

    def parse_equality(self):
        left = self.parse_comparison()
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'OPERATION' and self.tokens[self.pos][1] in {'♊', '♓'}:
            op = self.consume('OPERATION')
            right = self.parse_comparison()
            left = ('operation', left, op, right)
        return left

    def parse_comparison(self):
        left = self.parse_term()
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'OPERATION' and self.tokens[self.pos][1] in {'🐜', '🐘', '🐜🐞', '🐘🦣'}:
            op = self.consume('OPERATION')
            right = self.parse_term()
            left = ('operation', left, op, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'OPERATION' and self.tokens[self.pos][1] in {'🤰', '🔫'}:
            op = self.consume('OPERATION')
            right = self.parse_factor()
            left = ('operation', left, op, right)
        return left

    def parse_factor(self):
        left = self.parse_primary()
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'OPERATION' and self.tokens[self.pos][1] in {'🙅‍♂️', '🇦🇴'}:
            op = self.consume('OPERATION')
            right = self.parse_primary()
            left = ('operation', left, op, right)
        return left

    def parse_primary(self):
        token = self.tokens[self.pos]
        if token[0] == 'STRING':
            return self.consume('STRING')
        elif token[0] == 'IDENTIFIER':
            return self.consume('IDENTIFIER')
        elif token[0] == 'NUMBER':
            return self.consume('NUMBER')
        elif token[0] == 'BOOLEAN':
            return self.consume('BOOLEAN')
        elif token[0] == 'INPUT':
            self.consume('INPUT')
            if self.tokens[self.pos][0] == 'STRING':
                prompt = self.consume('STRING')
                return ('input', prompt)
            else:
                return ('input', None)
        else:
            raise RuntimeError(f'Unexpected token in expression: {token}')

    def consume(self, expected_type):
        token = self.tokens[self.pos]
        if token[0] == expected_type:
            self.pos += 1
            return token[1]
        else:
            # TODO: Put error line and column number
            # raise RuntimeError(f'Expected {expected_type} but got {token[0]}')
            expected_value = token_type_to_emoji.get(expected_type, expected_type)
            actual_value = token_type_to_emoji.get(token[0], token[0])
            raise RuntimeError(f'Expected {expected_value} but got {actual_value}')
        
    def match(self, expected_type):
        return self.pos < len(self.tokens) and self.tokens[self.pos][0] == expected_type

class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = {}

    def analyze(self):
        for statement in self.ast:
            # print(statement)
            self.analyze_statement(statement)
    
    def analyze_body(self, body):
        for statement in body:
            self.analyze_statement(statement)

    def analyze_statement(self, statement):
        if statement[0] == 'variable_declaration':
            self.analyze_variable_declaration(statement)
        elif statement[0] == 'output':
            self.analyze_output(statement)
        elif statement[0] == 'input':
            self.analyze_input(statement)
        elif statement[0] == 'conditional':
            self.analyze_conditional(statement)
        elif statement[0] == 'while_loop':
            self.analyze_while_loop(statement)
        elif statement[0] == 'for_loop':
            self.analyze_for_loop(statement)
        else:
            raise RuntimeError(f'Unknown statement type: {statement[0]}')

    def analyze_variable_declaration(self, statement):
        _, var_type, identifier, value = statement
        if identifier in self.symbol_table:
            raise RuntimeError(f'Variable {identifier} already declared')
        
        value_type = self.analyze_expression(value)
        if var_type == '🧵' and value_type != 'string':
            raise RuntimeError(f'Type error: Expected string for variable {identifier}, but got {value_type}')
        elif var_type == '🔢' and value_type != 'number':
            raise RuntimeError(f'Type error: Expected number for variable {identifier}, but got {value_type}')
        elif var_type == '✳️' and value_type != 'boolean':
            raise RuntimeError(f'Type error: Expected boolean for variable {identifier}, but got {value_type}')

        self.symbol_table[identifier] = value_type

    def analyze_input(self, statement):
        _, value = statement
        self.analyze_expression(value)
    
    def analyze_output(self, statement):
        _, value = statement
        self.analyze_expression(value)

    def analyze_conditional(self, statement):
        if len(statement) == 4:
            _, condition, if_body, else_body = statement
        else:
            _, condition, if_body = statement
            else_body = None
        condition_type = self.analyze_expression(condition)
        if condition_type != 'boolean':
            raise RuntimeError(f'Type error: Expected boolean expression in if condition, but got {condition_type}')

        self.analyze_body(if_body)

        if else_body:
            self.analyze_body(else_body)

    def analyze_while_loop(self, statement):
        _, condition, body = statement
        condition_type = self.analyze_expression(condition)
        if condition_type != 'boolean':
            raise RuntimeError(f'Type error: Expected boolean expression in while condition, but got {condition_type}')

        self.analyze_body(body)
    
    def analyze_for_loop(self, statement):
        _, variable, end, body = statement
        if variable in self.symbol_table:
            raise RuntimeError(f'Variable {variable} already declared')
        self.symbol_table[variable] = 'number'
        self.analyze_body(body)

    def analyze_expression(self, expression):
        if type(expression) is tuple:
            if expression[0] == 'operation':
                _, left, op, right = expression
                left_type = self.analyze_expression(left)
                right_type = self.analyze_expression(right)
                # AND / OR
                if op in {'😍😍', '😘🤨'}:
                    if left_type == 'boolean' and right_type == 'boolean':
                        return 'boolean'
                    else:
                        raise RuntimeError(f'Type error: Expected boolean operands for {op}, but got {left_type} and {right_type}')
                # == / !+ / < / > / <= / >=
                elif op in {'♊', '♓', '🐜', '🐘', '🐜🐞', '🐘🦣'}:
                    if left_type == right_type:
                        return 'boolean'
                    else:
                        raise RuntimeError(f'Type error: Expected matching types for {op}, but got {left_type} and {right_type}')
                # +
                elif op == '🤰':
                    # TODO: Concatenate strings?
                    if left_type == right_type == 'number':
                        return 'number'
                    else:
                        raise RuntimeError(f'Type error: Expected number operands for addition, but got {left_type} and {right_type}')
                # -
                elif op == '🔫':
                    if left_type == right_type == 'number':
                        return 'number'
                    else:
                        raise RuntimeError(f'Type error: Expected number operands for subtraction, but got {left_type} and {right_type}')
                # *
                elif op == '🙅‍♂️':
                    if left_type == right_type == 'number':
                        return 'number'
                    else:
                        raise RuntimeError(f'Type error: Expected number operands for multiplication, but got {left_type} and {right_type}')
                # /
                elif op == '🇦🇴':
                    if left_type == right_type == 'number':
                        return 'number'
                    else:
                        raise RuntimeError(f'Type error: Expected number operands for division, but got {left_type} and {right_type}')
            elif expression[0] == 'input':
                return 'string'
        elif type(expression) is str:
            if expression.isdigit():
                return 'number'
            elif expression == '✅' or expression == '❎':
                return 'boolean'
            elif expression.startswith('🌪️') and expression.endswith('🌪️'):
                return 'string'
            elif expression in self.symbol_table:
                return self.symbol_table[expression]
            else:
                raise RuntimeError(f'Undefined variable: {expression}')
        else:
            raise RuntimeError(f'Unexpected expression type: {expression}')

class Transpiler:
    def __init__(self, ast):
        self.ast = ast

    def transpile(self):
        return self.transpile_body(self.ast)
    
    def transpile_body(self, body):
        result = []
        for statement in body:
            result.append(self.transpile_statement(statement))

        return '\n'.join(result)
    
    def transpile_statement(self, statement):
        if statement[0] == 'variable_declaration':
            return self.transpile_variable_declaration(statement)
        elif statement[0] == 'output':
            return self.transpile_output(statement)
        elif statement[0] == 'input':
            return self.transpile_input(statement)
        elif statement[0] == 'conditional':
            return self.transpile_conditional(statement)
        elif statement[0] == 'while_loop':
            return self.transpile_while_loop(statement)
        elif statement[0] == 'for_loop':
            return self.transpile_for_loop(statement)
        else:
            raise RuntimeError(f'Unknown statement type: {statement[0]}')
        
    def transpile_variable_declaration(self, statement):
        _, var_type, identifier, value = statement
        return f'{identifier} = {self.transpile_expression(value)}'
    
    def transpile_output(self, statement):
        _, value = statement
        # print(self.indent_level)
        return f'print({self.transpile_expression(value)})'
    
    def transpile_input(self, statement):
        _, value = statement
        if value:
            return f'input({self.transpile_expression(value)})'
        else:
            return 'input()'
        
    def transpile_conditional(self, statement):
        if len(statement) == 4:
            _, condition, if_body, else_body = statement
        else:
            _, condition, if_body = statement
            else_body = None
        result = []
        result.append(f'if {self.transpile_expression(condition)}:')
        result.append(self.indent_code(self.transpile_body(if_body)))

        if else_body:
            result.append('else:')
            result.append(self.indent_code(self.transpile_body(else_body)))

        return '\n'.join(result)
    
    def transpile_while_loop(self, statement):
        _, condition, body = statement
        result = []
        result.append(f'while {self.transpile_expression(condition)}:')
        result.append(self.indent_code(self.transpile_body(body)))
        return '\n'.join(result)
    
    def transpile_for_loop(self, statement):
        _, variable, end, body = statement
        result = []
        result.append(f'for {variable} in range({end}):')
        result.append(self.indent_code(self.transpile_body(body)))
        return '\n'.join(result)
    
    def transpile_expression(self, expression):
        if type(expression) is tuple:
            if expression[0] == 'operation':
                _, left, op, right = expression
                op_map = {
                    '😍😍': 'and',
                    '😘🤨': 'or',
                    '♊': '==',
                    '♓': '!=',
                    '🐜': '<',
                    '🐘': '>',
                    '🐜🐞': '<=',
                    '🐘🦣': '>=',
                    '🤰': '+',
                    '🔫': '-',
                    '🙅‍♂️': '*',
                    '🇦🇴': '/',
                }

                return f'{self.transpile_expression(left)} {op_map[op]} {self.transpile_expression(right)}'
            elif expression[0] == 'input':
                return f'input({self.transpile_expression(expression[1])})'
        elif type(expression) is str:
            if expression.isdigit():
                return expression
            elif expression == '✅':
                return 'True'
            elif expression == '❎':
                return 'False'
            elif expression.startswith('🌪️') and expression.endswith('🌪️'):
                return f'\'{expression[2:-2]}\''
            else:
                return expression
            
        else:
            raise RuntimeError(f'Unexpected expression type: {expression}')
        
    def indent_code(self, code):
        indentation = '    '
        return '\n'.join(indentation + line for line in code.split('\n'))

parser = argparse.ArgumentParser(description='Transpile Python code and optionally run it.')

parser.add_argument('--in', dest='input_file', default='example.pye', help='Input Python file path (default: example.pye)')
parser.add_argument('--out', dest='output_file', default='example.py', help='Output transpiled file path (default: example.py)')
parser.add_argument('--run', action='store_true', help='Run the transpiled code')
parser.add_argument('--debug', action='store_true', help='Print debug information')

args = parser.parse_args()

with open(args.input_file, 'r', encoding='utf-8') as file:
    emojicode = file.read()

tokens = tokenize(emojicode)
parser = Parser(tokens)
ast = parser.parse()

semantic_analyzer = SemanticAnalyzer(ast)
semantic_analyzer.analyze()

transpiler = Transpiler(ast)
python_code = transpiler.transpile()

with open(args.output_file, 'w', encoding='utf-8') as output_file:
    output_file.write(python_code)
    print(f'Python code transpiled to {args.output_file}')

if args.run:
    os.system(f'python {args.output_file}')
