from var_table import SymbolTable

def interpret_rpn(rpn_list, symtable: SymbolTable):
    """
    Примитивный интерпретатор: читает rpn_list, оперирует стеком и symtable.
    symtable уже заполнен объявлениями в парсинге.
    """
    pc = 0  # счётчик команд в RPN
    stack = []

    while pc < len(rpn_list):
        instr = rpn_list[pc]

        if isinstance(instr, tuple):
            tag = instr[0]
        else:
            tag = instr
            
        if tag == "CONST_INT":
            stack.append(instr[1])
            pc += 1

        elif tag == "CONST_FLOAT":
            stack.append(instr[1])
            pc += 1

        elif tag == "VAR":
            # просто кладём на стек текущее значение переменной/ячейки
            var_name = instr[1]
            entry = symtable.get_entry(var_name)
            if entry['kind'] == 'var':
                val = symtable.get_variable(var_name)
                stack.append((var_name,val))
            else:
                # Если это массив, без индексатора — ошибка
                raise RuntimeError(f"Expected scalar but '{var_name}' is an array")
            pc += 1
        
        elif tag == "ARR":
            arr_name = instr[1]
            entry = symtable.get_entry(arr_name)
            if entry['kind'] == 'array':
                val = entry['size']
                stack.append((arr_name,val))
            else:
                raise RuntimeError(f"Expected array but '{var_name}' is an variable")
            pc += 1
            
        elif tag == "ARRAY_INDEX":
            # Берём индекс (справа в стеке) и имя массива (левее в стеке)
            idx = stack.pop()
            idx = idx[1] if isinstance(idx, tuple) else idx
            arr_name = stack.pop()[0]
            # Но тут нужно уточнить: ведь в RPN раньше мы клали ("VAR", arr_name), а после него CONST_INT idx
            # То есть в стеке были [..., arr_name, idx]. Здесь arr_name — строка, idx — число.
            if not isinstance(arr_name, str):
                raise RuntimeError(f"Invalid array access: expected array name, got {arr_name}")
            element = symtable.get_array_element(arr_name, idx)
            stack.append((arr_name, element, idx))
            pc += 1

        elif tag == "BIN_OP":
            op = instr[1]
            
            b = stack.pop() 
            a = stack.pop()
            b = b[1] if isinstance(b,tuple) else b
            a = a[1] if isinstance(a,tuple) else a
            if op == '+':
                stack.append(a + b)
            elif op == '-':
                stack.append(a - b)
            elif op == '*':
                stack.append(a * b)
            elif op == '/':
                stack.append(a / b)  # при int/int → float, если нужно целочисленное деление, заменить на a//b
            else:
                raise RuntimeError(f"Unknown binary operator '{op}'")
            pc += 1

        elif tag == "UNARY_OP":
            # u- → унарный минус
            v = stack.pop()
            v = v[1] if isinstance(v,tuple) else v
            stack.append(-v)
            pc += 1

        elif tag == "COMPARE":
            comp_op = instr[1]
            b = stack.pop()
            a = stack.pop()
            b = b[1] if isinstance(b,tuple) else b
            a = a[1] if isinstance(a,tuple) else a
            res = None
            if comp_op == '<':
                res = 1 if a < b else 0
            elif comp_op == '>':
                res = 1 if a > b else 0
            elif comp_op == '<=':
                res = 1 if a <= b else 0
            elif comp_op == '>=':
                res = 1 if a >= b else 0
            elif comp_op == '==':
                res = 1 if a == b else 0
            elif comp_op == '!=':
                res = 1 if a != b else 0
            else:
                raise RuntimeError(f"Unknown comparison '{comp_op}'")
            stack.append(res)
            pc += 1

        elif tag == "ASSIGN":
            # Присваивание: стек: [..., значение, адрес_ячейки]
            value = stack.pop()
            value = value[1] if isinstance(value,tuple) else value
            addr = stack.pop()
            # addr может быть либо строка (имя переменной), либо (имя массива, индекс), 
            # но у нас мы клали в стек так: ("VAR", name) → мы вытаскивали просто name (строка).
            # А в случае массива, при присваивании a[K] = S, мы перед ARRAY_INDEX
            # положили сначала ("VAR", "a") (что интерпретируется как строка "a"), 
            # потом CONST_INT K → потом при ARRAY_INDEX подряд извлекаем (a, K).
            if isinstance(addr, tuple) and len(addr) == 3:
                if symtable.get_entry(addr[0])['kind'] == 'array':
                    symtable.set_array_element(addr[0], addr[2], value)
                else:
                    raise RuntimeError(f"Invalid ASSIGN target: {addr[0]}")
            elif isinstance(addr, tuple) and len(addr) == 2:
                if symtable.get_entry(addr[0])['kind'] == 'var':
                    symtable.set_variable(addr[0], value)
                else:
                    raise RuntimeError(f"Invalid ASSIGN target: {addr[0]}")
            else:
                raise RuntimeError(f"Invalid ASSIGN target: {addr[0]}")
            pc += 1

        elif tag == "JF":
            # В ячейке слева лежит адрес перехода (целое)
            target = rpn_list[pc-1]  # предыдущая ячейка
            condition = stack.pop()
            if condition == 0:
                # Прыгаем
                pc = target
            else:
                pc += 1

        elif tag == "J":
            target = rpn_list[pc-1]
            pc = target

        elif tag == "READ":
            # Оператор input: из stdin читаем число (int или float?), 
            # но для простоты возьмём int
            value = input(">> ")
            value = float(value) if '.' in value else int(value)
            var_name = stack.pop()
            if isinstance(var_name, tuple) and len(var_name) == 3:
                if symtable.get_entry(var_name[0])['kind'] == 'array':
                    symtable.set_array_element(var_name[0], var_name[2], value)
                else:
                    raise RuntimeError(f"Invalid ASSIGN target: {var_name[0]}")
            elif isinstance(var_name, tuple) and len(var_name) == 2:
                if symtable.get_entry(var_name[0])['kind'] == 'var':
                    symtable.set_variable(var_name[0], value)
                else:
                    raise RuntimeError(f"Invalid ASSIGN target: {var_name[0]}")
            else:
                raise RuntimeError(f"Invalid ASSIGN target: {var_name[0]}")
            pc += 1

        elif tag == "WRITE":
            value = stack.pop()
            value = value[1] if isinstance(value, tuple) else value
            print("<<", value)
            pc += 1

        elif isinstance(tag, int):
            pc += 1
        
        elif tag == "EXIT":
            print(f"Execution finished with code {instr[1]}")
            # print('Final Symbol Table:')
            # for name, entry in symtable.table.items():
            #     print(name, entry)
            # input("Press any button to exit")
            break
        
        else:
            raise RuntimeError(f"Unknown instruction {instr} at pc={pc}")

    
