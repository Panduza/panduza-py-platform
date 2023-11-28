import time
import serial
from panduza_platform import MetaDriverBpc

class DriverHm7044(MetaDriverBpc):
    """ Driver to manage the HM7044 power supply
    """

    ###########################################################################
    ###########################################################################
    
    def config(self):
        """ FROM MetaDriver
        """
        return {
            "compatible": "bpc_hm7044",
            "info": { "type": "bpc", "version": "1.0" },
            "settings": {
                "serial_port" : "Serial port on which the power supply is connected",
                "channel" : "Channel number that must be driven by this interfaces [1,2,3,4]"
            }
        }
        
    ###########################################################################
    ###########################################################################

    def setup(self, tree):
        """ FROM MetaDriver
        """
        # Initialize variables
        self.serial_port = tree["settings"]["serial_port"]
        self.channel = tree["settings"]["channel"]

        #
        self.enable=False
        self.voltage=0
        self.current=0

        # 
        # self.__serial = serial.Serial(self.serial_port, 9600, timeout=1)

        # Register commands
        self.register_command("enable/set", self.__set_enable)
        self.register_command("voltage/set", self.__set_voltage)
        self.register_command("current/set", self.__set_current)

    ###########################################################################
    ###########################################################################

    def on_start(self):
        #
        # self.push_io_value(self.value)
        pass

    ###########################################################################
    ###########################################################################
        
    def loop(self):
        """ FROM MetaDriver
        """
        # if self._loop % 2 == 0:
        #     self.__push_attribute_value()
        #     self.__push_attribute_direction()
        # self._loop += 1
        # time.sleep(0.5)
        return False

    ###########################################################################
    ###########################################################################

    def __set_enable(self, payload):
        """
        """
        # Parse request
        req = self.payload_to_dict(payload)
        req_enable = req["enable"]
        self.enable=req_enable

        try:
                        
            # message_on = bytearray(b'EN\r\n')
            # read_v = bytearray(b'\r\n')
            # ser.write(message_on)

            # Update mqtt
            self.push_power_supply_enable(self.enable)

            # log
            logger.info(f"new enable : {self.enable}")

        except IOError as e:
            # mogger.error("Unable to set value %s to GPIO %s (%s) | %s", str(val), self.id, path, repr(e))
            pass

    ###########################################################################
    ###########################################################################

    def __set_voltage(self, payload):
        """
        """
        # Parse request
        req = self.payload_to_dict(payload)
        req_voltage = req["voltage"]
        self.voltage=req_voltage

        try:
                        
            # message_on = bytearray(b'EN\r\n')
            # read_v = bytearray(b'\r\n')
            # ser.write(message_on)

            # Update mqtt
            self.push_power_supply_voltage(self.voltage)

            # log
            logger.info(f"new voltage : {self.voltage}")

        except IOError as e:
            # mogger.error("Unable to set value %s to GPIO %s (%s) | %s", str(val), self.id, path, repr(e))
            pass

    ###########################################################################
    ###########################################################################

    def __set_current(self, payload):
        """
        """
        # Parse request
        req = self.payload_to_dict(payload)
        req_current = req["current"]
        self.current=req_current

        try:

            # message_on = bytearray(b'EN\r\n')
            # read_v = bytearray(b'\r\n')
            # ser.write(message_on)

            # Update mqtt
            self.push_power_supply_current(self.current)

            # log
            logger.info(f"new current : {self.current}")

        except IOError as e:
            # mogger.error("Unable to set value %s to GPIO %s (%s) | %s", str(val), self.id, path, repr(e))
            pass


