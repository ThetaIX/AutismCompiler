<div align="center">
<img src="/tests/photo_2025-06-03_13-06-18.jpg" width="300"  alt="ЛОГО">
</div>

# Autism Interpreter

A simple experimental interpreter and programming language implementation.

<div align="center">
<img src="https://static.wikia.nocookie.net/the-curse-of-the-wise-tree/images/e/e4/Mudroe-tainstvennoe-derevo-mem-25.jpg/revision/latest?cb=20230102165328&path-prefix=ru" width="900" height="120" alt="МУДРЫЙ ДУБ">
</div>

## Features

- Implemented in `Python`
- Basic symbol table implementation (without memory addresses)
- Static type system with support for:
  - `float`
  - `int`
- Static arrays support
- Control flow structures:
  - `while` loops
  - `if...else` conditional statements

## Language Grammar

<div align="center">
<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcROiCgl0L9JBN-30N7OMpv8L_4xy7oP4yMmXw&s" width="900" height="250" alt="HYPERPIGMINTATION">
</div>

The language follows this formal grammar:

```
P → A                         // Program
A → Q ; A | λ                // Sequence of statements
Q → E | C | L | I | O | M | Z // Statement types

E → aK = S                   // Assignment
M → array Z                  // Array declaration
Z → int aK | float aK       // Type declarations
S → S + T | S - T | T       // Addition/Subtraction
T → T * F | T / F | F       // Multiplication/Division
F → (S) | aK | k | -F | λ   // Factors
K → [S] | λ                 // Array indexing

C → if (V) {A} H            // Conditional
H → else {A} | λ            // Optional else
L → while (V) {A}           // Loop
V → S W S                   // Condition
W → == | != | < | >         // Comparison operators

I → input aK                // Input
O → output S                // Output
```

Where:
- `a` represents an identifier
- `k` represents a numeric constant
- `λ` represents an empty production

## Syntax Examples

<div align="center">
<img src="https://i.pinimg.com/originals/23/65/4f/23654f017292254595cdf4dcba918f42.jpg" width="1300" height="150" alt="AUTISM!!!">
</div>

```
// Variable declarations
int x;
float y;

// Array declarations
array int numbers[10];
array float values[5];

// Input/Output
input x;
output x + 5;

// Array operations
numbers[0] = 42;
output numbers[i];

// Arithmetic expressions
x = (5 + 3) * 2;
y = -x + 10;

// Control structures
if (x > 0) {
    output x;
} else {
    output -x;
};

while (x < 10) {
    x = x + 1;
    output x;
};
```

## Project Status

This is an experimental project in development. Future updates will include:
- Formal grammar specification
- More data types and features

## Getting Started

### File Extension
Source code files for the Autism programming language must use the `.aul` extension.

### Running Programs
To run a program, use the autism.exe executable. Make sure you're in the directory containing the executable or use the full path:

```bash
# If you're in the same directory as autism.exe
.\autism.exe your_program.aul

# If you're running from another directory
.\path\to\autism.exe your_program.aul
```

If no source file is provided, the interpreter will run with a default example program that demonstrates basic arithmetic operations.

### Example Program

<div align="center">
<img src="https://i.redd.it/mmum0i3dzzed1.jpeg" width="1000" height="150" alt="WHY SO SERIOUS">
</div>

Create a file `example.aul` with the following content:
```
int wiseTree;
wiseTree = 65;
int joker;
joker = 4;
output wiseTree + joker;
```

Then run it using:
```bash
# Run the program
.\path\to\interpreter\dist\autism.exe example.aul
```

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.

## Contributors

<div align="center">
<img src="https://kirov-portal.ru/upload/original/news/57f/57fa50e6f1edd2c533df422206235138.jpg" width="1000" height="100" alt="КОМАНДА">
</div>

### Core Team

| Contributor | Role | Responsibilities |
|------------|------|------------------|
| **ThetaIX** | Lead Developer | • Language grammar design<br>• Parser implementation<br>• Interpreter development |
| **Bear-Creator** | Technical Lead | • Semantic analysis<br>• Lexical analyzer (Lexer)<br>• Core language features |
| **MankaShev** | Documentation Lead | • Technical documentation<br>• Transition and symbol tables<br>• Project documentation |

### Special Thanks

Thanks to everyone who has contributed to making this project possible. If you'd like to contribute, please check our [Contributing](#contributing) section above.
