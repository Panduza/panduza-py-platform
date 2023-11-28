import time
from meta_drivers.dio import MetaDriverDio
from collections import ChainMap
from ...connectors.modbus_client_serial import ConnectorModbusClientSerial
from threading import Lock

mutex = Lock()

DIO_USBID_MODEL="05e1"
DIO_USBID_VENDOR="16c0"
DIO_USB_BAUDRATE=112500

DIO_MODBUS_ADDR=1
DIO_OFFSET_PULLS = 32
DIO_OFFSET_WRITE = 64

class DriverPZA_MODBUS_DIO(MetaDriverDio):

    def _PZA_DRV_config(self):
        # Extend the common bpc config
        return ChainMap(
            super()._PZA_DRV_config(),
            {
                "name": "io_control",
                "description": "Virtual DIO", 
                "compatible": ["pza_modbus_dio","io_pza_controling", "py.pza_modbus_dio"], # name to put in the tree.json
            },
        )

    def _PZA_DRV_loop_init(self):
        """Driver initialization
        """
        self.log.warning("inside loop init of driver")
        # Load tree settings

        self.settings = dict() if "settings" not in tree else tree["settings"]
        self.settings["vendor"] = DIO_USBID_VENDOR
        self.settings["model"] = DIO_USBID_MODEL
        self.settings["baudrate"] = DIO_USB_BAUDRATE
        self.settings["usb_serial_id"]
        self.settings["gpio_id"]
        
        mutex.acquire()
        self.modbus = ConnectorModbusClientSerial.GetV2(**self.settings) # init the connector
        mutex.release()

        # init values of instance dictionary
        self.modbus._ConnectorModbusClientSerial__instances["value_OUTPUT"] = False
        self.modbus._ConnectorModbusClientSerial__instances["active_low"] = False


        self.direction = False
        self.pullUp = ""
        self.pullDown = ""
        self.turnOn = False
        self.readValue = False

        self.log.info(tree["settings"])

        # first configuration
        self.__dir = {
            "direction":{
                "value":"in",
                "pull": "up", 
                "polling_cycle":5
            },
            "state":{
                "active":False,
                "active_low":False,
                "polling_cycle":5
            }    
        }
        super()._PZA_DRV_loop_init(tree)
    

    async def _PZA_DRV_DIO_get_direction_value(self):
        self.log.info(f"read direction value : {self.__dir['direction']['value']} !")
        return self.__dir["direction"]["value"]

    # configure the direction and value of io 
    async def _PZA_DRV_DIO_set_direction_value(self, v): # value direction (in/out)
        self.log.info(f"set direction value : {v}")
        self.__dir["direction"]["value"] = v

        gpio_id = self.settings["gpio_id"] # get the gpio_id number

        if v == "out":    
            self.log.info(f"it's a output")
            self.direction = self.modbus.write_coil(int(gpio_id),True,DIO_MODBUS_ADDR)
        elif v == "in":
            self.log.info("configuration as input")
            self.direction = self.modbus.write_coil(int(gpio_id),False,DIO_MODBUS_ADDR)
        else:
            raise Exception("error in value")

    async def _PZA_DRV_DIO_set_direction_pull(self, v):
        self.log.info(f"set direction pull : {v}")
        self.__dir["direction"]["pull"] = v # update brocker

        gpio_id = self.settings["gpio_id"]

        if self.__dir["direction"]["pull"]  == "up" and self.direction == False: # self.direction is false if it's input
            self.pullUp = self.modbus.write_coil(int(gpio_id)+DIO_OFFSET_PULLS, True,DIO_MODBUS_ADDR)
        elif self.__dir["direction"]["pull"]  == "down" and self.direction == False :
            self.pullDown = self.modbus.write_coil(int(gpio_id)+DIO_OFFSET_PULLS, False,DIO_MODBUS_ADDR)
        else : 
            raise Exception('You cant configure a pull for a output')

    async def _PZA_DRV_DIO_get_direction_pull(self):
        self.log.info(f"read direction pull : {self.__dir['direction']['pull']}!")
        return self.__dir["direction"]["pull"]
        
        
    async def _PZA_DRV_DIO_get_state_active(self):
        self.log.info(f"read state active : {self.__dir['state']['active']}!")

        # get the values of the instance dictionary
        valueOfIo = self.modbus._ConnectorModbusClientSerial__instances.get("value_OUTPUT")
        activeLow = self.modbus._ConnectorModbusClientSerial__instances.get("active_low")

        # update the fields
        if (int(self.settings["gpio_id"])%2 != 0 or int(self.settings["gpio_id"]) == 22 or int(self.settings["gpio_id"]) == 28) and self.__dir["direction"]["value"] == "in":    
            self.__dir["state"]["active"] = valueOfIo
            self.__dir["state"]["active_low"] = activeLow
            self.readValue = self.modbus.read_discrete_inputs(int(self.settings["gpio_id"]),1,DIO_MODBUS_ADDR) # push button test
            self.__dir["state"]["active"] = self.readValue
        elif (int(self.settings["gpio_id"])%2 == 0 or int(self.settings["gpio_id"]) == 21) and self.__dir["direction"]["value"] == "in":
            self.__dir["state"]["active"] = valueOfIo
            self.__dir["state"]["active_low"] = activeLow
            self.readValue = self.modbus.read_discrete_inputs(int(self.settings["gpio_id"]),1,DIO_MODBUS_ADDR) # push button test
            self.__dir["state"]["active"] = self.readValue 

        return self.__dir["state"]["active"]
    
    async def _PZA_DRV_DIO_set_state_active(self,v):
        self.log.info(f"set state active : {v}")
        self.__dir["state"]["active"] = v
        gpio_id = self.settings["gpio_id"]

        if self.direction == True and (self.__dir["state"]["active_low"] == False):
            self.turnOn = self.modbus.write_coil(DIO_OFFSET_WRITE+int(gpio_id),v,DIO_MODBUS_ADDR)  # write to coil
            self.readValue = self.modbus.read_discrete_inputs(int(gpio_id)+1,1,DIO_MODBUS_ADDR) # read the input value
            self.modbus._ConnectorModbusClientSerial__instances["value_OUTPUT"] = self.readValue
            self.modbus._ConnectorModbusClientSerial__instances["active_low"] = self.__dir["state"]["active_low"]
        elif self.direction == True and (self.__dir["state"]["active_low"] == True): 
            invert = not v
            self.turnOn = self.modbus.write_coil(DIO_OFFSET_WRITE+int(gpio_id),invert,DIO_MODBUS_ADDR) 
            self.readValue = self.modbus.read_discrete_inputs(int(gpio_id)+1,1,DIO_MODBUS_ADDR) # read the input value
            self.modbus._ConnectorModbusClientSerial__instances["value_OUTPUT"] = invert(self.readValue)
            self.modbus._ConnectorModbusClientSerial__instances["active_low"] = self.__dir["state"]["active_low"]
        elif self.direction == False:    
            raise Exception("can't write value to a input")


    def _PZA_DRV_DIO_get_state_activeLow(self):
        self.log.info(f"read state active low : {self.__dir['state']['active_low']}!")
        return self.__dir["state"]["active_low"]
    
    def _PZA_DRV_DIO_set_state_activeLow(self,v):
        self.log.info(f"set state active low : {v}")
        self.__dir["state"]["active_low"] = v

    def _PZA_DRV_DIO_get_state_polling_cycle(self):
        self.log.info(f"read state pulling : {self.__dir['state']['polling_cycle']}!")
        return self.__dir["state"]["polling_cycle"]
    
    def _PZA_DRV_DIO_set_state_polling_cycle(self,v):
        self.log.error(f"set state pulling : {v}")
        self.__dir["state"]["polling_cycle"] = v

    def _PZA_DRV_DIO_get_direction_polling_cycle(self):
        self.log.info(f"read direction pulling : {self.__dir['direction']['polling_cycle']}!")
        return self.__dir["direction"]["polling_cycle"]
    
    def _PZA_DRV_DIO_set_direction_polling_cycle(self,v):
        self.log.error(f"set direction pulling : {v}")
        self.__dir["direction"]["polling_cycle"] = v