import datetime
import math
import pytz
import sys
import os

#
# Zepto Linker
#
# @author  Rafael Campos Nunes
# @date    29/04/2021
# @version 0.7
#
# Reads a .z file and outputs a .dsr file that is compatible with Deeds ROM
# software module. The zepto processor reads from a ROM that has a capacity of
# 128 bytes only (4096 instructions of 32 bits each)
#

# These opcodes are written in hexadecimal
opcodes = {
    "addi": '0000',
    "subi": '0001',
    "andi": '0002',
    "ori":  '0003',
    "xori": '0004',
    "beq":  '0005',
    "bleu": '0006',
    "bles": '0007',
}

_registers_name = ['R' + str(number) for number in range(15)]
_registers_addr = [bin(number)[2:].zfill(4) for number in range(15)]

registers = dict(zip(_registers_name, _registers_addr))


def main():
    # The file used to read instructions from the Zepto assembly language.
    input_name = sys.argv[1]

    # contains the instructions of the program that will be transformed
    output_name = input_name.split(".")[0] + ".dsr"
    output_content = ""

    zepto_instructions = []
    zepto_rom_size = 4*1024*16  # 4KB*16
    zepto_instructions_size = 0

    with open(input_name, 'r') as fd:
        for line in fd:
            # filtering parseable lines
            if not (line.startswith('#') or line.startswith('\n')):
                zepto_instructions.append(zepto_parse(line))

    # First construct the header
    zepto_instructions_size = len(zepto_instructions)*2
    output_content += zepto_header(zepto_instructions_size)

    j = 1
    for i in range(0, len(zepto_instructions)):
        output_content += zepto_instructions[i] + " "

        if j % 2 == 0:
            output_content += "\n"
            j = 0
        j += 1

    print(output_content)

    # create read/write only and trunc the file if it already exists.
    with open(output_name, 'w+') as fd:
        fd.write(output_content)


def zepto_parse(line):
    '''
    Parses a line of instructions into the .DSR format
    '''

    parsed = ""
    data = line.strip('\n').split(' ')

    opcode_mnemonic = data[0]
    operands_mnemonic = data[1].split(",")

    # Parsing goes from
    opcode = opcodes[opcode_mnemonic]
    parsed += opcode

    for operand in operands_mnemonic:
        try:
            parsed += " " + registers[operand]
        except KeyError:
            if operand.isnumeric():
                parsed += " " + f'{int(operand):X}'.zfill(4)

    padd = ' '*(25-pad(operands_mnemonic))
    formatted = 'opcode {:4} -> operands {}{} -> {} {}'.format(opcode_mnemonic,
                                                                operands_mnemonic,
                                                                padd,
                                                                opcode,
                                                                parsed)
    print(formatted)

    return parsed


def zepto_header(size):
    tz = pytz.timezone('Brazil/East')
    date = datetime.datetime.now(tz)

    now = date.strftime("%D %H:%M:%S")

    data = '''
# Zepto Linker
#
# Program created at ''' + now + '''
# Program has ''' + str(size) + ''' bytes (program without ROM padding)
#
#\n
'''

    return data


def pad(list):
    '''
    Return a number representing the amount of padding necessary to format
    '''

    # [] + ''*len(list)
    n = 2 + 2*len(list)

    if len(list) > 0:
        # spaces + commas
        n += 2*(len(list)-1)

    for e in list:
        if e.isnumeric():
            if e == 0:
                size = 1
            else:
                size = len(e)
        else:
            # assume it is a string list
            size = len(e)

        n += size

    return n


if __name__ == "__main__":
    main()
