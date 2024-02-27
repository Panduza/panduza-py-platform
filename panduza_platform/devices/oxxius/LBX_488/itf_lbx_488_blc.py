
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
        return round((ma_value * 0.001), 3)

    def A_to_mA(self, ma_value):
        return (ma_value * 1000)

    def mW_to_W(self, ma_value):
        return round((ma_value * 0.001), 3)

    def W_to_mW(self, ma_value):
        return (ma_value * 1000)

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
        current_save = self.msg_to_float(await self.usb_conn.write_and_read("?SC"))
        current_save = int(current_save)
        await self.usb_conn.write_and_read("CM 125")
        current_max = self.msg_to_float(await self.usb_conn.write_and_read("?SC"))
        self.min_max_current={
            "min": 0,
            "max": self.mA_to_A(current_max)
        }
        await self.usb_conn.write_and_read(f"CM {current_save}") # restore previous value
        # print(self.min_max_current)

        # Get min and max value for power set point
        power_max = self.msg_to_float(await self.usb_conn.write_and_read("?MAXLP"))
        self.min_max_power={
            "min": 0,
            "max": self.mW_to_W(power_max)
        }



        await self.__debug_print_all_registers()
        # data = await self.usb_conn.write_and_read("?SV")
        # print(data)
        # data = await self.usb_conn.write_and_read("?SV")
        # print(data)


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
        if v == "constant_current":
            await self.usb_conn.write_and_read("ACC 1")
        if v == "constant_power":
            await self.usb_conn.write_and_read("APC 1")

        await self.__debug_print_all_registers()

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

        # Wait for it
        value_i = None
        while(value_i != v):
            value_i = await self._PZA_DRV_BLC_read_enable_value()

    # ---

    ###########################################################################

    async def _PZA_DRV_BLC_read_power_value(self):
        c = self.msg_to_float(await self.usb_conn.write_and_read(f"?SP"))
        print(c)
        print(self.mW_to_W(c))
        return self.mW_to_W(c)

    # ---

    async def _PZA_DRV_BLC_write_power_value(self, v):
        self.log.info(f"write power : {v}")
        val_mW = self.W_to_mW(v)
        await self.usb_conn.write_and_read(f"PM {val_mW}")

    # ---

    async def _PZA_DRV_BLC_power_value_min_max(self):
        return self.min_max_power

    # ---

    async def _PZA_DRV_BLC_read_power_decimals(self):
        return 3


    # =============================================================================
    # **** DEBUG ****

    async def _PZA_DRV_BLC_read_current_value(self):
        c = self.msg_to_float(await self.usb_conn.write_and_read(f"?SC"))
        return self.mA_to_A(c)

    # ---

    async def _PZA_DRV_BLC_write_current_value(self, v):
        self.log.info(f"write current : {v}")
        val_mA = self.A_to_mA(v)
        await self.usb_conn.write_and_read(f"CM {val_mA}")

    # ---

    async def _PZA_DRV_BLC_current_value_min_max(self):
        return self.min_max_current

    # ---

    async def _PZA_DRV_BLC_read_current_decimals(self):
        return 3

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

