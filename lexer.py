import re

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self):
        return f'Token({self.type}, {self.value!r}, line={self.line}, col={self.column})'

class Lexer:
    def __init__(self):
        # Словарь лексем с их типами
        self.token_specs = {
            'if': ('KEYWORD', 1), 'else': ('KEYWORD', 2), 'while': ('KEYWORD', 3),
            'array': ('KEYWORD', 5), 'input': ('KEYWORD', 6), 'output': ('KEYWORD', 7),
            '+': ('OPERATOR', 8), '-': ('OPERATOR', 9), '*': ('OPERATOR', 10), '/': ('OPERATOR', 11),
            '=': ('ASSIGN_OP', 12), '==': ('COMP_OP', 13), '!=': ('COMP_OP', 14),
            '<': ('COMP_OP', 15), '>': ('COMP_OP', 16),
            '(': ('PAREN', 17), ')': ('PAREN', 18), '[': ('BRACKET', 19), ']': ('BRACKET', 20),
            '{': ('BRACE', 21), '}': ('BRACE', 22), ';': ('DELIMITER', 23), ',': ('DELIMITER', 24)
        }
        # Таблица переходов конечного автомата
        self.transitions = {
            'S': {
                'letter': ('A', 0), 'digit': ('B', 1), '+': ('E', 2), '-': ('E', 3), '*': ('E', 4), '/': ('E', 5),
                '=': ('E', 6), '<': ('E', 7), '>': ('E', 8), '!': ('E', 9), '.': ('Z', 27), ',': ('E', 11),
                '(': ('E', 12), ')': ('E', 13), '[': ('E', 14), ']': ('E', 15), '{': ('E', 16), '}': ('E', 17),
                ';': ('E', 18), 'space': ('S', 19), 'other': ('Z', 20), '\n': ('S', 21), 'EOF': ('E', 22)
            },
            'A': {
                'letter': ('A', 23), 'digit': ('A', 23), '+': ('E*', 24), '-': ('E*', 24), '*': ('E*', 24),
                '/': ('E*', 24), '=': ('E*', 24), '<': ('E*', 24), '>': ('E*', 24), '!': ('E*', 24), '.': ('Z', 27),
                ',': ('E*', 24), '(': ('E*', 24), ')': ('E*', 24), '[': ('E*', 24), ']': ('E*', 24), '{': ('E*', 24),
                '}': ('E*', 24), ';': ('E*', 24), 'space': ('E', 24), 'other': ('Z', 27), '\n': ('E', 24), 'EOF': ('E', 22)
            },
            'B': {
                'letter': ('Z', 27), 'digit': ('B', 25), '+': ('E*', 26), '-': ('E*', 26), '*': ('E*', 26),
                '/': ('E*', 26), '=': ('E*', 26), '<': ('E*', 26), '>': ('E*', 26), '!': ('E*', 26), '.': ('C', 31),
                ',': ('E*', 26), '(': ('Z', 27), ')': ('E*', 26), '[': ('E*', 26), ']': ('E*', 26), '{': ('Z', 27),
                '}': ('E*', 26), ';': ('E*', 26), 'space': ('E', 26), 'other': ('Z', 27), '\n': ('E', 26), 'EOF': ('E', 22)
            },
            'C': {
                'letter': ('Z', 27), 'digit': ('D', 28), '+': ('Z', 27), '-': ('Z', 27), '*': ('Z', 27),
                '/': ('Z', 27), '=': ('Z', 27), '<': ('Z', 27), '>': ('Z', 27), '!': ('Z', 27), '.': ('Z', 27),
                ',': ('Z', 27), '(': ('Z', 27), ')': ('Z', 27), '[': ('Z', 27), ']': ('Z', 27), '{': ('Z', 27),
                '}': ('Z', 27), ';': ('Z', 27), 'space': ('Z', 27), 'other': ('Z', 27), '\n': ('Z', 27), 'EOF': ('Z', 27)
            },
            'D': {
                'letter': ('Z', 27), 'digit': ('D', 28), '+': ('E*', 30), '-': ('E*', 30), '*': ('E*', 30),
                '/': ('E*', 30), '=': ('E*', 30), '<': ('E*', 30), '>': ('E*', 30), '!': ('E*', 30), '.': ('Z', 27),
                ',': ('E*', 30), '(': ('Z', 27), ')': ('E*', 30), '[': ('Z', 27), ']': ('E*', 30), '{': ('Z', 27),
                '}': ('Z', 27), ';': ('E*', 30), 'space': ('E', 30), 'other': ('Z', 27), '\n': ('E', 30), 'EOF': ('E', 30)
            }
        }
        # Регулярные выражения для идентификаторов и чисел
        self.patterns = [
            (r'^[a-zA-Z][a-zA-Z0-9]*$', 'ID'),
            (r'^\d+\.\d+$', 'FLOAT'),
            (r'^\d+$', 'INT')
        ]

    def get_input_category(self, char, is_eof=False):
        if is_eof:
            return 'EOF'
        if char.isalpha():
            return 'letter'
        if char.isdigit():
            return 'digit'
        if char in '+-*/=<>!,.()[]{};':
            return char
        if char.isspace() and char != '\n':
            return 'space'
        if char == '\n':
            return '\n'
        return 'other'

    def tokenize(self, code):
        tokens = []
        errors = []
        state = 'S'
        buffer = ''
        line = 1
        column = 0
        number = 0  # целая часть
        decimal = 1  # множитель для дробной части
        value = 0  # для хранения дробной части
        pos = 0

        def emit(type, val, ln, col):
            tokens.append(Token(type, val, ln, col))

        while pos <= len(code):
            is_eof = (pos == len(code))
            char = '' if is_eof else code[pos]
            category = self.get_input_category(char, is_eof)
            next_state, action = self.transitions[state].get(category, ('Z', 27))

            # Семантика
            if action == 0:
                buffer = char
                start_col = column
            elif action == 1:
                number = ord(char) - ord('0')
                value = 0  # Сбрасываем value при начале нового числа
                buffer = char
                start_col = column
            elif action in range(2, 19):
                if char in self.token_specs:
                    ttype, _ = self.token_specs[char]
                    emit(ttype, char, line, column)
                else:
                    errors.append(f"Line {line}, col {column}: invalid symbol '{char}'")
            elif action == 19:
                pass
            elif action == 20:
                errors.append(f"Line {line}, col {column}: invalid char '{char}'")
            elif action == 21:
                line += 1
                column = 0
            elif action == 22:
                break
            elif action == 23:
                buffer += char
            elif action == 24:
                buf_type = next((t for p, t in self.patterns if re.match(p, buffer)), None)
                if buffer in self.token_specs:
                    ttype, _ = self.token_specs[buffer]
                elif buf_type:
                    ttype = buf_type
                else:
                    ttype = 'ERROR'
                    errors.append(f"Line {line}, col {start_col}: invalid token '{buffer}'")
                emit(ttype, buffer, line, start_col)
                buffer = ''
            elif action == 25:
                number = number * 10 + (ord(char) - ord('0'))
                buffer += char
            elif action == 26:
                emit('INT', str(number), line, start_col)
                buffer = ''
                number = 0
                value = 0  # Сбрасываем value
                decimal = 1
            elif action == 27:
                errors.append(f"Line {line}, col {column}: invalid sequence '{buffer + char}'")
                buffer = ''
            elif action == 28:
                decimal *= 0.1
                value = value + (ord(char) - ord('0')) * decimal  # Изменено: накапливаем дробную часть в value
                buffer += char
            elif action == 30:
                final_value = float(number) + value  # Изменено: правильное сложение целой и дробной части
                emit('FLOAT', str(final_value), line, start_col)
                buffer = ''
                number = 0
                value = 0
                decimal = 1
            elif action == 31:  # Переход от целой части к дробной
                buffer += char
                value = 0  # Сбрасываем value для новой дробной части
                decimal = 1

            if next_state == 'E*':
                pos -= 1
                next_state = 'E'

            state = next_state
            pos += 1
            column += 1

            if state in ['E', 'Z']:
                state = 'S'

        return tokens, errors

    def run(self, code):
        tokens, errors = self.tokenize(code)
        for t in tokens:
            print(t)
        if errors:
            print("\nLexical errors:")
            for e in errors:
                print(e)

# Пример использования
if __name__ == '__main__':
    sample = '''
int x;
x = 10
while(x > 10)
{
    output x; 
    x = x - 1;
}
invalid$token;
'''  
    Lexer().run(sample)
