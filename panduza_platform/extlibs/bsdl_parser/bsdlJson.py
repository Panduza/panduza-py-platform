#!/usr/bin/env python3
#
# Copyright (C) 2016  Forest Crossman <cyrozap@gmail.com>
# Copyright (C) 2022  Bryan CADET <http://github.com/BCadet>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import json
from pyftdi.bits import BitSequence

class BsdlJson:
    def __init__(self, bsdljson):
        self.json_data = bsdljson
        self.boundary_length = self._get_boundary_length()
        self.sample_opcode = self.get_opcode("SAMPLE")
        self.boundary_register = self._get_boundary_register()
        self.pin_map = self._get_pin_map()
        self.instruction_length = self._get_instruction_length()
        self.idcode = self._get_idcode()
        self.all_pins = self._get_all_pins()

    def _get_instruction_length(self):
        instruction_length_int = 0
        instruction_register_description = self.json_data.get("instruction_register_description")
        if instruction_register_description is not None:
            instruction_length = instruction_register_description.get("instruction_length")
            if instruction_length is not None:
                instruction_length_int = int(instruction_length)
        return instruction_length_int


    def _get_boundary_length(self):
        boundary_length_int = 0
        boundary_scan_register_description = self.json_data.get("boundary_scan_register_description")
        if boundary_scan_register_description is not None:
            fixed_boundary_stmts = boundary_scan_register_description.get("fixed_boundary_stmts")
            if fixed_boundary_stmts is not None:
                boundary_length = fixed_boundary_stmts.get("boundary_length")
                if boundary_length is not None:
                    boundary_length_int = int(boundary_length)
        return boundary_length_int

    def get_opcode(self, requested_name):
        opcode = None
        instruction_register_description = self.json_data.get("instruction_register_description")
        if instruction_register_description is not None:
            instruction_opcodes = instruction_register_description.get("instruction_opcodes")
            if instruction_opcodes is not None:
                for instruction_opcode in instruction_opcodes:
                    instruction_name = instruction_opcode.get("instruction_name")
                    if instruction_name.upper() == requested_name.upper():
                        opcode_raw = instruction_opcode.get("opcode_list", [None])[0]
                        if opcode_raw is not None:
                            opcode = int(opcode_raw, 2)
                            return BitSequence(opcode, length=len(opcode_raw))
        return opcode

    def _get_boundary_register(self):
        boundary_register = {}
        try:
            boundary_scan_register_description = self.json_data.get("boundary_scan_register_description")
            if boundary_scan_register_description is not None:
                fixed_boundary_stmts = boundary_scan_register_description.get("fixed_boundary_stmts")
                if fixed_boundary_stmts is not None:
                    boundary_register_list = fixed_boundary_stmts.get("boundary_register")
                    if boundary_register_list is not None:
                        for cell in boundary_register_list:
                            cell_number = cell.get("cell_number")
                            if cell_number is not None:
                                cell_info = cell.get("cell_info")
                                if cell_info is not None:
                                    boundary_register[cell_number] = cell_info
            return boundary_register
        except:
            return None

    def _get_pin_map(self):
        pin_map = {}
        pin_map_ast = self.json_data.get("device_package_pin_mappings")[0].get("pin_map")
        if pin_map_ast is not None:
            for entry in pin_map_ast:
                pin_map[entry["port_name"]] = entry["pin_list"]
        return pin_map


############################################################################################################

    def _get_idcode(self):
        optional_register_description = self.json_data.get("optional_register_description")
        if optional_register_description is not None:
            if len(optional_register_description) > 1 :
                idcode_register = optional_register_description[0]
            else :
                idcode_register = optional_register_description
 
            id = idcode_register['idcode_register']
            id_concatenated = ''.join(id[1:])
            idcode = hex(int(id_concatenated,2))

        return idcode
    
    def _get_all_pins(self):
        pins = []
        try:
            boundary_scan_register_description = self.json_data.get("boundary_scan_register_description")
            if boundary_scan_register_description is not None:
                fixed_boundary_stmts = boundary_scan_register_description.get("fixed_boundary_stmts")
                if fixed_boundary_stmts is not None:
                    boundary_register_list = fixed_boundary_stmts.get("boundary_register")
                    if boundary_register_list is not None:
                        for cell in boundary_register_list:
                            cell_number = cell.get("cell_number")
                            if cell_number is not None:
                                cell_info = cell.get("cell_info")
                                if cell_info is not None:
                                    cell_spec = cell_info.get("cell_spec")
                                    if cell_spec is not None:
                                        funct = cell_spec.get("function")
                                        if funct == "INPUT" or funct == "OUTPUT3":
                                            port_id = cell_spec.get("port_id")
                                            if port_id not in pins :
                                                pins.append(port_id)
            return pins
        except:
            return None
                                    
                                