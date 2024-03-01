import asyncio
from meta_drivers.powermeter import MetaDriverPowermeter

from connectors.thorlabs_pm100.connector import ConnectorThorlabsPM100


class InterfaceThorlabsPM100APowermeter(MetaDriverPowermeter):
    """Fake Powermeter driver
    """

    # ---

    def __init__(self, name=None, settings={}) -> None:
        """Constructor
        """
        self.settings = settings
        super().__init__(name=name)

    # ---

    async def _PZA_DRV_loop_init(self):
        """Init function
        Reset fake parameters
        """
 
        self.conn = await ConnectorThorlabsPM100.Get(**self.settings)
        # print(self.conn.read())

        # Call meta class BPC ini
        await super()._PZA_DRV_loop_init()

    # ---

    async def _PZA_DRV_POWERMETER_read_measure_value(self):
        return self.conn.read()

    # ---

    async def _PZA_DRV_POWERMETER_read_measure_decimals(self):
        """
        """
        return 5

