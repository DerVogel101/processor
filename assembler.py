import os
import sys
from dataclasses import dataclass

INSTRUCTIONS = {
    "nop": (0b0000, 0, 0),
    "add": (0b0001, 1, 2),
    "sub": (0b0010, 1, 2),
    "and": (0b0011, 1, 2),
    "or": (0b0100, 1, 2),
    "nor": (0b0101, 1, 2),
    "xor": (0b0110, 1, 2),
    "inc": (0b0111, 1, 0),
    "rolr": (0b1000, 1, 0),
    "bib": (0b1001, 6, 3),
    "jmp": (0b1010, 0, 3),
    "mov": (0b1011, 1, 1),
    "ldi": (0b1100, 1, 4),
    "in": (0b1101, 1, 5),
    "out": (0b1110, 1, 5),
    "rnv": (0b1111, 1, 0)
}

REGISTERS = {
    "a": 0b0000,
    "b": 0b0001,
    "c": 0b0010,
    "d": 0b0011,
    "e": 0b0100,
    "f": 0b0101,
    "g": 0b0110,
    "h": 0b0111,
    "i": 0b1000,
    "j": 0b1001,
    "k": 0b1010,
    "l": 0b1011,
    "m": 0b1100,
    "n": 0b1101,
    "o": 0b1110,
    "flags": 0b1111
}

INOUT = {
    "i0": 0b0000,
    "i1": 0b0001,
    "i2": 0b0010,
    "i3": 0b0011,
    "i4": 0b0100,
    "i5": 0b0101,
    "i6": 0b0110,
    "i7": 0b0111,
    "o0": 0b1000,
    "o1": 0b1001,
    "o2": 0b1010,
    "o3": 0b1011,
    "o4": 0b1100,
    "o5": 0b1101,
    "o6": 0b1110,
    "o7": 0b1111
}

IF_BIT ={
    "a0": 0b0000,
    "a1": 0b0001,
    "a2": 0b0010,
    "a3": 0b0011,
    "a4": 0b0100,
    "a5": 0b0101,
    "a6": 0b0110,
    "a7": 0b0111,
    "z": 0b1000,
    "c": 0b1001,
    "s": 0b1010,
    "f3": 0b1011,
    "f4": 0b1100,
    "f5": 0b1101,
    "f6": 0b1110,
    "f7": 0b1111
}


# load file
def load_code(file_path: str):
    with open(file_path, "r") as f:
        return f.read()


def break_up(asm_code: str):
    lines = []
    for line in asm_code.splitlines():
        stripped = " ".join(line.strip().split())
        lines.append(stripped.split(" "))
    return lines


def convert_to_binary(param_code: list[list[str]]):
    binary_byte_code = []
    jump_labels = {}
    for line in param_code:
        if line[0] in INSTRUCTIONS:
            instruction = INSTRUCTIONS[line[0]]
            opcode = instruction[0]
            if instruction[1] == 0:
                dest = opcode << 4 | 0b0000
                binary_byte_code.append(dest)
            elif instruction[1] == 1:
                if line[1] in REGISTERS:
                    dest = opcode << 4 | REGISTERS[line[1]]
                    binary_byte_code.append(dest)
                else:
                    print(f"Error: {line[1]} is not a valid register")
                    sys.exit(1)
            elif instruction[1] == 6:
                if line[1] in IF_BIT:
                    dest = opcode << 4 | IF_BIT[line[1]]
                    binary_byte_code.append(dest)
                else:
                    print(f"Error: {line[1]} is not a valid IF_BIT")
                    sys.exit(1)
            else:
                print(f"Error: {line[0]} is not a valid instruction")
                sys.exit(1)
            if instruction[2] == 0:
                pass
            elif instruction[2] == 1:
                if line[2] in REGISTERS:
                    params = REGISTERS[line[2]] << 4 | 0b0000
                    binary_byte_code.append(params)
                else:
                    print(f"Error: {line[2]} is not a valid register")
                    sys.exit(1)
            elif instruction[2] == 2:
                if line[2] in REGISTERS:
                    params = REGISTERS[line[2]]
                else:
                    print(f"Error: {line[2]} is not a valid register")
                    sys.exit(1)
                if line[3] in REGISTERS:
                    params = params << 4 | REGISTERS[line[3]]
                else:
                    print(f"Error: {line[3]} is not a valid register")
                    sys.exit(1)
                binary_byte_code.append(params)
            elif instruction[2] == 3:
                if line[0] == "jmp":
                    line_ = line[1]
                else:
                    line_ = line[2]
                if line_ in jump_labels:
                    binary_byte_code.append(line_)
                else:
                    print(f"Error: {line[1]} is not a valid jump label")
                    sys.exit(1)
            elif instruction[2] == 4:
                params = eval(line[2])
                binary_byte_code.append(params)
            elif instruction[2] == 5:
                if line[2] in INOUT:
                    params = INOUT[line[2]] << 4 | 0b0000
                    binary_byte_code.append(params)
                else:
                    print(f"Error: {line[2]} is not a valid INOUT")
                    sys.exit(1)
        elif line[0] == ":":
            # binary_byte_code.append(":" + line[1])
            jump_labels[line[1]] = len(binary_byte_code) - 1
        else:
            print(f"Error: {line[0]} is not a valid instruction")
            sys.exit(1)
    print(jump_labels)

    for i, line in enumerate(binary_byte_code):
        if isinstance(line, str):
            binary_byte_code[i] = jump_labels[line]
    return binary_byte_code


if __name__ == "__main__":
    code = load_code("code.asm")
    broken_code = break_up(code)
    print(broken_code)
    binary = convert_to_binary(broken_code)
    print(binary)
    for bit4 in binary:
        if isinstance(bit4, int):
            print(bin(bit4), end=" ")
        else:
            print(bit4, end=" ")
        print()
