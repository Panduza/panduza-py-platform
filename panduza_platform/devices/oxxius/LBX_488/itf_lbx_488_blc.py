
from meta_drivers.blc import MetaDriverBlc


from connectors.serial_low_usb import ConnectorSerialLowUsb



class InterfaceLbx488Blc(MetaDriverBlc):
    """Fake BLC driver
    """

    # ---

    def __init__(self, name=None, settings={}) -> None:
        """Constructor
        """
        self.settings = settings
        super().__init__(name=name)

    def msg_to_float(self, bytes_value):
        return float(bytes_value[:-1])

    def mA_to_A(self, ma_value):
        return (ma_value * 0.001)

    # =============================================================================
    # FROM MetaDriverBlc

    # ---

    async def _PZA_DRV_loop_init(self):
        """Init function
        Reset fake parameters
        """

        self.usb_conn = await ConnectorSerialLowUsb.Get(**self.settings)


        # Get min and max value for current set point
        # When setting the current, the unit used is the percentage of the nominal current. When reading the
        # current, the returned value is expressed in milliAmperes.
        # Although the setting of “100%” is designed to drive the LBX at nominal power at the beginning of the
        # unit’s lifespan, the user is allowed to set this current up to 125% of the nominal current in order to
        # cope for a potential loss of efficiency due to aging
        await self.usb_conn.write_and_read("CM 125")
        current_max = self.msg_to_float(await self.usb_conn.write_and_read("?SC"))
        self.min_max_current={
            "min": 0,
            "max": self.mA_to_A(current_max)
        }
        # print(self.min_max_current)


        print(await self.usb_conn.write_and_read("CM 10"))
        print(await self.usb_conn.write_and_read("?SC"))
        print(await self.usb_conn.write_and_read("PM 200"))
        print(await self.usb_conn.write_and_read("PM 5"))
        await self.__debug_print_all_registers()
        # data = await self.usb_conn.write_and_read("?SV")
        # print(data)
        # data = await self.usb_conn.write_and_read("?SV")
        # print(data)
        
        # ?ACC (current constant)
        # ?APC (power constant)
        
        self.__fakes = {
            "mode": {
                "value": "constant_power"
            },
            "enable": {
                "value": False
            },
            "power": {
                "value": 0,
                "min": -1000,
                "max":  1000,
                "decimals": 2
            },
            "current": {
                "value":  0,
                "min":   0,
                "max":  50,
                "decimals": 3
            },
            "misc": {
                "model": "DEATHSTAR (Panduza Fake Laser Control)"
            }
        }

        # Call meta class BLC ini
        await super()._PZA_DRV_loop_init()


    # =============================================================================
    # **** MODE/VALUE ****

    # ---

    async def _PZA_DRV_BLC_read_mode_value(self):
        """
        """
        ACC = await self.usb_conn.write_and_read("?ACC")
        if ACC == b'1\x00':
            return "constant_current"

        APC = await self.usb_conn.write_and_read("?APC")
        if APC == b'1\x00':
            return "constant_power"

        return "no_regulation"

    # ---

    async def _PZA_DRV_BLC_write_mode_value(self, v):
        """
        """
        self.log.info(f"write enable : {v}")
        self.__fakes["mode"]["value"] = v

    # ---

    # =============================================================================
    # **** ENABLE/VALUE ****

    # ---

    async def _PZA_DRV_BLC_read_enable_value(self):
        """Read emission status and convert to bool
        """
        EMISSION = await self.usb_conn.write_and_read("?L")
        if EMISSION == b'1\x00':
            return True
        else:
            return False

    # ---

    async def _PZA_DRV_BLC_write_enable_value(self, v):
        self.log.info(f"write enable : {v}")
        int_value = 0 # off by default
        if v:
            int_value = 1
        status = await self.usb_conn.write_and_read(f"L {int_value}")
        self.log.info(f"status={status}")

    # ---

    ###########################################################################

    async def _PZA_DRV_BLC_read_power_value(self):
        # self.log.debug(f"read power value !")
        return self.__fakes["power"]["value"]

    # ---

    async def _PZA_DRV_BLC_write_power_value(self, v):
        self.log.info(f"write power : {v}")
        self.__fakes["power"]["value"] = v
        self.__fakes["power"]["real"] = v
    
    # ---

    async def _PZA_DRV_BLC_power_value_min_max(self):
        return {
            "min": self.__fakes["power"]["min"],
            "max": self.__fakes["power"]["max"] 
        }

    # ---

    async def _PZA_DRV_BLC_read_power_decimals(self):
        return self.__fakes["power"]["decimals"]


    # =============================================================================
    # **** DEBUG ****

    async def _PZA_DRV_BLC_read_current_value(self):
        # self.log.debug(f"read current value !")
        return self.__fakes["current"]["value"]

    # ---

    async def _PZA_DRV_BLC_write_current_value(self, v):
        self.log.info(f"write current : {v}")
        self.__fakes["current"]["value"] = v
        self.__fakes["current"]["real"] = v

    # ---

    async def _PZA_DRV_BLC_current_value_min_max(self):
        return self.min_max_current

    # ---

    async def _PZA_DRV_BLC_read_current_decimals(self):
        return self.__fakes["current"]["decimals"]

    # ---

    # =============================================================================
    # **** DEBUG ****

    async def __debug_print_all_registers(self):
        """Print all read registers
        """
        cmds = [
            "?SV", "?ACC", "?APC", "?BT", "?C", "?CDRH", "?CW", 
            "?DST", "?DT", "?F", "?HH", "?HID", "?INT", "?IV", "?L", 
            "?MAXLC", "?MAXLP", "?P", "?PST", "?SC", "?SP", "?STA",
            "?T"
        ]
        for cmd_str in cmds:    
            print(cmd_str, " = ", await self.usb_conn.write_and_read(cmd_str) )

