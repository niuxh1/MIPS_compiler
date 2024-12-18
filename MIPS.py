class MIPS:
    def __init__(self):
        self.registers = {
            '$0': 0, '$1': 1, '$2': 2, '$3': 3, '$4': 4, '$5': 5, '$6': 6, '$7': 7,
            '$8': 8, '$9': 9, '$10': 10, '$11': 11, '$12': 12, '$13': 13, '$14': 14, '$15': 15,
            '$16': 16, '$17': 17, '$18': 18, '$19': 19, '$20': 20, '$21': 21, '$22': 22, '$23': 23,
            '$24': 24, '$25': 25, '$26': 26, '$27': 27, '$28': 28, '$29': 29, '$30': 30, '$31': 31
        }

        self.opcodes = {
            'add': '000000',
            'sub': '000000',
            'and': '000000',
            'or': '000000',
            'xor': '000000',
            'sll': '000000',
            'slt': '000000',
            'srl': '000000',
            'subu': '000000',
            'addiu': '001001',
            'lw': '100011',
            'sw': '101011',
            'addi': '001000',
            'slti': '001010',
            'beq': '000100',
            'bne': '000101',
            'blez': '000110',
            'andi': '001100',
            'ori': '001101',
            'xori': '001110',
            'j': '000010',
            'jal': '000011',
            'jr': '000000'
        }

        self.funct = {
            'add': '100000',
            'sub': '100010',
            'and': '100100',
            'slt': '101010',
            'or': '100101',
            'xor': '100110',
            'sll': '000000',
            'srl': '000010',
            'jr': '001000'
        }

    def to_bin(self, num, bits):
        if num < 0:
            num = (1 << bits) + num
        return format(num, f'0{bits}b')

    def parse_R(self, instruction):
        if not (instruction.split(',')[0] == 'jr' or instruction.split(',')[0] == 'sll' or instruction.split(',')[0] == 'srl'):

            parts = instruction.split(',')
            opcode = self.opcodes[parts[0]]
            rs = self.registers[parts[1]]
            rt = self.registers[parts[2]]
            rd = self.registers[parts[3]]
            shamt = '00000'
            funct = self.funct[parts[0]]

            return opcode + self.to_bin(rs, 5) + self.to_bin(rt, 5) + self.to_bin(rd, 5) + shamt + funct
        elif instruction.split(',')[0] == 'jr':
            parts = instruction.split(',')
            opcode = self.opcodes[parts[0]]
            rs = self.registers[parts[1]]
            rt = '00000'
            rd = '00000'
            shamt = '00000'
            funct = self.funct[parts[0]]

            return opcode + self.to_bin(rs, 5) + rt + rd + shamt + funct
        elif instruction.split(',')[0] == 'sll' or instruction.split(',')[0] == 'srl':
            parts = instruction.split(',')
            opcode = self.opcodes[parts[0]]
            rs = '00000'
            rt = self.registers[parts[1]]
            rd = self.registers[parts[2]]
            shamt = self.to_bin(int(parts[3]), 5)
            funct = self.funct[parts[0]]

            return opcode + rs + self.to_bin(rt, 5) + self.to_bin(rd, 5) + shamt + funct

    def parse_I(self, instruction):
        parts = instruction.split(',')
        if parts[0] in ['lw', 'sw']:
            opcode = self.opcodes[parts[0]]
            rt = self.registers[parts[1]]
            imm = int(parts[2].split('(')[0])
            rs = self.registers[parts[2].split('(')[1].split(')')[0]]
            return opcode + self.to_bin(rs, 5) + self.to_bin(rt, 5) + self.to_bin(imm, 16)
        elif parts[0] not in ['blez']:
            opcode = self.opcodes[parts[0]]
            rs = self.registers[parts[1]]
            rt = self.registers[parts[2]]
            imm = int(parts[3])
            return opcode + self.to_bin(rs, 5) + self.to_bin(rt, 5) + self.to_bin(imm, 16)
        elif parts[0] in ['blez']:
            opcode = self.opcodes[parts[0]]
            rs = self.registers[parts[1]]
            rt = '00000'
            imm = int(parts[2])
            return opcode + self.to_bin(rs, 5) +rt + self.to_bin(imm, 16)

    def parse_J(self, instruction):
        parts = instruction.split(',')
        opcode = self.opcodes[parts[0]]

        addr = int(parts[1], 16)

        return opcode + self.to_bin(addr, 26)

    def parse(self, instruction):
        part = instruction.split(',')
        if part[0] in ['add',
                       'sub',
                       'slt',
                       'and',
                       'or',
                       'xor',
                       'sll',
                       'srl',
                       'subu',
                       'jr']:
            return self.parse_R(instruction)
        elif part[0] in ['addiu',
                         'lw',
                         'sw',
                         'addi',
                         'slti',
                         'beq',
                         'bne',
                         'andi',
                         'blez',
                         'ori',
                         'xori']:
            return self.parse_I(instruction)
        elif part[0] in ['j', 'jal']:
            return self.parse_J(instruction)

    def assemble(self, program):
        lines = program.split('\n')
        binary = []
        for line in lines:
            line = line.strip()
            if not line or line[0] == '#':
                continue
            if line == 'halt':
                binary.append('11111100000000000000000000000000')
                break
            binary.append(self.parse(line))

        return binary


program = """
add,$1,$2,$3
addiu,$1,$0,8
ori,$2,$0,2
xori,$3,$2,8
sub,$4,$3,$1
and,$5,$4,$2
sll,$5,$5,2
beq,$5,$1,-2
jal,0x0000050
slt,$8,$13,$1
addiu,$14,$0,-2
slt,$9,$8,$14
slti,$10,$9,2
slti,$11,$10,0
add,$11,$11,$10
bne,$11,$2,-2
addiu,$12,$0,-2
addiu,$12,$12,1
blez,$12,-2
andi,$12,$2,2
j,0x000050
sw,$2,4($1)
lw,$13,4($1)
jr,$31
halt
"""

translator = MIPS()
binary_code = translator.assemble(program)
program = program.strip()
program = program.split('\n')
file_path = "test_instructions.txt"
with open(file_path, "w") as file:
    for line in binary_code:
        file.write(line + "\n")
