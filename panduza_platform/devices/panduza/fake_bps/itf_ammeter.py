import asyncio
from meta_drivers.ammeter import MetaDriverAmmeter


class InterfacePanduzaFakeAmmeter(MetaDriverAmmeter):
    """Fake Ammeter driver
    """

    # ---

    async def _PZA_DRV_loop_init(self):
        """Init function
        Reset fake parameters
        """

        # settings = tree.get("settings", {})
        # self.log.info(settings)

        # work_with_fake_bpc = settings.get("work_with_fake_bpc", None)
        # self.bpc_obj = self.get_interface_instance_from_pointer(work_with_fake_bpc)

        
        self.platform.load_task(self.__increment_task())


        self.__fakes = {
            "measure": {
                "value": 0
            }
        }

        # Call meta class BPC ini
        await super()._PZA_DRV_loop_init()

    # ---

    async def _PZA_DRV_AMMETER_read_measure_value(self):
        return self.__fakes["measure"]["value"]

    # ---

    async def __increment_task(self):
        while self.alive:
            await asyncio.sleep(0.2)
            self.__fakes["measure"]["value"] += 0.001
