class SymbolTable:
    def __init__(self):
        # Будем хранить: key = имя (str), value = словарь с полями
        #   'kind': 'var' или 'array'
        #   'type': 'int' или 'float'
        #   'size': если массив, то выражение размера (целочисленное)
        #   'address': если вы хотите симулировать реальные адреса, или None
        #   'value': для скалярных переменных (при интерпретации RPN)
        #   'elements': для массивов (список или None до выделения)
        self.table = {}

    def declare_variable(self, name: str, var_type: str, line=None, column=None):
        """
        Объявление скалярной переменной.
        var_type: 'int' или 'float'
        """
        if name in self.table:
            raise SyntaxError(f"Line {line}:{column}: Variable '{name}' already declared")
        self.table[name] = {
            'kind': 'var',
            'type': var_type,
            'value': None,     # место для хранения (при интерпретации)
            'address': None    # если бы выделяли адреса в памяти
        }

    def declare_array(self, name: str, var_type: str, size: int, line=None, column=None):
        """
        Объявление массива. Размер size уже должен быть вычислен как int ≥ 0.
        """
        if name in self.table:
            raise SyntaxError(f"Line {line}:{column}: Array '{name}' already declared")
        if size < 0:
            raise SyntaxError(f"Line {line}:{column}: Array '{name}' declared with negative size {size}")
        # Для упрощения храним список заранее заполненный нулями (или None)
        elements = [0] * size if var_type == 'int' else [0.0] * size
        self.table[name] = {
            'kind': 'array',
            'type': var_type,
            'size': size,
            'elements': elements,
            'address': None
        }

    def is_declared(self, name: str):
        return name in self.table

    def get_entry(self, name: str):
        return self.table.get(name)

    def set_variable(self, name: str, value):
        """
        При интерпретации: установить скалярную переменную в value.
        """
        entry = self.table.get(name)
        if entry is None:
            raise NameError(f"Variable '{name}' is not declared")
        if entry['kind'] != 'var':
            raise TypeError(f"'{name}' is not a scalar variable")
        # Проверка типов: int ← int, float ← int/float
        if entry['type'] == 'int':
            if not isinstance(value, int):
                raise TypeError(f"Cannot assign {type(value).__name__} to int variable '{name}'")
        elif entry['type'] == 'float':
            if not isinstance(value, (int, float)):
                raise TypeError(f"Cannot assign {type(value).__name__} to float variable '{name}'")
            if isinstance(value, int):
                value = float(value)
        entry['value'] = value

    def get_variable(self, name: str):
        entry = self.table.get(name)
        if entry is None:
            raise NameError(f"Variable '{name}' is not declared")
        if entry['kind'] != 'var':
            raise TypeError(f"'{name}' is not a scalar variable")
        return entry['value']

    def set_array_element(self, name: str, index: int, value):
        """
        При интерпретации: установить a[index] = value.
        """
        entry = self.table.get(name)
        if entry is None:
            raise NameError(f"Array '{name}' is not declared")
        if entry['kind'] != 'array':
            raise TypeError(f"'{name}' is not an array")
        if not (0 <= index < entry['size']):
            raise IndexError(f"Index {index} out of bounds for array '{name}' of size {entry['size']}")
        # Приведение типа
        if entry['type'] == 'int':
            if not isinstance(value, int):
                raise TypeError(f"Cannot assign {type(value).__name__} to int array '{name}' element")
        else:  # float array
            if not isinstance(value, (int, float)):
                raise TypeError(f"Cannot assign {type(value).__name__} to float array '{name}' element")
            if isinstance(value, int):
                value = float(value)
        entry['elements'][index] = value

    def get_array_element(self, name: str, index: int):
        entry = self.table.get(name)
        if entry is None:
            raise NameError(f"Array '{name}' is not declared")
        if entry['kind'] != 'array':
            raise TypeError(f"'{name}' is not an array")
        if not (0 <= index < entry['size']):
            raise IndexError(f"Index {index} out of bounds for array '{name}' of size {entry['size']}")
        return entry['elements'][index]
