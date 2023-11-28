from panduza_platform.extlibs.bsdl_parser import bsdl,bsdlJson
import os


class BsdlSemantics:
    def map_string(self, ast):
        parser = bsdl.bsdlParser()
        ast = parser.parse(''.join(ast), "port_map")
        return ast

    def grouped_port_identification(self, ast):
        parser = bsdl.bsdlParser()
        ast = parser.parse(''.join(ast), "group_table")
        return ast
    

def get_bsdl_file(bsdl_folder):
    list_bsdl_files = os.listdir(bsdl_folder)
    bsdl_file_directory = []
    bsdl_file = []
    for i in range(len(list_bsdl_files)):
        bsdl_file_directory.append(os.path.join(bsdl_folder,list_bsdl_files[i]))
        f = open(bsdl_file_directory[i],"r") 
        bsdl_file.append(f.read())

    return bsdl_file


def get_idcode_from_bsdl(bsdl_folder):
    parser = bsdl.bsdlParser()
    list_bsdl_files = os.listdir(bsdl_folder)
    bsdl_file = get_bsdl_file(bsdl_folder)
    
    idcode_bsdl= []

    for i in range(len(list_bsdl_files)):
        json = parser.parse(bsdl_file[i], "bsdl_description", semantics=BsdlSemantics(), parseinfo=False).asjson()
        json_bsdl = bsdlJson.BsdlJson(json)

        idcode_bsdl.append(json_bsdl.idcode)
    
    return idcode_bsdl


def get_pins_from_bsdl(bsdl_folder):
    parser = bsdl.bsdlParser()
    list_bsdl_files = os.listdir(bsdl_folder)
    bsdl_file = get_bsdl_file(bsdl_folder)
    
    pins = []

    for i in range(len(list_bsdl_files)):
        json = parser.parse(bsdl_file[i], "bsdl_description", semantics=BsdlSemantics(), parseinfo=False).asjson()
        json_bsdl = bsdlJson.BsdlJson(json)

        pins.append(json_bsdl.all_pins)
    
    return pins
