
from meta_drivers.blc import MetaDriverBlc
from connectors.serial_tty import ConnectorSerialTty

COMMAND_TIME_LOCK=1

### Commands Definitions

def cmd(cmd):
    """Append the correct command termination to the command
    """
    termination = "\n\r"
    return (cmd + termination)

### Interface Definition

class InterfaceCobolt0501Blc(MetaDriverBlc):
    """
    """

    # ---

    def __init__(self, name=None, settings={}) -> None:
        """Constructor
        """
        self.settings = settings
        super().__init__(name=name)


    # =============================================================================
    # FROM MetaDriverBlc

    # ---

    # def _PZA_DRV_BLC_config(self):
    #     """
    #     """
    #     return {
    #         "name": "panduza.fake.bpc",
    #         "description": "Virtual BPC"
    #     }

    # ---

    async def _PZA_DRV_loop_init(self):
        """Init function
        Reset fake parameters
        """
        
        self.serial_connector = await ConnectorSerialTty.Get(**self.settings)

        # command = "sn?"
        # termination = "\n\r"
        # cmd = (command + termination)
        # print(cmd.encode())
        # # print("pok")
        # idn = await self.serial_connector.write_and_read_until(cmd, expected=b"\n")
        # print(f"ddddddd {idn}")
        # idn = await self.serial_connector.write_and_read_until(cmd, expected=b"\n")
        # print(f"ddddddd {idn}")
        # idn = await self.serial_connector.write_and_read_until(cmd, expected=b"\n")
        # print(f"ddddddd {idn}")
        # leds = await self.serial_connector.write_and_read_during("leds?\r\n", time_lock_s=COMMAND_TIME_LOCK, read_duration_s=1)
        # print(f"leds {leds}")


        self.__debug_print_all_registers()

        self.__fakes = {
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

        # Call meta class BPC ini
        await super()._PZA_DRV_loop_init()

    ###########################################################################

    # ---

    async def _PZA_DRV_BLC_read_mode_value(self):
        """Must get the mode value on the BPC and return it
        """
        raise NotImplementedError("Must be implemented !")

    async def _PZA_DRV_BLC_write_mode_value(self, v):
        """Must set *v* as the new mode value on the BPC
        """
        raise NotImplementedError("Must be implemented !")


    # ---

    async def _PZA_DRV_BLC_read_enable_value(self):
        """Get laser ON/OFF state
        """
        # 0 = OFF
        # 1 = ON
        value = await self.serial_connector.write_and_read_until(cmd("l?"), expected=b"\n")
        return bool(value)

    # ---

    async def _PZA_DRV_BLC_write_enable_value(self, v):
        """Set laser ON/OFF state
        """
        val_int = 0
        if v:
            val_int = 1
        await self.serial_connector.write(cmd(f"l{val_int}"), expected=b"\n")

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

    ###########################################################################

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
        return {
            "min": self.__fakes["current"]["min"],
            "max": self.__fakes["current"]["max"] 
        }

    # ---

    async def _PZA_DRV_BLC_read_current_decimals(self):
        return self.__fakes["current"]["decimals"]


    ###########################################################################

    async def __debug_print_all_registers(self):
        """Print all read registers
        """
        cmd_str = "l?"
        print(cmd_str, " = ", await self.serial_connector.write(cmd(cmd_str), expected=b"\n") )
        cmd_str = "p?"
        print(cmd_str, " = ", await self.serial_connector.write(cmd(cmd_str), expected=b"\n") )
        cmd_str = "pa?"
        print(cmd_str, " = ", await self.serial_connector.write(cmd(cmd_str), expected=b"\n") )
        cmd_str = "i?"
        print(cmd_str, " = ", await self.serial_connector.write(cmd(cmd_str), expected=b"\n") )
        cmd_str = "ilk?"
        print(cmd_str, " = ", await self.serial_connector.write(cmd(cmd_str), expected=b"\n") )
        cmd_str = "leds?"
        print(cmd_str, " = ", await self.serial_connector.write(cmd(cmd_str), expected=b"\n") )
        cmd_str = "f?"
        print(cmd_str, " = ", await self.serial_connector.write(cmd(cmd_str), expected=b"\n") )
        cmd_str = "sn?"
        print(cmd_str, " = ", await self.serial_connector.write(cmd(cmd_str), expected=b"\n") )
        cmd_str = "hrs?"
        print(cmd_str, " = ", await self.serial_connector.write(cmd(cmd_str), expected=b"\n") )



