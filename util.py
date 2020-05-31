
import re
from assembler_config import config_constant

def remove_commect(line):
    line = re.sub(r'#.*$', "", line)
    line = re.sub(r'//.*$', "", line)
    return line

def init_op_table(fp):
    OPTAB = {} # map opcode to dictionary
    # the mapping between opcode/operand and machine code
    # as well as addtional information
    # such as pseudo code
    # OPTAB = {
    #     "opcode" : {
    #         "format" :      "r",
    #         "op" :      "00000",
    #         "shamt" :         0,
    #         "funct" :         32,
    #         "address":     None,
    #         "pseudo": True/False,
    #         "op_size":         4,
    #     },
    #    ...
    # }

    # first read instructions
    lines = fp.readlines()
    reading_instruction = False
    reading_register = False
    for line in lines:
        line = line.strip()
        if(line[0] == "#"):
            continue
        if(line == "<instruction>"): # cannot use is here
                                    # or only address/id is being compared
            reading_instruction = True
            continue
        elif(line == "<register>"):
            reading_register = True
            continue
        elif(line == "<done>"):
            reading_register = False
            reading_instruction = False
        
        if(reading_instruction):
            comp = line.split(",")
            
            if(len(comp) is not 11):
                raise ValueError("OPTAB file format is not valid!")
            OPTAB[comp[0]] = {"format" :      comp[1],
                              "op" :          comp[2],
                              "rs":           comp[3],
                              "rt":           comp[4],
                              "rd":           comp[5],
                              "shamt" :       comp[6],
                              "funct" :       comp[7],
                              "address":      comp[8],
                              "pseudo":       comp[9],
                              "op_size":      comp[10]
                             }
        elif(reading_register):
            comp = line.split(",")
            if(len(comp) is not 2):
                raise ValueError("OPTAB file format is not valid!")
            OPTAB[comp[0]] = comp[1]
    #print(OPTAB)
    return OPTAB


def replace_pseudo():
    pass
def is_legal(TYPE, value, OPTAB=None, dict_op = None):
    res = True
    if(TYPE == "opcode"):
        if(OPTAB is None or OPTAB.find(value) is None):
            return False
    elif(TYPE == "operands"):
        pass
    elif(TYPE == "format"):
        pass
    else:
        raise ValueError("Invalid Type %s!"%TYPE)

def get_operands_index(reg):
    index_str = reg.replace("$r", "")
    return int(index_str)


def process_bit(text_segment):
    result_list = []
    for line_segment in text_segment:
        line_bit = line_segment["instruction"]
        line_bit = line_bit.replace(" ", "") # remove space
        int_bit = int(line_bit, 2)
        hex_bit = "{:0>8x}".format(int_bit)
        result_list.append(hex_bit)
    return result_list

def output_coe(header, hex_text):
    coe_name = header["name"] + ".coe"
    fp = open(coe_name, "w")
    header_text = [";{:s}.asm\n".format(header["name"]),
                   "memory_initialization_radix=16;\n",
                   "memory_initialization_vector=\n"]
    fp.writelines(header_text)
    newline_count = 0
    for i in range(len(hex_text)):
        line = hex_text[i]
        if(i != len(hex_text) - 1):
            fp.write(line+", ")
        else:
            fp.write(line+";")
        if(newline_count == 9):
            newline_count = 0;
            fp.write("\n")
        else:
            newline_count += 1
    

def base_convert(str):
    # process a string with a number in possible different bases
    # return a integer value of that number
    int_res = None
    if(config_constant == "numberprefix"):
        str = str.strip()
        binary_obj = re.match(r'^-?b[0-1]+$',str)
        hex_obj = re.match(r'-?0x[0-9A-Fa-f]+$', str)
        decimal_obj = re.match(r'-?[0-9]+',str)
        if(binary_obj != None):
            int_res = int(str,2)
        elif(hex_obj != None):
            int_res = int(str,16)
        elif(decimal_obj != None):
            int_res = int(str)
        else:
            raise ValueError("Invalid Syntax: " + str)

    else:
        str = str.strip()
        binary_obj = re.match(r'^b|B[0-1]+$',str)
        octal_obj = re.match(r'^o|O[0-7]+$',str)
        hex_obj = re.match(r'^h|H[0-9A-Fa-f]+$', str)
        decimal_obj = re.match(r'[0-9]+',str)
        if(binary_obj != None):
            int_res = int(str,2)
        elif(hex_obj != None):
            int_res = int(str,16)
        elif(octal_obj != None):
            int_res = int(str, 8)
        elif(decimal_obj != None):
            int_res = int(str)
        else:
            raise ValueError("Invalid Syntax: " + str)
    
    return int_res

