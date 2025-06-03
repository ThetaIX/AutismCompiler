# Autism Compiler

A simple experimental compiler and programming language implementation.

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
Source code files for the Autism programming language must use the `.au` extension.

### Running Programs
To run a program, use the autism.exe executable:
```bash
autism.exe your_program.au
```

If no source file is provided, the compiler will run with a default example program that demonstrates basic arithmetic operations.

### Example Program
Create a file `example.au` with the following content:
```
int x;
int y;
float z;
input x;
input y;
z = x * 2 + (y - 3) / 2 - (6 * (x - 1));
output z;
```

Then run it using:
```bash
autism.exe example.au
```

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.

## Contributors

### Core Team

| Contributor | Role | Responsibilities |
|------------|------|------------------|
| **ThetaIX** | Lead Developer | • Language grammar design<br>• Parser implementation<br>• Interpreter development |
| **Bear-Creator** | Technical Lead | • Semantic analysis<br>• Lexical analyzer (Lexer)<br>• Core language features |
| **MankaShev** | Documentation Lead | • Technical documentation<br>• Transition and symbol tables<br>• Project documentation |

### Special Thanks

Thanks to everyone who has contributed to making this project possible. If you'd like to contribute, please check our [Contributing](#contributing) section above.
