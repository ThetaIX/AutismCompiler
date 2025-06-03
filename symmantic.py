from collections import deque
from lexer import Lexer, Token
from var_table import SymbolTable
from interpretator import interpret_rpn

# ----- Парсер с семантикой -----
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = deque()
        self.current = None

        # Вот куда будем складывать итоговый RPN-код (список строк и/или чисел).
        self.output = []

        # Таблица символов (отвечает за объявления и значения переменных/массивов).
        self.symtable = SymbolTable()

    def _advance(self):
        if not self.tokens:
            return
        self.current = self.tokens.popleft()

    def _eat(self, expected_type=None, expected_value=None):
        token = self.current
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected token type {expected_type}, got {token} at line {token.line}")
        if expected_value and token.value != expected_value:
            raise SyntaxError(f"Expected token value '{expected_value}', got {token} at line {token.line}")
        self._advance()
        return token

    def parse(self, code):
        toks, errors = self.lexer.tokenize(code)
        if errors:
            raise SyntaxError(f"Lexical errors: {errors}")
        # Добавляем токен EOF
        self.tokens = deque(toks + [Token('EOF', '', toks[-1].line, toks[-1].column+1)])
        self._advance()

        # Стартовый символ грамматики
        self.parse_A()

        # В конце добавляем «exit»-метку (код завершения)
        self.output.append(("EXIT", 0))
        return self.output

    # ---------------------------------------------------
    # A → aK = S; A
    #   | if ( V ) { A } H; A
    #   | while ( V ) { A }; A
    #   | input a; A
    #   | output S; A
    #   | array Q'; A
    #   | float a; A
    #   | int a; A
    #   | λ
    # ---------------------------------------------------
    def parse_A(self):
        while self.current.type != 'EOF' and self.current.value != '}':
            # ---------------- if ( V ) { A } [else { A } ] ; ----------------
            if self.current.value == 'if':
                self._eat(expected_value='if')
                self._eat(expected_value='(')
                self.parse_V()                 # кладёт RPN для условия (S COMP_OP S)

                # Зарезервировать место для "jump if false"
                pos_jf = len(self.output)
                self.output.append(None)       # потом сюда подставим адрес (int)
                self.output.append(("JF", None))

                self._eat(expected_value=')')
                self._eat(expected_value='{')
                self.parse_A()                 # рекурсивно тело if
                self._eat(expected_value='}')

                # Проверить, есть ли ветка else
                if self.current.value == 'else':
                    # Если есть else, нужно сначала вставить безусловный переход после тела if
                    pos_j = len(self.output)
                    self.output.append(None)   # адрес, куда прыгаем после else
                    self.output.append(("J", None))

                    # Теперь заполняем куда прыгать, если условие ложно:
                    self.output[pos_jf] = len(self.output)

                    self._eat(expected_value='else')
                    self._eat(expected_value='{')
                    self.parse_A()             # тело else
                    self._eat(expected_value='}')
                    # После else заполняем адрес, куда прыгать из if-true, чтобы пропустить else
                    self.output[pos_j] = len(self.output)

                else:
                    # Если else нет, то просто заполняем адрес для jf: выход из if
                    self.output[pos_jf] = len(self.output)

                self._eat(expected_value=';')


            # ---------------- while ( V ) { A } ; ----------------
            elif self.current.value == 'while':
                self._eat(expected_value='while')

                # Сохраняем адрес начала проверки условия
                pos_loop_start = len(self.output)

                self._eat(expected_value='(')
                self.parse_V()  # кладёт RPN: S COMP_OP S

                # Зарезервировать место для "jump if false" (выход из цикла)
                pos_jf = len(self.output)
                self.output.append(None)
                self.output.append(("JF", None))

                self._eat(expected_value=')')
                self._eat(expected_value='{')
                self.parse_A()  # тело цикла
                # После тела — безусловный переход обратно на pos_loop_start
                self.output.append(pos_loop_start) #!!!!!!!!!!
                self.output.append(("J", None))

                self._eat(expected_value='}')
                self._eat(expected_value=';')

                # Теперь заполняем адрес, куда прыгает JF (если условие ложно)
                self.output[pos_jf] = len(self.output)


            # ---------------- input a; ----------------
            elif self.current.value == 'input':
                self._eat(expected_value='input')
                var_token = self._eat('ID')
                var_name = var_token.value

                # Проверяем, что переменная объявлена
                if not self.symtable.is_declared(var_name):
                    raise NameError(f"Line {var_token.line}: Variable '{var_name}' is not declared for input")

                
                # RPN: (имя переменной, команда READ)
                if self.current.value == '[':
                    self.output.append(("ARR", var_name))
                    self.parse_K()
                else:
                    self.output.append(("VAR", var_name))
                self._eat(expected_value=';')
                self.output.append(("READ", None))


            # ---------------- output S; ----------------
            elif self.current.value == 'output':
                self._eat(expected_value='output')
                self.parse_S()   # кладёт RPN для S
                self._eat(expected_value=';')
                self.output.append(("WRITE", None))


            # ---------------- array Q'; ----------------
            elif self.current.value == 'array':
                self._eat(expected_value='array')

                # В RPN просто помечаем, что начинается объявление массива:
                # Но главное — вызвать parse_Q(), чтобы в таблицу символов добавить массив.
                #self.output.append(("ARRAY_DECL", None))

                self.parse_Q()    # внутри добавится (type, name, size) + сама регистрация в symtable
                self._eat(expected_value=';')


            # ---------------- float a; ----------------
            elif self.current.value == 'float':
                decl_tok = self._eat(expected_value='float')
                var_tok = self._eat('ID')
                var_name = var_tok.value
                self._eat(expected_value=';')

                # Семантическое действие: объявляем скалярную переменную типа float
                self.symtable.declare_variable(var_name, 'float', decl_tok.line, decl_tok.column)

                # RPN: маркер DECL_FLOAT + имя переменной
                #self.output.append(("DECL_FLOAT", var_name))


            # ---------------- int a; ----------------
            elif self.current.value == 'int':
                decl_tok = self._eat(expected_value='int')
                var_tok = self._eat('ID')
                var_name = var_tok.value
                self._eat(expected_value=';')

                # Семантическое действие: объявляем скалярную переменную типа int
                self.symtable.declare_variable(var_name, 'int', decl_tok.line, decl_tok.column)

                # RPN: маркер DECL_INT + имя переменной
                #self.output.append(("DECL_INT", var_name))


            # ---------------- aK = S; ----------------
            elif self.current.type == 'ID':
                # Присваивание
                id_token = self._eat('ID')
                var_name = id_token.value

                # Сначала проверяем, объявлена ли переменная/массив
                if not self.symtable.is_declared(var_name):
                    raise NameError(f"Line {id_token.line}: Variable '{var_name}' is not declared")

                # В RPN добавляем маркер «VAR var_name» (имя, по которому интерпретатор будет брать ячейку)
                if self.current.value == '[':
                    self.output.append(("ARR", var_name))
                else:
                    self.output.append(("VAR", var_name))

                # optional index K (если a[K])
                self.parse_K()

                # Разбираем символ '='
                self._eat(expected_value='=')
                # Здесь кладём RPN для правой части
                self.parse_S()
                self._eat(expected_value=';')

                # После всего добавляем маркер ASSIGN
                self.output.append(("ASSIGN", None))

            else:
                raise SyntaxError(f"Unexpected token in A: {self.current}")

    # ---------------------------------------------------
    # Q' → (float ID [ S ] ) | (int ID [ S ] )
    # Семантика: объявление массива. Размер S должен быть целочисленным константным выражением.
    # ---------------------------------------------------
    def parse_Q(self):
        # У current уже "int" или "float"
        if self.current.value == 'float':
            decl_tok = self._eat(expected_value='float')
            var_tok = self._eat('ID')
            var_name = var_tok.value

            # Ожидаем '['
            self._eat(expected_value='[')
            # Разбираем S ( RPN для размера массива )
            size_rpn_start = len(self.output)
            self.parse_S()
            # Теперь size_rpn_end = len(self.output)-1

            # Попытаемся вычислить размер как константу
            size = self.evaluate_constant(self.output[size_rpn_start:])
            # Удалим фрагмент size из RPN, потому что объявление массива мы реализуем здесь в момент парсинга
            del self.output[size_rpn_start:]

            # Семантическое действие: объявляем массив float var_name размер size
            self.symtable.declare_array(var_name, 'float', size, decl_tok.line, decl_tok.column)

            # В RPN запишем маркер: ARRAY_FLOAT var_name, size
            #self.output.append(("ARRAY_FLOAT", var_name, size))

            self._eat(expected_value=']')

        elif self.current.value == 'int':
            decl_tok = self._eat(expected_value='int')
            var_tok = self._eat('ID')
            var_name = var_tok.value

            self._eat(expected_value='[')
            size_rpn_start = len(self.output)
            self.parse_S()
            size = self.evaluate_constant(self.output[size_rpn_start:])
            del self.output[size_rpn_start:]

            # Семантическое действие
            self.symtable.declare_array(var_name, 'int', size, decl_tok.line, decl_tok.column)
            #self.output.append(("ARRAY_INT", var_name, size))

            self._eat(expected_value=']')

        else:
            raise SyntaxError(f"Unexpected token in Q: {self.current}")

    # ---------------------------------------------------
    # S → T S'
    # ---------------------------------------------------
    def parse_S(self):
        self.parse_T()
        self.parse_S_prime()

    # ---------------------------------------------------
    # S' → + T {output '+'} S' | - T {output '-'} S' | λ
    # ---------------------------------------------------
    def parse_S_prime(self):
        while self.current.value in ('+', '-'):
            op = self._eat(expected_value=self.current.value).value
            self.parse_T()
            self.output.append(("BIN_OP", op))

    # ---------------------------------------------------
    # T → F T'
    # ---------------------------------------------------
    def parse_T(self):
        self.parse_F()
        self.parse_T_prime()

    # ---------------------------------------------------
    # T' → * F {output '*'} T' | / F {output '/'} T' | λ
    # ---------------------------------------------------
    def parse_T_prime(self):
        while self.current.value in ('*', '/'):
            op = self._eat(expected_value=self.current.value).value
            self.parse_F()
            self.output.append(("BIN_OP", op))

    # ---------------------------------------------------
    # F → ( S ) | aK | k | - F
    # ---------------------------------------------------
    def parse_F(self):
        if self.current.value == '(':
            self._eat(expected_value='(')
            self.parse_S()
            self._eat(expected_value=')')

        elif self.current.value == '-':
            self._eat(expected_value='-')
            self.parse_F()
            self.output.append(("UNARY_OP", 'u-'))

        elif self.current.type in ('ID', 'INT', 'FLOAT'):
            tok = self._eat(expected_type=self.current.type)
            if tok.type == 'ID':
                # Использование переменной/массива в выражении: маркер VAR/ARRAY_INDEX позже
                # НО здесь учтём только «чистое» использование скалярного ID, 
                # без индексации. Если индекс есть, parse_K() это обработает.
                if self.current.value == '[':
                    self.output.append(("ARR", tok.value))
                else:
                    self.output.append(("VAR", tok.value))
                self.parse_K()
            elif tok.type == 'INT':
                # Целочисленная константа
                self.output.append(("CONST_INT", int(tok.value)))
            else:  # FLOAT
                self.output.append(("CONST_FLOAT", float(tok.value)))
        else:
            raise SyntaxError(f"Unexpected token in F: {self.current}")

    # ---------------------------------------------------
    # V → S COMP_OP S
    # ---------------------------------------------------
    def parse_V(self):
        self.parse_S()
        comp_tok = self._eat(expected_type='COMP_OP')
        comp_op = comp_tok.value
        self.parse_S()
        # В RPN добавляем маркер COMP_OP
        self.output.append(("COMPARE", comp_op))

    # ---------------------------------------------------
    # K → [ S ] | λ    (индексация массива)
    # ---------------------------------------------------
    def parse_K(self):
        if self.current.value == '[':
            self._eat(expected_value='[')
            self.parse_S()
            # После того как RPN для S (индекс) уже в output, добавляем маркер ARRAY_INDEX
            self.output.append(("ARRAY_INDEX", None))
            self._eat(expected_value=']')

    # ---------------------------------------------------
    # Вспомогательный метод: пытаемся вычислить RPN-цепочку (size_rpn)
    # и вернуть integer. Если невозможно (есть VAR или нецелое), бросаем ошибку.
    # ---------------------------------------------------
    def evaluate_constant(self, fragment):
        """
        fragment — часть self.output, содержащая RPN выражение, 
        которое должно содержать только CONST_INT и BIN_OP.
        Возвращаем целочисленное значение. Если что-то не так, бросаем SyntaxError.
        """
        stack = []
        for node in fragment:
            tag = node[0]
            if tag == "CONST_INT":
                stack.append(node[1])
            elif tag == "BIN_OP":
                op = node[1]
                if len(stack) < 2:
                    raise SyntaxError("Invalid constant expression for array size")
                b = stack.pop()
                a = stack.pop()
                if op == '+':
                    stack.append(a + b)
                elif op == '-':
                    stack.append(a - b)
                elif op == '*':
                    stack.append(a * b)
                elif op == '/':
                    if b == 0:
                        raise ZeroDivisionError("Division by zero in constant expression")
                    stack.append(a // b)
                else:
                    raise SyntaxError(f"Unknown binary operator '{op}' in constant expression")
            else:
                # Если встретили что-то кроме CONST_INT/BIN_OP, значит размер массива 
                # не является константой
                raise SyntaxError("Array size must be a constant integer expression")
        if len(stack) != 1:
            raise SyntaxError("Invalid constant expression for array size")
        result = stack.pop()
        if not isinstance(result, int):
            raise SyntaxError("Array size must be an integer")
        return result

if __name__ == '__main__':
    sample = '''
array int a[3];
int x;
x = 0;
while(x < 3)
{
    input a[x];
    x = x + 1;
};
x = 0;
int tmp;
while(x < 2)
{ 
    if(a[x] > a[x+1])
    {
        tmp = a[x];
        a[x] = a[x+1];
        a[x+1] = tmp;
        x = 0; 
    }
    else
    {
        x = x + 1;
    };
};
'''  
    parser = Parser(Lexer())
    rpn = parser.parse(sample)
    print('RPN:', rpn)
    interpret_rpn(rpn, parser.symtable)