import random


class Rom:
    def __init__(self):
        self.write_rom = [0b0000 for _ in range(256)]
        self.rom = tuple(self.write_rom)
        self.writable = True

    def set(self, position: int, value: int) -> None:
        """
        Set the value of the ROM at the given position
        :param position: 8-bit position
        :param value: 8-bit value
        """
        if self.writable:
            self.write_rom[position] = value
        else:
            raise TypeError("ROM is not writable, any more")

    def finish_rom_init(self) -> None:
        """
        Finish the initialization of the ROM, making it read-only
        """
        self.rom = tuple(self.write_rom)
        self.writable = False
        del self.write_rom
        del self.set

    def get(self, position: int) -> int:
        """
        Get the value of the ROM at the given position
        :param position: 8-bit position
        :return: 8-bit value
        """
        return self.rom[position]


class Registers:
    def __init__(self):
        self.registers = [0b0000 for _ in range(16)]

    def set(self, register: int, value: int) -> None:
        """
        Set the value of the register at the given position
        :param register: 4-bit register
        :param value: 8-bit value
        """
        self.registers[register] = value

    def get(self, register: int) -> int:
        """
        Get the value of the register at the given position
        :param register: 4-bit register
        :return: 8-bit value
        """
        return self.registers[register]


class InOut:
    def __init__(self):
        self.inout = [0b0000 for _ in range(16)]

    def set(self, inout: int, value: int) -> None:
        """
        Set the value of the inout at the given position
        :param inout: 4-bit inout
        :param value: 8-bit value
        """
        self.inout[inout] = value

    def get(self, inout: int) -> int:
        """
        Get the value of the inout at the given position
        :param inout: 4-bit inout
        :return: 8-bit value
        """
        return self.inout[inout]

    def set_external(self, in_address: int, value: int) -> None:
        """
        Set the value of the input at the given position
        :param in_address: 4-bit in_address
        :param value: 8-bit value
        """
        if in_address < 0b1000:
            self.inout[in_address] = value
        else:
            raise ValueError("Invalid input address")

    def get_external(self, out_address: int) -> int:
        """
        Get the value of the output at the given position
        :param out_address: 4-bit out_address
        :return: 8-bit value
        """
        if out_address > 0b0111:
            return self.inout[out_address]
        else:
            raise ValueError("Invalid output address")


class ALU:
    def __init__(self, registers: Registers):
        self.registers = registers

    def add(self, dest: int, reg1: int, reg2: int) -> None:
        data1 = self.registers.get(reg1)
        data2 = self.registers.get(reg2)
        result = data1 + data2
        if result & 0b1_0000_0000:
            flags = self.registers.get(0xFF)
            flags |= 0b0100_0000
            self.registers.set(0xFF, flags)
        result &= 0b0_1111_1111
        self.registers.set(dest, result)

    def sub(self, dest: int, reg1: int, reg2: int) -> None:
        data1 = self.registers.get(reg1)
        data2 = self.registers.get(reg2)
        result = data1 - data2
        if result < 0:
            flags = self.registers.get(0xFF)
            flags |= 0b0010_0000
            self.registers.set(0xFF, flags)
        if result == 0:
            flags = self.registers.get(0xFF)
            flags |= 0b1000_0000
            self.registers.set(0xFF, flags)
        result &= 0b0_1111_1111
        self.registers.set(dest, result)

    def and_(self, dest: int, reg1: int, reg2: int) -> None:
        data1 = self.registers.get(reg1)
        data2 = self.registers.get(reg2)
        result = data1 & data2
        if result == 0:
            flags = self.registers.get(0xFF)
            flags |= 0b1000_0000
            self.registers.set(0xFF, flags)
        self.registers.set(dest, result)

    def or_(self, dest: int, reg1: int, reg2: int) -> None:
        data1 = self.registers.get(reg1)
        data2 = self.registers.get(reg2)
        result = data1 | data2
        if result == 0:
            flags = self.registers.get(0xFF)
            flags |= 0b1000_0000
            self.registers.set(0xFF, flags)
        self.registers.set(dest, result)

    def nor(self, dest: int, reg1: int, reg2: int) -> None:
        data1 = self.registers.get(reg1)
        data2 = self.registers.get(reg2)
        result = ~(data1 | data2)
        if result == 0:
            flags = self.registers.get(0xFF)
            flags |= 0b1000_0000
            self.registers.set(0xFF, flags)
        self.registers.set(dest, result)

    def xor(self, dest: int, reg1: int, reg2: int) -> None:
        data1 = self.registers.get(reg1)
        data2 = self.registers.get(reg2)
        result = data1 ^ data2
        if result == 0:
            flags = self.registers.get(0xFF)
            flags |= 0b1000_0000
            self.registers.set(0xFF, flags)
        self.registers.set(dest, result)

    def inc(self, dest: int):
        data = self.registers.get(dest)
        result = data + 1
        if result & 0b1_0000_0000:
            flags = self.registers.get(0xFF)
            flags |= 0b0100_0000
            self.registers.set(0xFF, flags)
        result &= 0b0_1111_1111
        self.registers.set(dest, result)

    def rolr(self, dest: int):
        data = self.registers.get(dest)
        carry = data & 0b0000_0001  # Check if LSB is set
        result = (data >> 1) | (data << 7) & 0b1111_1111  # Perform rotate right
        self.registers.set(dest, result)

        # Update carry flag
        flags = self.registers.get(0xFF)
        if carry:
            flags |= 0b0100_0000  # Set carry flag
        else:
            flags &= 0b1011_1111  # Clear carry flag
        self.registers.set(0xFF, flags)

    def rnv(self, dest: int):
        result = random.randint(0, 255)
        self.registers.set(dest, result)


class CPU:
    @staticmethod
    def split_instruction(instruction: int) -> tuple[int, int]:
        """
        Split the instruction into the upper 4 bits and the lower 4 bits
        :param instruction: 8-bit instruction
        :return: tuple of the upper 4 bits and the lower 4 bits
        """
        return (instruction & 0b1111_0000) >> 4, instruction & 0b0000_1111

    def __init__(self, rom: Rom, registers: Registers, inout: InOut):
        self.rom = rom
        self.registers = registers
        self.inout = inout
        self.alu = ALU(registers)
        self.pc = 0  # Program Counter

    def fetch(self) -> int:
        instruction = self.rom.get(self.pc)
        self.pc += 1
        return instruction

    def decode_execute(self, instruction: int) -> None:
        upper_4_bits, lower_4_bits = self.split_instruction(instruction)

        match upper_4_bits:
            case 0b0000:  # NOP
                pass
            case 0b0001:  # ADD
                upper_arg, lower_arg = self.split_instruction(self.fetch())
                self.alu.add(lower_4_bits, upper_arg, lower_arg)
            case 0b0010:  # SUB
                upper_arg, lower_arg = self.split_instruction(self.fetch())
                self.alu.sub(lower_4_bits, upper_arg, lower_arg)
            case 0b0011:  # AND
                upper_arg, lower_arg = self.split_instruction(self.fetch())
                self.alu.and_(lower_4_bits, upper_arg, lower_arg)
            case 0b0100:  # OR
                upper_arg, lower_arg = self.split_instruction(self.fetch())
                self.alu.or_(lower_4_bits, upper_arg, lower_arg)
            case 0b0101:  # NOR
                upper_arg, lower_arg = self.split_instruction(self.fetch())
                self.alu.nor(lower_4_bits, upper_arg, lower_arg)
            case 0b0110:  # XOR
                upper_arg, lower_arg = self.split_instruction(self.fetch())
                self.alu.xor(lower_4_bits, upper_arg, lower_arg)
            case 0b0111:  # INC
                self.alu.inc(lower_4_bits)
            case 0b1000:  # ROLR
                self.alu.rolr(lower_4_bits)
            case 0b1001:  # BIB
                upper_arg, lower_arg = self.split_instruction(self.fetch())
                if lower_4_bits & 0b1000:
                    data = self.registers.get(0b1111)
                else:
                    data = self.registers.get(0b0000)
                index = lower_4_bits & 0b0111
                mask = 1 << index
                bit_value = (data & mask) >> index
                if bit_value:
                    self.pc = (upper_arg << 4) | lower_arg
            case 0b1010:  # JMP
                upper_arg, lower_arg = self.split_instruction(self.fetch())
                self.pc = ((upper_arg << 4) | lower_arg) - 1
            case 0b1011:  # MOV
                upper_arg, _ = self.split_instruction(self.fetch())
                self.registers.set(lower_4_bits, self.registers.get(upper_arg))
            case 0b1100:  # LDI
                upper_arg, lower_arg = self.split_instruction(self.fetch())
                self.registers.set(lower_4_bits, (upper_arg << 4) | lower_arg)
            case 0b1101:  # IN
                upper_arg, _ = self.split_instruction(self.fetch())
                data = self.inout.get(upper_arg)
                self.registers.set(lower_4_bits, data)
            case 0b1110:  # OUT
                upper_arg, _ = self.split_instruction(self.fetch())
                data = self.registers.get(lower_4_bits)
                self.inout.set(upper_arg, data)
            case 0b1111:  # RNV
                self.alu.rnv(lower_4_bits)
            case _:
                raise ValueError(f"Unknown opcode: {hex(upper_4_bits)}")

    def step(self) -> None:
        instruction = self.fetch()
        self.decode_execute(instruction)


if __name__ == "__main__":
    rom = Rom()
    # rom.set(0, 0b1100_0001)
    # rom.set(1, 0b0001_0000)
    # rom.set(2, 0b1100_0010)
    # rom.set(3, 0b0001_1000)
    # rom.set(4, 0b0001_0000)
    # rom.set(5, 0b0001_0010)
    # rom.set(6, 0b1110_0000)
    # rom.set(7, 0b1000_0000)
    for i, value in enumerate([193, 16, 194, 24, 17, 18, 225, 128, 0, 160, 7]):
        rom.set(i, value)
    rom.finish_rom_init()

    registers = Registers()
    inout = InOut()

    cpu = CPU(rom, registers, inout)

    for _ in range(10):
        cpu.step()

    print(bin(inout.get_external(0b1000)))
