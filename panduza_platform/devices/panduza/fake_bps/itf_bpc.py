import time
from collections import ChainMap
from meta_drivers.bpc import MetaDriverBpc

class InterfacePanduzaFakeBpc(MetaDriverBpc):
    """Fake BPC driver
    """

    # =============================================================================
    # FROM MetaDriverBpc

    # ---

    def _PZA_DRV_BPC_config(self):
        """
        """
        return {
            "name": "panduza.fake.bpc",
            "description": "Virtual BPC"
        }

    # ---

    async def _PZA_DRV_loop_init(self):
        """Init function
        Reset fake parameters
        """
        self.__fakes = {
            "enable": {
                "value": False
            },
            "voltage": {
                "value": 0,
                "real": 0,
                "min": -1000,
                "max":  1000,
                "decimals": 2
            },
            "current": {
                "value":  0,
                "real":  0,
                "min":   0,
                "max":  50,
                "decimals": 3
            },
            "settings_capabilities": {
                "ovp": False,       # Over Voltage Protection
                "ocp": False,       # Over Current Protection
                "silent": False,    # Silent mode
            },
            "settings": {
                "ovp": False,
                "ocp": False,
                "silent": False,
            },
            "misc": {
                "model": "GOUBY42 (Panduza Fake Power Supply)"
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

    async def _PZA_DRV_BPC_read_voltage_value(self):
        # self.log.debug(f"read voltage value !")
        return self.__fakes["voltage"]["value"]

    # ---

    async def _PZA_DRV_BPC_write_voltage_value(self, v):
        self.log.info(f"write voltage : {v}")
        self.__fakes["voltage"]["value"] = v
        self.__fakes["voltage"]["real"] = v
    
    # ---

    async def _PZA_DRV_BPC_voltage_value_min_max(self):
        return {
            "min": self.__fakes["voltage"]["min"],
            "max": self.__fakes["voltage"]["max"] 
        }

    # ---

    async def _PZA_DRV_BPC_read_voltage_decimals(self):
        return self.__fakes["voltage"]["decimals"]

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

