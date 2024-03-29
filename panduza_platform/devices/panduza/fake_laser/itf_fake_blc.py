
from meta_drivers.blc import MetaDriverBlc

class InterfacePanduzaFakeBlc(MetaDriverBlc):
    """Fake BLC driver
    """

    # =============================================================================
    # FROM MetaDriverBlc

    # # ---

    # def _PZA_DRV_BLC_config(self):
    #     """
    #     """
    #     return {
    #         "name": "panduza.fake.bLc",
    #         "description": "Virtual BLC"
    #     }

    # ---

    async def _PZA_DRV_loop_init(self):
        """Init function
        Reset fake parameters
        """
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

    ###########################################################################


    async def _PZA_DRV_BLC_read_mode_value(self):
        return self.__fakes["mode"]["value"]


    async def _PZA_DRV_BLC_write_mode_value(self, v):
        self.log.info(f"write enable : {v}")
        self.__fakes["mode"]["value"] = v


    async def _PZA_DRV_BLC_read_enable_value(self):
        # self.log.debug(f"read enable !")
        return self.__fakes["enable"]["value"]

    # ---

    async def _PZA_DRV_BLC_write_enable_value(self, v):
        self.log.info(f"write enable : {v}")
        self.__fakes["enable"]["value"] = v

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

