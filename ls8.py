import sys, os
from cpu import *

cpu = CPU()

if __name__ == '__main__':
    try:
        cpu.load(sys.argv[1])
        cpu.run()
    except KeyboardInterrupt:
        cpu.halted = True
        print('Interrupted')