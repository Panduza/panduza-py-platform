
from core.platform_device import PlatformDevice
from connectors.boundary_scan_ftdi import ConnectorBoundaryScanFtdi
from extlibs.bsdl_reader import read_Bsdl

from pyftdi.jtag import JtagEngine

import asyncio

USBID_VENDOR="0403"
USBID_MODEL="6014"
USBID_SERIAL_SHORT="null"

class DeviceFtdiFt232h_jtag(PlatformDevice):
    """ FTDI
    """

    def _PZA_DEV_config(self):
        """
        """
        return {
            "family": "TBD",
            "model": "Ft232h_jtag",
            "manufacturer": "Ftdi"
        }

    def _PZA_DEV_interfaces_generator(self):
        """
        """
        interfaces = []
        
        jtag_frequency = self.get_settings().get("jtag_frequency",6E6)
        jtag_bsdl_folder = self.get_settings().get("jtag_bsdl_folder", "/etc/BSDL")

        pins_detected = self.get_pins_from_idcode(jtag_bsdl_folder) # a list of pins from each device detected
        pins_wanted  = self.get_settings().get("pins_wanted",None)
        number_of_devices = len(pins_detected)

        # print(pins_wanted)
        # print(pins)

        pins = pins_detected.copy()
    
        #pins = asyncio.run(get_pins_from_idcode(jtag_bsdl_folder,jtag_frequency))
        #pins = run_async_function(jtag_bsdl_folder,jtag_frequency)
        
        if pins_wanted != None : 
            pins_list = set(pins_wanted)

            for i in range(number_of_devices):
                if pins[i] is not None:
                    common_pins = pins_list.intersection(pins[i])
                    if not common_pins:
                        pins[i] = None
                    else:
                        pins[i] = list(common_pins) 
    


        for device_number in range(0,number_of_devices):
            if pins[device_number] is not None:
                for pin in pins[device_number]:
                    interfaces.append({
                        "name": f"jtag_device_{device_number}_{pin}",
                        "driver": "ftdi.boudary_scan.dio",
                        "settings": {
                            "usb_vendor": USBID_VENDOR,
                            "usb_model": USBID_MODEL,
                            "usb_serial_short": USBID_SERIAL_SHORT,

                            "jtag_frequency" : jtag_frequency,
                            "jtag_bsdl_folder" : jtag_bsdl_folder,
                            "device_number" : device_number,
                            "pin" : pin
                            
                        }
                    })
                    
        return interfaces


    

    def get_pins_from_idcode(self,jtag_bsdl_folder):
        number_of_devices = 0
        idcode_detected = {}
        idcode_modified = []
        pins = []

        idcode_bsdl = read_Bsdl.get_idcodes_from_bsdl(jtag_bsdl_folder)
        pins_bsdl = read_Bsdl.get_pins_from_bsdl(jtag_bsdl_folder)

        self.engine = JtagEngine(frequency=float(10E6))
        self.engine.configure(f'ftdi://0x{USBID_VENDOR}:0x{USBID_MODEL}/1')
        self.engine.reset()

        self.engine.change_state('shift_dr')
        idcode = self.engine._ctrl.read(32)
        idcode_detected[number_of_devices] = str(f"0x{format(int(idcode),'08X')}")
        
        while int(idcode) != 0:
            number_of_devices += 1
            idcode = self.engine._ctrl.read(32)
            if (int(idcode)>0): 
                idcode_detected[number_of_devices] = str(f"0x{format(int(idcode),'08X')}")          
        
        self.engine.change_state('update_dr')
        self.engine.go_idle()
        

        # Remove the first 4 bits of the idcodes (= idcode without 4-bit version number)
        for n in range (len(idcode_detected)):
            idcode_modified.append(hex(int(idcode_detected[n][-7:],16)))    
        
        for j in range(len(idcode_modified)):
            for k in range(len(idcode_bsdl)) :

                if idcode_modified[j] == idcode_bsdl[k]:
                    pins.append(pins_bsdl[k])
        
        return pins

    
    
# async def get_pins_from_idcode(jtag_bsdl_folder,jtag_frequency):

#     idcode_modified = []
#     pins = []

#     idcode_bsdl = read_bsdlJson_files.get_idcode_from_bsdl(jtag_bsdl_folder)
#     pins_bsdl = read_bsdlJson_files.get_pins_from_bsdl(jtag_bsdl_folder)

#     jtag_connector = await ConnectorBoundaryScanFtdi.Get(usb_vendor=USBID_VENDOR,
#                                                               usb_model=USBID_MODEL,
#                                                               usb_serial_short=USBID_SERIAL_SHORT,
#                                                               jtag_bsdl_folder=jtag_bsdl_folder,
#                                                               jtag_frequency=jtag_frequency)

    

#     idcodes_detected = await jtag_connector.get_idcodes()

#     # Remove the first 4 bits of the idcodes (= idcode without 4-bit version number)
#     for n in range (len(idcodes_detected)):
#         idcode_modified.append(hex(int(idcodes_detected[n][-7:],16)))    
    
#     for j in range(len(idcode_modified)):
#         for k in range(len(idcode_bsdl)) :

#             if idcode_modified[j] == idcode_bsdl[k]:
#                 pins.append(pins_bsdl[k])
    
#     return pins




# def run_async_function(jtag_bsdl_folder,jtag_frequency):
#     # loop = asyncio.new_event_loop()
#     #asyncio.set_event_loop(loop)
#     print("pookkkkkkk")
#     pins = asyncio.get_event_loop().run_until_complete(get_pins_from_idcode(jtag_bsdl_folder, jtag_frequency))
#     print("fiiiiiiiiiiiiiiiiiiiiiiiin")
#     #return pins
#     return [ None,["PA5","PA10"],None,["PA5","PA10"]]





    