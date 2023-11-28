import asyncio
import concurrent.futures

from .boundary_scan_base import ConnectorBoundaryScanBase
from extlibs.bsdl_reader import read_Bsdl
from log.driver import driver_logger

from pyftdi.ftdi import Ftdi
from pyftdi.jtag import JtagEngine
from pyftdi.bits import BitSequence



###########################################################################
###########################################################################


def get_bit_settings(bit_state_dict, boundary_reg):
    byte_array = list(boundary_reg)

    for bit in bit_state_dict.keys():

        if bit_state_dict[bit] == 1:
            byte_array[bit] = 1
        else:
            byte_array[bit] = 0
    return BitSequence(byte_array)



###########################################################################
###########################################################################

class ConnectorBoundaryScanFtdi(ConnectorBoundaryScanBase):
    """The serial modbus client connector centralize access to a given port as a modbus client
    """

    # Hold instances mutex
    __MUTEX = asyncio.Lock()

    # Contains instances
    __INSTANCES = {}

    ###########################################################################

    # Local logs
    log = driver_logger("ConnectorBoundaryScanFtdi")

    @staticmethod
    async def Get(**kwargs):

        """Singleton main getter
        
        :Keyword Arguments:

        * *usb_vendor* (``str``) --
            ID_VENDOR_ID
        * *usb_model* (``str``) --
            ID_MODEL_ID
        * *usb_serial_short* (``str``) --
            ID_SERIAL_SHORT
        * *jtag_frequency* (``str``) --
            jtag_frequency
        * *jtag_bsdl_folder* (``str``) --
            jtag_bsdl_folder
        """

        # Log
        ConnectorBoundaryScanFtdi.log.debug(f"Get connector for {kwargs}")

        async with ConnectorBoundaryScanFtdi.__MUTEX:
             # Log
            ConnectorBoundaryScanFtdi.log.debug(f"Lock acquired !")
        
            # Check if an FTDI is detected
            if (len(Ftdi.list_devices())) < 1 :
                raise Exception("can't detect the FTDI")
            
            
            if "usb_vendor" in kwargs:
                usb_vendor = kwargs["usb_vendor"]

            if "usb_model" in kwargs:
                usb_model = kwargs["usb_model"]

            if "usb_serial_short" in kwargs:
                usb_serial_short = kwargs["usb_serial_short"]

            if "jtag_frequency" in kwargs:
                jtag_frequency = kwargs["jtag_frequency"]

            if "jtag_bsdl_folder" in kwargs:
                jtag_bsdl_folder = kwargs["jtag_bsdl_folder"]  

            else:
                raise Exception("no way to identify the informations given in the tree.json")
            
            instance_name = str(f"{usb_vendor}_{usb_model}_{usb_serial_short}")
            

            # Check if instance already exists
            if instance_name in ConnectorBoundaryScanFtdi.__INSTANCES:
                return ConnectorBoundaryScanFtdi.__INSTANCES[instance_name]
            
            # Create an instance
            try:
                new_instance = ConnectorBoundaryScanFtdi(key=instance_name,               
                                            usb_vendor=usb_vendor,
                                            usb_model=usb_model,
                                            usb_serial_short=usb_serial_short,
                                            jtag_frequency=jtag_frequency,
                                            jtag_bsdl_folder=jtag_bsdl_folder
                                            )
                ConnectorBoundaryScanFtdi.__INSTANCES[instance_name] = new_instance

            except Exception as e:
                raise Exception('Error during initialization').with_traceback(
                    e.__traceback__)

            # Return the newly created instance
            ConnectorBoundaryScanFtdi.log.info(f"Creation of instance {instance_name}")
            return ConnectorBoundaryScanFtdi.__INSTANCES[instance_name]
    

    
    def __init__(self,**kwargs):
        """Constructor
        """

        # Init local mutex
        self._mutex = asyncio.Lock()    
               
        # Get parameters
        usb_vendor = kwargs.get('usb_vendor', "0403")
        usb_model = kwargs.get('usb_model', "6014")
        jtag_frequency = kwargs.get('jtag_frequency', 6E6)
        jtag_bsdl_folder = kwargs.get('jtag_bsdl_folder', "/etc/BSDL") #################
           
        # Init engine
        self.engine = JtagEngine(frequency=float(jtag_frequency))
        self.engine.configure(f'ftdi://0x{usb_vendor}:0x{usb_model}/1')
        self.engine.reset()

        # Get idcodes
        idcode_bsdl = read_Bsdl.get_idcodes_from_bsdl(jtag_bsdl_folder)
             
        idcode_detected = self.idcode()    # retrieve the idcodes in order and store them in a dictionnary (key = device_number ; value = idcode)

        # Get number of devices
        self.total_devices = self.scan()

        # Get bsdl files
        bsdl_file = read_Bsdl.get_bsdl_files(jtag_bsdl_folder)

        # list for idcode without version number
        idcode_modified = []

        # Dictionnary for BSDL files 
        self.bsdl_dict = {}
        
        # Remove the first 4 bits of the idcodes (= idcode without 4-bit version number)
        for n in range (len(idcode_detected)):
            idcode_modified.append(hex(int(idcode_detected[n][-7:],16)))    
        
        # Store the correct bsdl files in order 
        for j in range(len(idcode_modified)):
            for k in range(len(idcode_bsdl)) :

                if idcode_modified[j] == idcode_bsdl[k]:
                    self.bsdl_dict[j] = bsdl_file[k]

        # Check if the number of devices detected correponds to the number of bsdl files detected
        if (len(self.bsdl_dict) != self.total_devices):
            raise Exception("can't reach bsdl files of some devices")

        # Definition of dictionnaries and lists
 
        self.bsdl = {}
        self.bypass_opcode = {}
        self.sample_opcode = {}
        self.extest_opcode = {}

        self.instruct = {}          # the instruction to send at the jtag ftdi

        self.ir_length = []
        self.boundary_length = []


        # Get informations from bsdl files
        for k in sorted(self.bsdl_dict.keys()):
        
            bsdl_info = read_Bsdl.BsdlInfo(self.bsdl_dict.get(k))
            self.bsdl[k] = bsdl_info
            
            self.bypass_opcode[k] = self.bsdl[k]._get_opcode('BYPASS')
            self.extest_opcode[k] = self.bsdl[k]._get_opcode('EXTEST')
            self.sample_opcode[k] = self.bsdl[k]._get_opcode('SAMPLE')
            
            self.ir_length.append(self.bsdl[k].instruction_length)
            self.boundary_length.append(self.bsdl[k].boundary_length)
            self.instruct[k] = (self.bypass_opcode[k],self.ir_length[k])
            

        self.length_instruct = sum(self.ir_length)
        self.total_boundary_length = sum(self.boundary_length)
        
        self.previous_device_number = None

        # Init bit setting
        self.init_bit_settings()
        


    ###########################################################################
    ###########################################################################


    async def async_read_number_of_devices(self):
        """
        function that returns the number of devices detected in the jtag chain
        """
        result = await self.run_async_function(self.scan)
        print("Result:", result)
        return result

         
    
    async def async_get_idcodes(self):
        """
        function that returns the differnts idcodes of devices in order in the jtag chain
        """
        
        result = await self.run_async_function(self.idcode)
        print("Result:", result)
        return result


    
    async def async_read_pin(self, device_number, pin, direction):
        """
        function that reads the state of a pin
        """  
        result = await self.run_async_function(self.read,device_number, pin, direction)
        print("Result:", result)
        return result
            

    
    async def async_write_pin(self, device_number, pin, value):
        """
        function that writes on a pin
        """
        result = await self.run_async_function(self.write,device_number,pin,value)
        return result
    


    async def run_async_function(self,function,*args):
        async with self._mutex:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Submit the function to the executor
                future = executor.submit(function, *args)
                
                # Wait for the future to complete
                while not future.done():
                    await asyncio.sleep(0.1)
                    #print(f"Waiting for the thread to complete...")
                
                # Retrieve the result from the future
                result = future.result()
                #print("Result:", result)
                
                return result
            
            

    ###########################################################################
    ###########################################################################

    def scan(self):
        number_of_devices = len(self.idcode())

        return number_of_devices
    
    def idcode(self):
        number_of_devices = 0
        idcode_hex = {}

        self.engine.reset()
        self.engine.change_state('shift_dr')
        idcode = self.engine._ctrl.read(32)
        idcode_hex[number_of_devices] = str(f"0x{format(int(idcode),'08X')}")
        
        while int(idcode) != 0:
            number_of_devices += 1
            idcode = self.engine._ctrl.read(32)
            if (int(idcode)>0): 
                idcode_hex[number_of_devices] = str(f"0x{format(int(idcode),'08X')}")          
        
        self.engine.change_state('update_dr')
        self.engine.go_idle()

        return idcode_hex

    def read(self,device_number,pin,direction):
        global bit_settings

        boundary_scan = self.sample(device_number)
        for bit in range(0, self.boundary_length[device_number]):
            cell = self.bsdl[device_number].boundary_register[bit]
            cell_spec = cell["cell_spec"]
            if cell_spec["port_id"] == pin:
                if direction == "in" and cell_spec["function"].upper() == "INPUT": 

                    byte_array_scan = list(boundary_scan)

                    if byte_array_scan[bit] == 1 :
                        self.extest(bit_settings,device_number)
                        return True
                    else :
                        self.extest(bit_settings,device_number)
                        return False
                    
                elif direction == "out" and cell_spec["function"].upper() == "OUTPUT3":
                    
                    self.check_device(device_number)
                    
                    byte_array = list(bit_settings)
                
                    if byte_array[bit] == 1 :
                        self.extest(bit_settings,device_number)
                        return True
                    else :
                        self.extest(bit_settings,device_number)
                        return False

    
    def write (self, device_number,pin,value):
        bit_state_dict = {}
        for bit in range(0, self.boundary_length[device_number]):
            cell = self.bsdl[device_number].boundary_register[bit]
            cell_spec = cell["cell_spec"]
            if cell_spec["port_id"] == pin:
                if cell_spec["function"].upper() == "OUTPUT3":
                    disable_spec = cell["input_or_disable_spec"]                      
                    control_cell_number = int(disable_spec["control_cell"]) 
                    disable_value = int(disable_spec["disable_value"])
                    enable_value = 0 if disable_value == 1 else 1
                    bit_state_dict[control_cell_number] = enable_value
                    bit_state_dict[bit] = value
                    
        global bit_settings
        
        self.check_device(device_number)
        boundary_reg = bit_settings 
        bit_settings = get_bit_settings(bit_state_dict, boundary_reg) 
                    
        self.extest(bit_settings,device_number) 



    def init_bit_settings(self):
        """ function that init/reset the bit settings """

        global bit_settings
        self.engine.capture_dr()
        self.engine.reset()
        bit_settings = self.engine.read_dr(self.total_boundary_length)
        self.engine.go_idle()

        return bit_settings


    def check_device(self,device_number):
        """ Check if the device number is different than the previous device number. This function is used in read and write functions """
        if self.previous_device_number != device_number :
            self.init_bit_settings()
            self.previous_device_number = device_number
        

    def sample(self,device_number):
        """function that performs the BoundaryScan and returns the bitstream"""

        instruction = self.instruction(device_number,"sample")
        self.engine.capture_ir()
        self.engine.write_ir(instruction)
        self.engine.capture_dr()
        
        boundary_scan = self.engine.read_dr(self.boundary_length[device_number])

        boundary_scan_shift = bin(int(boundary_scan) >> device_number)
        boundary_scan_shift = int(boundary_scan_shift,2)
        boundary_scan_shift = format(boundary_scan_shift,f'0{self.boundary_length[device_number]}b')
        bit_sequence = BitSequence(boundary_scan_shift,msb=True)

        return bit_sequence    
    
    def extest(self,bit_settings,device_number):
        """ function that performs the BoundaryScan and writes to the registers """
    
        instruction = self.instruction(device_number,"extest")
        self.engine.capture_ir()
        self.engine.write_ir(instruction)
        self.engine.capture_dr()
        
        bit_settings_shift = bin(int(bit_settings) >> self.total_devices - device_number - 1)
        bit_settings_shift = int(bit_settings_shift,2)
        bit_settings_shift = format(bit_settings_shift,f'0{self.boundary_length[device_number]}b')
        bit_settings = BitSequence(bit_settings_shift,msb=True)

        self.engine.write_dr(bit_settings)  

    
    def instruction (self,device_number,mode):
        """ function that generate the instruction to control the device wanted """
        
        tab = []
        instruct = self.instruct.copy()  

        #print(instruct)
        if mode == "extest":
            instruct[device_number] = (self.extest_opcode[device_number],) + instruct[device_number][1:]
            
        elif mode == "sample":
            instruct[device_number] = (self.sample_opcode[device_number],) + instruct[device_number][1:]
            
        #print(instruct)
        
        for k in sorted(instruct.keys(),reverse = True):
            
            tab.append(BitSequence(int(instruct[k][0]),length = instruct[k][1]))
            result = ''.join(str(element)[3:] for element in tab)
            
            if len(tab) == self.total_devices: 
                #print(BitSequence(str(result), msb=True,length=self.length_instruct))
                return BitSequence(str(result), msb=True,length=self.length_instruct)
                                                        
        else :             
            raise Exception ("unknown mode")


