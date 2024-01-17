import asyncio
from meta_drivers.powermeter import MetaDriverPowermeter

from connectors.usbtmc import ConnectorUsbtmc

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

        # settings = tree.get("settings", {})
        # self.log.info(settings)
        self.usbtmc = ConnectorUsbtmc.Get(**self.settings)

        self.platform.load_task(self.__increment_task())

        self.__fakes = {
            "measure": {
                "value": 0
            }
        }

        # Call meta class BPC ini
        await super()._PZA_DRV_loop_init()

    # ---

    async def _PZA_DRV_POWERMETER_read_measure_value(self):
        return self.__fakes["measure"]["value"]

    # ---

    async def __increment_task(self):
        while self.alive:
            await asyncio.sleep(0.2)
            self.__fakes["measure"]["value"] += 0.001
