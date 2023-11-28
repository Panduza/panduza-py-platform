import abc
from collections import ChainMap
from core.platform_driver import PlatformDriver

class MetaDriverRelay(PlatformDriver):
    """
    """

    # =============================================================================
    # PLATFORM DRIVERS FUNCTIONS

    def _PZA_DRV_config(self):
        """Driver base configuration
        """
        base = {
            "info": {
                "type": "relay",
                "version": "0.0"
            }
        }
        return ChainMap(base, self._PZA_DRV_RELAY_config())

    # ---

    async def _PZA_DRV_loop_init(self):
        """From PlatformDriver
        """
        # Set handers
        self.__cmd_handlers = {
            "state" : self.__handle_cmds_set_state
        }

        # first update
        await self.__update_attribute_initial()

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

    @abc.abstractmethod
    def _PZA_DRV_RELAY_config(self):
        """Driver base configuration
        """
        pass

    # ---

    @abc.abstractmethod
    async def _PZA_DRV_RELAY_read_state_open(self):
        """
        """
        pass

    # ---

    @abc.abstractmethod
    async def _PZA_DRV_RELAY_write_state_open(self, value):
        """
        """
        pass

    # =============================================================================
    # PRIVATE FUNCTIONS

    # ---

    async def __update_attribute_initial(self):
        """Function to perform the initial init
        """
        await self.__att_state_full_update()

    # ---

    async def __handle_cmds_set_state(self, cmd_att):
        """
        """
        update_obj = {}
        await self._prepare_update(update_obj, 
                            "state", cmd_att,
                            "open", [bool]
                            , self._PZA_DRV_RELAY_write_state_open
                            , self._PZA_DRV_RELAY_read_state_open)
        await self._update_attributes_from_dict(update_obj)

    # ---

    async def __att_state_full_update(self):
        """
        """
        await self._update_attributes_from_dict({
            "state": {
                "open": await self._PZA_DRV_RELAY_read_state_open()
            }
        })

    # ---

