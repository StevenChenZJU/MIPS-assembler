from util import *
from assembler_config import *
def get_register_field(OPTAB, operands, dict_op, field):
    if(dict_op[field].find('$') != -1):
        index = get_operands_index(dict_op[field])
        if(index < len(operands)):
            r = " " + OPTAB[operands[index]]
        else:
            r = " 11111" # deal with instruction **`jalr`** with default value
    else:
        r = " " + dict_op[field];
    return r
def sign_extend(int_to_extend, length):
    length_int = int(length)
    res = None
    if(length_int == 16):
        if(int_to_extend >= 0):
            res = "{0:0>16b}".format(int_to_extend)
        else:
            #res = "{0:1>16b}".format(-int_to_extend)
            res = bin(int_to_extend & 0xffffffff)[-16:] # & 0xffffff to get the 2's complement
            # print(int_to_extend, res)
            # print(res[-16:])
    elif(length_int == 5):
        if(int_to_extend >= 0):
            res = "{0:0>5b}".format(int_to_extend)
        else:
            #res = "{0:1>5b}".format(-int_to_extend)
            res = bin(int_to_extend & 0xffffffff)[-5:]
    elif(length_int == 26):
        if(int_to_extend >= 0):
            res = "{0:0>26b}".format(int_to_extend)
        else:
            #res = "{0:1>26b}".format(-int_to_extend)
            res = bin(int_to_extend & 0xffffffff)[-26:]
    return res
def process_r(OPTAB, operands, dict_op):
    rs = None
    rt = None
    rd = None
    # rs
    rs = get_register_field(OPTAB,operands, dict_op, 'rs')
    # rt
    rt = get_register_field(OPTAB,operands, dict_op, 'rt')
    # rd
    rd = get_register_field(OPTAB,operands, dict_op, 'rd')
    # shamt
    if(dict_op['shamt'].find('$') != -1):
        shamt = " " + sign_extend(base_convert(operands[get_operands_index(dict_op['shamt'])]), 5)
    else:
        shamt = " " +dict_op["shamt"]
    # funct
    funct = " " +dict_op["funct"]
    return rs + rt + rd + shamt + funct

def process_j(OPTAB, operands, dict_op, SYMTAB, address, unresolved):
    # for regex
    bits = ""
    res_obj = re.match(r'^[0-9]+|0[0-9]+|0x[0-9a-f]+$', operands[0].strip())
    if(res_obj == None):
        # resolve label
        label = operands[0]
        if(SYMTAB.get(label) is not None):
            # for j format, theoretically, the address type should be "real"
            addr_int = SYMTAB[label] # should be the address instead of offset
            addr = None
            if(dict_op["address"] == "divided"):
                addr = sign_extend(addr_int // 4, 26)
            elif(dict_op["address"] == "real"):
                addr = sign_extend(addr_int, 26)
            else:
                raise ValueError("Address Type Error: "+dict_op["address"])
            bits += " " + addr
        else:
            unresolved.append({"label":label, "address":"Unresolved"})
            print(label + " Unresolved!")
            bits += " Unresolved"
    else:
        # number_str = operands[0].zfill(26)
        addr_int = base_convert(operands[0])
        addr = "{0:0>26b}".format(addr_int)
        
        bits += " " + addr

    return bits
def process_i(OPTAB, operands, dict_op, SYMTAB, address, unresolved):
    bits = ""
    rs = get_register_field(OPTAB, operands, dict_op, 'rs')
    rt = get_register_field(OPTAB, operands, dict_op, 'rt')
    imm_field = operands[len(operands)-1].strip()
    
    res_obj = re.match(r'^-?[0-9]+|0[0-9]+|0x[0-9a-f]+$', imm_field)
    if(dict_op["address"] == "imm"):
        imm = None
        if(res_obj is None):
            raise ValueError("Unexpected immediate number!")
        else:
            imm = sign_extend(base_convert(imm_field), 16)
        bits += rs + rt + imm
    else:       
        if(res_obj is None):
            label = imm_field
            if(SYMTAB.get(label) is not None):
                # should minus the address of the next instrction
                addr_offset_int = SYMTAB[label] - (address + 4) 
                
                if(dict_op["address"] == "divided"):
                    addr_offset = sign_extend(addr_offset_int // 4, 16)
                elif(dict_op["address"] == "real"):
                    addr_offset = sign_extend(addr_offset_int, 16)
                else:
                    raise ValueError("Address Type Error: "+dict_op["address"])
            else:
                unresolved.append({"label":label, "address":"Unresolved"})
                print(label + " Unresolved!")
                addr_offset = "Unresolved"
        else:
            # number_str = operands[0].zfill(26)
            addr_offset_int = base_convert(imm_field) - (address + 4)
            
            addr_offset = sign_extend(addr_offset_int, 16)
        
        addr_offset = " " + addr_offset
        bits += rs + rt + addr_offset
    
    return bits
    
def process_op(dict_op, operands, OPTAB, SYMTAB, address):
    bits = ""
    unresolved = []
    reloc = {}

    bits += dict_op["op"]
    op_format = dict_op["format"]
    if(config_type == "Debug"):
        print(operands)
    if(op_format == 'r'):
        bits += process_r(OPTAB, operands, dict_op)
    elif(op_format == 'j'):
        bits += process_j(OPTAB, operands, dict_op, SYMTAB, address, unresolved)
    elif(op_format == 'i'):
        bits += process_i(OPTAB, operands, dict_op, SYMTAB, address, unresolved)

    
    return bits, unresolved, reloc
