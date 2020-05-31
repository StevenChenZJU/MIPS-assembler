import sys
import re
from util import *
from assembler_config import * 
from op_processor import *

def first_pass(lines, OPTAB):
    

    inter_code = [] # list of 
    SYMTAB = {} # dict of 
    data_segment = []
    text_size = 0
    data_size = 0 
    LOCCTR = 0
    #to do: 
    #is_start = False # determine whether it is started
    #is_text = None # is_text is true if we are processing text;
                   # false for data
    for line in lines:
        line = remove_commect(line)
        
        line = line.strip().lower() # remove \n \t and space
        
        if(line == ''):
            continue

        #check whether there is a label
        index = line.find(':')
        # return -1 if not found
        if(index is not -1):
            label = line[:index]
            if(SYMTAB.get(label) != None):
                raise ValueError("Duplicated Symbol %s!"%label)
            line = line[index+1:].lstrip()
            SYMTAB[label] = LOCCTR
        
        if(line == ''):
            continue

        # have instruction in this line
        line = line.replace('\t', " ")
        components = line.split(" ", 1)
        opcode = components[0]
        operands = components[1].lstrip()
        dict_op = OPTAB.get(opcode)
        if(dict_op is None):
            print(line)
            print(components)
            raise ValueError("Invalid opcode %s!"%opcode)
        else:
            
            list_operands = operands.split(",")

            if(dict_op["format"] == 'i' and list_operands[1].find('(') != -1):
                # num($reg)
                to_process = list_operands[1].strip()
                index = to_process.find('(')
                rindex = to_process.find(')')
                list_operands.pop()
                list_operands.append(to_process[index+1:rindex].strip()) 
                 # put the register in first
                list_operands.append(to_process[:index])
                #print(list_operands)
                
            #if(not is_legal("operands",list_operands)):
             #   raise ValueError("Invalid operands!" + str(list_operands))
            for i in range(len(list_operands)):
                 list_operands[i] = list_operands[i].strip()
            inter_code.append({ "address":LOCCTR,
                                "opcode":opcode,
                                "operands":list_operands,
                                "dict_op":dict_op})
            # in case it is pseudo code
            # add correct length
            size_code = int(dict_op["op_size"])
            LOCCTR += size_code
            text_size += size_code
            

    if(config_type == "DEBUG"):
        print(SYMTAB)
    return  inter_code, SYMTAB, text_size, data_size, data_segment


def second_pass(inter_code, SYMTAB, OPTAB):
    text_segment = [] # list of dictionary
    relocation_information = []
    symbol_table = []

    for dict_line in inter_code:
        address = dict_line["address"]
        opcode = dict_line["opcode"]
        operands = dict_line["operands"]
        dict_op = dict_line["dict_op"]

        #if(not is_legal("format", operands, dict_op = dict_op)):
         #   raise ValueError("Format Error!")
        #else:

        if(dict_op["pseudo"] is True):
            # to do : to support pseudo code
            pass
        else:
            # the format is checked
            bits, unresolved, reloc = process_op(dict_op, operands, OPTAB, SYMTAB, address)
            if(len(unresolved) is not 0):
                symbol_table.append(unresolved)
            if(reloc is not None):
                relocation_information.append(reloc)
            text_segment.append({"address":address, "instruction":bits})


    return  text_segment, relocation_information, symbol_table 

if __name__ == "__main__":
    args = sys.argv
    arm_name = None
    if(len(args) == 2):
        arm_name = args[1]
    elif(len(args) < 2):
        raise ValueError("Too few arguments! Need to specify the asm file!")
    else:
        raise ValueError("Too many arguments!")

    SYMTAB = None
    OPTAB = None 
    text_size = None
    data_size = None
    inter_code = None
    
    header = {"name": arm_name.replace(".asm", ""),
              "text_size": None,
              "data_size": None}

    OPTAB_file = "OPTAB.txt"
    with open(OPTAB_file, "r") as opfp:
        OPTAB = init_op_table(opfp)
    
    
    with open(arm_name,'r') as fp:
        lines = fp.readlines()
        inter_code, SYMTAB, text_size, data_size,data_segment=  first_pass(lines, OPTAB)
    
    if(config_type == "Debug"):
        print(SYMTAB)
    header["text_size"] = text_size
    header["data_size"] = data_size

    # return dictionary of lists
    text_segment = None
    data_segment = None
    relocation_infomation = None
    symbol_table = None

    text_segment, relocation_information, symbol_table = second_pass(inter_code, SYMTAB, OPTAB)

    if(config_type == "Debug"):
        print(header)
        print(text_segment)
        print(relocation_infomation)
        print(symbol_table)
    elif(config_type == "Release"):
        hex_text = process_bit(text_segment)
        output_coe(header, hex_text)
    else:
        raise ValueError("Invalid Configuration!")

    if(config_type == "Release"):
        print("Successfully Compile into " + header["name"] + ".coe")
