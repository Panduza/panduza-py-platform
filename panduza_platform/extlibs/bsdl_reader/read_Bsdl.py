import re
import os
from pyftdi.bits import BitSequence

#############################################################################
#          Functions for reading multiple BSDL files from a folder          # 
#############################################################################

def get_bsdl_files(bsdl_folder):
    list_bsdl_files = os.listdir(bsdl_folder)
    bsdl_file_directory = []
    bsdl_file = []
    for i in range(len(list_bsdl_files)):
        bsdl_file_directory.append(os.path.join(bsdl_folder,list_bsdl_files[i]))
        f = open(bsdl_file_directory[i],"r") 
        bsdl_file.append(f.read())

    return bsdl_file


def get_idcodes_from_bsdl(bsdl_folder):

    list_bsdl_files = os.listdir(bsdl_folder)
    bsdl_files = get_bsdl_files(bsdl_folder)
    idcode_bsdl= []

    for i in range(len(list_bsdl_files)):
        bsdl = BsdlInfo(bsdl_files[i])
        idcode_bsdl.append(bsdl.idcode)
    
    return idcode_bsdl

def get_pins_from_bsdl(bsdl_folder):
    list_bsdl_files = os.listdir(bsdl_folder)
    bsdl_files = get_bsdl_files(bsdl_folder)  
    pins = []

    for i in range(len(list_bsdl_files)):
        bsdl = BsdlInfo(bsdl_files[i])
        pins.append(bsdl.all_pins)
    
    return pins





#############################################################################
#############################################################################
#                   Class for reading a BSDL file                           #
#############################################################################
#############################################################################
class BsdlInfo:
    def __init__(self, bsdl_file):
        self.bsdl_data = bsdl_file
        self.entity = self._get_entity()
        self.boundary_length = self._get_boundary_length()
        self.instruction_length = self._get_instruction_length()
        self.idcode = self._get_idcode()
        self.boundary_register = self._get_boundary_register()
        self.all_pins = self._get_all_pins()
        
    def _get_entity(self):
        entity_pattern = re.compile(r'entity\s+(\w+)\s+is')
        entity_name = entity_pattern.search(self.bsdl_data).group(1)

        return entity_name


    def _get_instruction_length(self):
        instruction_length_pattern = re.compile(r'attribute\s+INSTRUCTION_LENGTH\s+of\s+(\w+)\s*:\s*entity\s+is\s+(\d+)')
        instruction_length = instruction_length_pattern.search(self.bsdl_data).group(2)
            
        return int(instruction_length)
    
    def _get_boundary_length(self):
        boundary_length_pattern = re.compile(r'attribute\s+BOUNDARY_LENGTH\s+of\s+(\w+)\s*:\s*entity\s+is\s+(\d+)')
        boundary_length = boundary_length_pattern.search(self.bsdl_data).group(2)
            
        return int(boundary_length)

    def _get_opcode(self, request_name):
        opcode_pattern = re.compile(r'"(\w+)\s+\((\d+)\)\,*"')

        opcodes = {}
        for opcode_match in opcode_pattern.finditer(self.bsdl_data):
            opcode_name, opcode_value = opcode_match.group(1), opcode_match.group(2)
            opcodes[opcode_name] = BitSequence(opcode_value,msb=True,length = self.instruction_length)

        return opcodes.get(request_name)
    
    def _get_idcode(self):
        idcode_pattern = re.compile(r'"(\d+)"\s|("1";)')

        idcode_matches = idcode_pattern.finditer(self.bsdl_data)
        idcode_parts = [match[0] for match in idcode_matches if match[1] != '& "1";']
        idcode_parts_cleaned = [part.replace('"', '').replace(';', '').replace(' ', '') for part in idcode_parts]
        idcode = "".join(idcode_parts_cleaned)
        idcode_hex = hex(int(idcode,2))
        return idcode_hex
    
    def _get_boundary_register(self):
        boundary_pattern = re.compile(r'"\s*(\d+)\s*\((\w+),\s*(\w+|\*),\s*(\w+),\s*(\d+|X)\s*(\)\s*|,\s*(\d+),\s*(\d+),\s*(\w)+\s*\))')

        boundary_register_list = []
        for match in boundary_pattern.finditer(self.bsdl_data):
            cell_spec = {
            'cell_name': match.group(2),
            'port_id': match.group(3),
            'function': match.group(4),
            'safe_bit': match.group(5)
            }
            
            if match.group(6):
                input_or_disable_spec = {
                    'control_cell': match.group(7),
                    'disable_value': match.group(8),
                    'disable_result': match.group(9)
                }
            else :
                input_or_disable_spec = None
            
            boundary_register = {
            'cell_spec': cell_spec,
            'input_or_disable_spec': input_or_disable_spec
            }
            
            boundary_register_list.append(boundary_register)
            
        return boundary_register_list[::-1]
    
    def _get_all_pins(self):
        boundary_registers = self._get_boundary_register()
        all_pins = set()  

        for reg in boundary_registers:
            port_id = reg['cell_spec']['port_id']
            function = reg['cell_spec']['function']
            if function.upper() == "INPUT" or function.upper() == "OUTPUT3":
                all_pins.add(port_id)

        return list(all_pins)



if __name__ == "__main__":
    bsdl_file_path = "/home/rethusan/test_parser/BSDL/STM32F103RB.bsdl"  # xc7s50_csga324    STM32F103RB       STM32L476_486_LQFP144_P      CORTEXM3
    bsdl_folder = "/home/rethusan/test_parser/BSDL"

    with open(bsdl_file_path, 'r') as bsdl_file:
        bsdl_content = bsdl_file.read()
    
    data = BsdlInfo(bsdl_content)

    print("Idcode :", data.boundary_register)

    print(data._get_opcode("SAMPLE"))

    print('############')
    
    idcodes = get_idcodes_from_bsdl(bsdl_folder)
    print(idcodes)
    
    # pins = get_pins_from_bsdl(bsdl_folder)
    # print(pins)

    
