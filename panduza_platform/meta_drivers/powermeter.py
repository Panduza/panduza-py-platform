import abc
import time
import asyncio
import inspect
from collections import ChainMap
from core.platform_driver import PlatformDriver

class MetaDriverPowermeter(PlatformDriver):
    """Abstract Driver with helper class to manage PowerMeter interface
    """

    # =============================================================================
    # PLATFORM DRIVERS FUNCTIONS

    def _PZA_DRV_config(self):
        """Driver base configuration
        """
        base = {
            "info": {
                "type": "powermeter",
                "version": "0.0"
            }
        }
        return base

    # ---

    async def _PZA_DRV_loop_init(self):
        """From PlatformDriver
        """
        # Set handers
        self.__cmd_handlers = {
            "measure" : self.__handle_cmds_set_measure
        }

        # 
        self.__polling_cycle = 1

        # first update
        await self.__update_attribute_initial()

        # Start polling task
        self.platform.load_task(self.__polling_task())

        # Init Success
        await super()._PZA_DRV_loop_init()

    # ---

    async def _PZA_DRV_cmds_set(self, payload):
        cmds = self.payload_to_dict(payload)
        # self.log.debug(f"cmds as json : {cmds}")
        for att in self.__cmd_handlers:
            if att in cmds:
                await self.__cmd_handlers[att](cmds[att])

    # =============================================================================
    # TO OVERRIDE IN DRIVER

    # ---

    async def _PZA_DRV_POWERMETER_read_measure_value(self):
        """
        """
        file_name = inspect.stack()[0][1]
        function_name = inspect.stack()[0][3]
        raise NotImplementedError(f"Function not implemented ! '{function_name}' => %{file_name}%")

    # =============================================================================
    # PRIVATE FUNCTIONS

    # ---

    async def __polling_task(self):
        """Task to poll the value
        """
        while self.alive:
            await asyncio.sleep(self.__polling_cycle)
            await self._update_attributes_from_dict({
                "measure": {
                    "value": await self._PZA_DRV_POWERMETER_read_measure_value()
                }
            })

    # ---

    async def __update_attribute_initial(self):
        """Function to perform the initial init
        """
        await self.__att_measure_full_update()

    # ---

    async def __handle_cmds_set_measure(self, cmd_att):
        """
        """
        update_obj = {}
        await self._prepare_update(update_obj, 
                            "measure", cmd_att,
                            "polling_cycle", [float, int]
                            , self.__set_poll_cycle
                            , self.__get_poll_cycle)
        await self._update_attributes_from_dict(update_obj)

    # ---

    async def __set_poll_cycle(self, v):
        self.__polling_cycle = v

    # ---

    async def __get_poll_cycle(self):
        return self.__polling_cycle

    # ---

    async def __att_measure_full_update(self):
        """
        """
        await self._update_attributes_from_dict({
            "measure": {
                "value": await self._PZA_DRV_POWERMETER_read_measure_value(),
                "polling_cycle": await self.__get_poll_cycle()
            }
        })

    # ---

