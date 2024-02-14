
from meta_drivers.blc import MetaDriverBlc
from connectors.serial_tty import ConnectorSerialTty

COMMAND_TIME_LOCK=1

### Commands Definitions

def cmd(cmd):
    """Append the correct command termination to the command
    """
    termination = "\r" # only one "\r" is OK, do not use "\n"
    return (cmd + termination)

### Interface Definition

class InterfaceCobolt0501Blc(MetaDriverBlc):
    """
    
    https://github.com/cobolt-lasers/pycobolt
    
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

        print("clear", await self.serial_connector.write_and_read_until(cmd(""), expected=b"\n"))
        print("clear", await self.serial_connector.write_and_read_until(cmd(""), expected=b"\n"))
        print("clear", await self.serial_connector.write_and_read_until(cmd(""), expected=b"\n"))
        print("l?", await self.serial_connector.write_and_read_until(cmd("l?"), expected=b"\n"))
        print("l0", await self.serial_connector.write_and_read_until(cmd("l0"), expected=b"\n"))

        print("slc", )
        # print("slc?", await self.serial_connector.write_and_read_until(cmd("slc?"), expected=b"\n"))
        print("i?", await self.serial_connector.write_and_read_until(cmd("i?"), expected=b"\n"))


        

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


        await self.__debug_print_all_registers()

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
        mode_b = await self.serial_connector.write_and_read_until(cmd("gam?"), expected=b"\n")
        print(f"mode {mode_b}")
        mode_i = int(mode_b.decode('utf-8').rstrip())
        print(f"mode {mode_i}")
        
        if mode_i == 0:
            return "constant_current"
        if mode_i == 1:
            return "constant_power"
        # if mode_i == 2:
        #     return "modulation"

        return "no_regulation"


    async def _PZA_DRV_BLC_write_mode_value(self, v):
        """Must set *v* as the new mode value on the BPC
        """
        self.log.info(f"write enable : {v}")
        if v == "constant_current":
            await self.serial_connector.write_and_read_until(cmd("ci"), expected=b"\n")

        if v == "constant_power":
            await self.serial_connector.write_and_read_until(cmd("cp"), expected=b"\n")

    # ---

    async def _PZA_DRV_BLC_read_enable_value(self):
        """Get laser ON/OFF state
        """
        # 0 = OFF
        # 1 = ON
        value_b = await self.serial_connector.write_and_read_until(cmd("l?"), expected=b"\n")
        value_i = int(value_b.decode('utf-8').rstrip())
        self.log.info(f"read enable value : {value_i} | {bool(value_i)}")
        return bool(value_i)

    # ---

    async def _PZA_DRV_BLC_write_enable_value(self, v):
        """Set laser ON/OFF state
        """
        val_int = 0
        if v:
            val_int = 1
        self.log.info(f"write enable value : {val_int}")
        await self.serial_connector.write_and_read_until(cmd(f"l{val_int}"), expected=b"\n")

    # ---

    ###########################################################################

    async def _PZA_DRV_BLC_read_power_value(self):
        power_b = await self.serial_connector.write_and_read_until(cmd(f"p?"), expected=b"\n")
        power_f = float(power_b.decode('utf-8').rstrip())
        return power_f

    # ---

    async def _PZA_DRV_BLC_write_power_value(self, v):
        self.log.info(f"write power : {v}")
        await self.serial_connector.write_and_read_until(cmd(f"p {v}"), expected=b"\n")

    # ---

    async def _PZA_DRV_BLC_power_value_min_max(self):
        return {
            "min": 0,
            "max": 0.3
        }

    # ---

    async def _PZA_DRV_BLC_read_power_decimals(self):
        return 3

    ###########################################################################

    # ---

    async def _PZA_DRV_BLC_read_current_value(self):
        current_b = await self.serial_connector.write_and_read_until(cmd(f"glc?"), expected=b"\n")
        current_f = float(current_b.decode('utf-8').rstrip())
        self.log.debug(f"read current : {current_f}")
        return current_f

    # ---

    async def _PZA_DRV_BLC_write_current_value(self, v):
        self.log.info(f"write current : {v}")
        await self.serial_connector.write_and_read_until(cmd(f"slc {v}"), expected=b"\n")

    # ---

    async def _PZA_DRV_BLC_current_value_min_max(self):
        return {
            "min": 0,
            "max": 0.5
        }

    # ---

    async def _PZA_DRV_BLC_read_current_decimals(self):
        return 1


    ###########################################################################

    async def __debug_print_all_registers(self):
        """Print all read registers
        """
        cmds = [
            "l?", "p?", "pa?", "i?", "ilk?", "leds?", "f?", "sn?", "hrs?", "glm?", "glc?"
        ]
        for cmd_str in cmds:
            print(cmd_str, " = ", await self.serial_connector.write_and_read_until(cmd(cmd_str), expected=b"\n") )


