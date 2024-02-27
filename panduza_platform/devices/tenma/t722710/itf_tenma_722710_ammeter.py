from hamcrest import assert_that, has_key, instance_of
import asyncio
from meta_drivers.ammeter import MetaDriverAmmeter
from connectors.serial_tty import ConnectorSerialTty

COMMAND_TIME_LOCK=0.1

class InterfaceTenma722710Ammeter(MetaDriverAmmeter):

    # ---

    def __init__(self, name=None, settings={}) -> None:
        """Constructor
        """
        self.settings = settings
        super().__init__(name=name)

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

    # ---

    async def _PZA_DRV_AMMETER_read_measure_value(self):
        current = await self.serial_connector.write_and_read_during(f"IOUT{self.channel}?\n", time_lock_s=COMMAND_TIME_LOCK, read_duration_s=0.1)
        return float(current)

    # ---

