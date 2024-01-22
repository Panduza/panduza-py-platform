from hamcrest import assert_that, has_key, instance_of
import asyncio
from meta_drivers.bpc import MetaDriverBpc
from connectors.serial_tty import ConnectorSerialTty

VOLTAGE_BOUNDS     = { "min": 0, "max": 30 }
CURRENT_BOUNDS      = { "min": 0, "max": 5 }

COMMAND_TIME_LOCK=0.1

class InterfaceKoradKa3005pBPC(MetaDriverBpc):

    # ---

    def __init__(self, name=None, settings={}) -> None:
        """Constructor
        """
        self.settings = settings
        super().__init__(name=name)

    # ---

    def _PZA_DRV_BPC_config(self):
        """
        """
        return {
            "name": "korad.ka3005p.bpc",
            "description": "Power Supply KA3005P from Korad"
        }

    # ---

    async def _PZA_DRV_loop_init(self):
        """Driver initialization
        """
        # Get the Serial Connector
        self.serial_connector = await ConnectorSerialTty.Get(**self.settings)
        
        # 
        self.channel = 1
        
        # Call meta class BPC ini
        await super()._PZA_DRV_loop_init()

    ###########################################################################
    ###########################################################################

    async def _PZA_DRV_BPC_read_enable_value(self):
        # await asyncio.sleep(1)
        status = await self.serial_connector.write_and_read_during(f"STATUS?", time_lock_s=COMMAND_TIME_LOCK, read_duration_s=0.1)

        return bool(status[0] & (1 << 6))

    async def _PZA_DRV_BPC_write_enable_value(self, v):
        await self.serial_connector.write("OUT{}".format(int(v)), time_lock_s=COMMAND_TIME_LOCK)

    # ---

    async def _PZA_DRV_BPC_read_voltage_value(self):
        voltage = await self.serial_connector.write_and_read_during(f"VSET{self.channel}?\n", time_lock_s=COMMAND_TIME_LOCK, read_duration_s=0.1)
        return float(voltage)

    async def _PZA_DRV_BPC_write_voltage_value(self, v):
        await self.serial_connector.write("VSET1:{:05.2f}".format(v), time_lock_s=COMMAND_TIME_LOCK)

    async def _PZA_DRV_BPC_voltage_value_min_max(self):
        return VOLTAGE_BOUNDS
    
    async def _PZA_DRV_BPC_read_voltage_decimals(self):
        return 2

    # ---

    async def _PZA_DRV_BPC_read_current_value(self):
        current = await self.serial_connector.write_and_read_during(f"ISET{self.channel}?\n", time_lock_s=COMMAND_TIME_LOCK, read_duration_s=0.1)
        return float(current[0:5])

    async def _PZA_DRV_BPC_write_current_value(self, v):
        await self.serial_connector.write("ISET1:{:05.3f}".format(v), time_lock_s=COMMAND_TIME_LOCK)
        
    async def _PZA_DRV_BPC_current_value_min_max(self):
        return CURRENT_BOUNDS

    async def _PZA_DRV_BPC_read_current_decimals(self):
        return 3


