
from meta_drivers.blc import MetaDriverBlc
from connectors.serial_tty import ConnectorSerialTty

COMMAND_TIME_LOCK=1

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

    # def _PZA_DRV_BPC_config(self):
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
        
        command = "sn?"
        termination = "\r\n"
        cmd = (command + termination)
        print(cmd)
        idn = await self.serial_connector.write_and_read_until(cmd, time_lock_s=COMMAND_TIME_LOCK, read_duration_s=1)
        print(f"ddddddd {idn}")
        idn = await self.serial_connector.write_and_read_until(cmd, time_lock_s=COMMAND_TIME_LOCK, read_duration_s=1)
        print(f"ddddddd {idn}")
        idn = await self.serial_connector.write_and_read_until(cmd, time_lock_s=COMMAND_TIME_LOCK, read_duration_s=1)
        print(f"ddddddd {idn}")
        # leds = await self.serial_connector.write_and_read_until("leds?\r\n", time_lock_s=COMMAND_TIME_LOCK, read_duration_s=1)
        # print(f"leds {leds}")

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

    async def _PZA_DRV_BPC_read_enable_value(self):
        # self.log.debug(f"read enable !")
        return self.__fakes["enable"]["value"]

    # ---

    async def _PZA_DRV_BPC_write_enable_value(self, v):
        self.log.info(f"write enable : {v}")
        self.__fakes["enable"]["value"] = v

    ###########################################################################

    async def _PZA_DRV_BPC_read_power_value(self):
        # self.log.debug(f"read power value !")
        return self.__fakes["power"]["value"]

    # ---

    async def _PZA_DRV_BPC_write_power_value(self, v):
        self.log.info(f"write power : {v}")
        self.__fakes["power"]["value"] = v
        self.__fakes["power"]["real"] = v
    
    # ---

    async def _PZA_DRV_BPC_power_value_min_max(self):
        return {
            "min": self.__fakes["power"]["min"],
            "max": self.__fakes["power"]["max"] 
        }

    # ---

    async def _PZA_DRV_BPC_read_power_decimals(self):
        return self.__fakes["power"]["decimals"]

    ###########################################################################

    async def _PZA_DRV_BPC_read_current_value(self):
        # self.log.debug(f"read current value !")
        return self.__fakes["current"]["value"]

    # ---

    async def _PZA_DRV_BPC_write_current_value(self, v):
        self.log.info(f"write current : {v}")
        self.__fakes["current"]["value"] = v
        self.__fakes["current"]["real"] = v

    # ---

    async def _PZA_DRV_BPC_current_value_min_max(self):
        return {
            "min": self.__fakes["current"]["min"],
            "max": self.__fakes["current"]["max"] 
        }

    # ---

    async def _PZA_DRV_BPC_read_current_decimals(self):
        return self.__fakes["current"]["decimals"]

