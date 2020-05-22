import sys, msvcrt

SP = 7 #Stack pointer

class CPU:

    def __init__(self):
        self.register = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.halted = False

        self.ir = None
        self.FL = None

        self.a = None
        self.b = None

        self.register[SP] = 0xF4

        self.branchtable = {
            0b10100000: self.add, #ADD
            0b10101000: self.and8, #AND
            0b01010000: self.call, #CALL
            0b10100111: self.cmp8, #CMP
            0b00000001: self.hlt, #HLT
            0b01010101: self.jeq, #JEQ
            0b01010110: self.jne, #JNE
            0b01010100: self.jmp, #JMP
            0b10000010: self.ldi, #LDI
            0b10100010: self.mul, #MUL
            0b01000110: self.pop, #POP
            0b01000111: self.prn, #PRN
            0b01000101: self.push, #PUSH
            0b00010001: self.ret, #RET
            0b10000100: self.st #ST
        }

    def add(self):
        self.ir = 'ADD'
        self.alu()
        self.pc += 3

    def and8(self):
        self.ir = 'AND'
        self.alu()

    def alu(self):
        """ALU operations."""
        op = self.ir
        a = self.a
        b = self.b
        if op == "ADD":
            self.register[a] += self.register[b]
        elif op == "MUL":
            self.register[a] *= self.register[b]
        elif op == 'CMP':
            # print('CMPing')
            if self.register[a] == self.register[b]: #compare the registers!
                self.FL = 0b00000001
                # print('equal')
            elif self.register[a] > self.register[b]:
                self.FL = 0b00000010
                # print('a > b')
            elif self.register[a] < self.register[b]:
                self.FL = 0b00000100
                # print('a < b')
        elif op == 'AND':
            self.register[a] = self.register[a] & self.register[b]
        elif op == 'OR':
            self.register[a] = self.register[a] | self.register[b]
        elif op == 'XOR':
            self.register[a] = self.register[a] ^ self.register[b]
        elif op == 'NOT':
            self.register[a] = ~self.register[a]
        elif op == 'SHL':
            self.register[a] = self.register[a] << self.register[b]
        elif op == 'SHR':
            self.register[a] = self.register[a] >> self.register[b]
        elif op == 'MOD':
            self.register[a] = self.register[a] % self.register[b]
        else:
            raise Exception("Unsupported ALU operation")

    def call(self):
        self.register[SP] -= 1
        self.ram_write(self.register[SP], self.pc + 2)
        self.pc = self.register[self.a]

    def cmp8(self):
        self.ir = 'CMP'
        self.alu()
        self.pc += 3
    
    def hlt(self):
        pass
        # Disabled to check keypress interrupt
        # print('\nHalting.')
        # self.halted = True
        # sys.exit(0)
    
    def jeq(self):
        if self.FL & 0b00000001 == 1:
            # print('jeq = 1')
            self.pc = self.register[self.a]
        else:
            self.pc += 2

    def jne(self):
        if self.FL & 0b00000001 == 0:
            # print('jne = 0')
            self.pc = self.register[self.a]
        else:
            self.pc += 2

    def jmp(self):
        # print('jump')
        self.pc = self.register[self.a]

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        print(f'\nLoading {filename}...\n')
        with open(filename + '.ls8') as prog_file:
            address = 0
            for line in prog_file:
                if line[0] == '#' or line[0] == '' or line[0] == '\n':
                    next
                else:
                    instruction = line[0:8]
                    self.ram[address] = int(instruction, 2)
                    address += 1

    def ldi(self):
        self.register[self.a] = self.b
        self.pc += 3

    def mul(self):
        self.ir = 'MUL'
        self.alu()
        self.pc += 3

    def pop(self):
        # print('popping')
        value = self.ram[self.register[SP]]
        self.register[self.a] = value
        self.register[SP] += 1
        self.pc += 2

    def prn(self):
        print('')
        print(self.register[self.a])
        self.pc +=2

    def push(self):
        # print('pushing')
        self.register[SP] -= 1
        value = self.register[self.a]
        self.ram[self.register[SP]] = value
        self.pc += 2

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def ret(self):
        self.pc = self.ram_read(self.register[SP])
        self.register[SP] += 1

    def run(self):
        print('Running...')
        while not self.halted:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('ASCII')
                print(f'\n{key}')
                if key == 'x':
                    print('Exiting...')
                    self.halted = True
            IR = self.ram[self.pc]
            opcount = IR >> 6
            self.ir = IR
            self.set_ab(opcount)
            self.branchtable[IR]()
        print('Halted.')
        sys.exit(1)

    def set_ab(self, opcount):
        # print('opcount:', opcount)
        if opcount == 1:
            self.a = self.ram_read(self.pc + 1)
        elif opcount == 2:
            self.a = self.ram_read(self.pc + 1)
            self.b = self.ram_read(self.pc + 2)

    def st(self):
        self.ram_write(self.register[self.b], self.register[self.a])
    
    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.FL,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()