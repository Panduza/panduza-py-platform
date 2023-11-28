import abc
import json
import time
import inspect
import asyncio
from collections import ChainMap
from core.platform_driver import PlatformDriver

class MetaDriverDio(PlatformDriver):

    # =============================================================================
    # PLATFORM DRIVERS FUNCTIONS

    def _PZA_DRV_config(self):
        """Driver base configuration
        """
        base = {
            "info": {
                "type": "dio",
                "version": "0.0"
            }
        }
        return ChainMap(base, self._PZA_DRV_DIO_config())

    # ---

    async def _PZA_DRV_loop_init(self):
        """From PlatformDriver
        """
        # Set handers
        self.__cmd_handlers = {
            "direction" : self.__handle_cmds_set_direction,
            "state" : self.__handle_cmds_set_state,
        }

        self.__polling_cycle = 1

        # first update
        await self.__update_attribute_initial()

        # trigger for polling task
        self.trigger = False

        # Init Success
        await super()._PZA_DRV_loop_init()

    # ---

    async def _PZA_DRV_loop_run(self, loop):
        # polls
        
        # await self.__poll_att_state()
        # await asyncio.sleep(5)
        # await self.__poll_att_direction()
        # await asyncio.sleep(5)

        await self.__poll_trigger()
        

    # ---

    async def _PZA_DRV_cmds_set(self, payload):
        cmds = self.payload_to_dict(payload)
        self.log.debug(f"cmds as json : {cmds}")
        for att in self.__cmd_handlers:
            if att in cmds:
                await self.__cmd_handlers[att](cmds[att])
        
        self.trigger = True
        
                


    # =============================================================================
    # TO OVERRIDE IN DRIVER

    # ---

    def _PZA_DRV_DIO_config(self):
        """Driver base configuration
        """
        file_name = inspect.stack()[0][1]
        function_name = inspect.stack()[0][3]
        raise NotImplementedError(f"Function not implemented ! '{function_name}' => %{file_name}%")

    # ---

    async def _PZA_DRV_DIO_get_direction_value(self):
        """ get value of direction value
        """
        file_name = inspect.stack()[0][1]
        function_name = inspect.stack()[0][3]
        raise NotImplementedError(f"Function not implemented ! '{function_name}' => %{file_name}%")

    # ---

    async def _PZA_DRV_DIO_set_direction_value(self, value):
        """ set value of direction value

        -  Args
            value : value to be set : in or out
        """
        file_name = inspect.stack()[0][1]
        function_name = inspect.stack()[0][3]
        raise NotImplementedError(f"Function not implemented ! '{function_name}' => %{file_name}%")

    # ---

    async def _PZA_DRV_DIO_get_direction_pull(self):
        """ get direction pull
        """
        file_name = inspect.stack()[0][1]
        function_name = inspect.stack()[0][3]
        raise NotImplementedError(f"Function not implemented ! '{function_name}' => %{file_name}%")

    # ---

    async def _PZA_DRV_DIO_set_direction_pull(self, v):
        """ set the pull direction
        -Args
        value : value to be set : up, down or open
        """
        file_name = inspect.stack()[0][1]
        function_name = inspect.stack()[0][3]
        raise NotImplementedError(f"Function not implemented ! '{function_name}' => %{file_name}%")

    # ---

    async def _PZA_DRV_DIO_get_state_active(self):
        """ get the active state
        """
        file_name = inspect.stack()[0][1]
        function_name = inspect.stack()[0][3]
        raise NotImplementedError(f"Function not implemented ! '{function_name}' => %{file_name}%")

    # ---

    async def _PZA_DRV_DIO_set_state_active(self,v):
        """ get the active state
        -Args
        value : value to be set : True or False
        """
        file_name = inspect.stack()[0][1]
        function_name = inspect.stack()[0][3]
        raise NotImplementedError(f"Function not implemented ! '{function_name}' => %{file_name}%")

    # ---

    async def _PZA_DRV_DIO_get_state_activeLow(self):
        """ get the active low state
        """
        file_name = inspect.stack()[0][1]
        function_name = inspect.stack()[0][3]
        raise NotImplementedError(f"Function not implemented ! '{function_name}' => %{file_name}%")

    # ---

    async def _PZA_DRV_DIO_set_state_activeLow(self,v):
        """ set the active low state
            -Args
            value : value to be set : True or False
        """
        file_name = inspect.stack()[0][1]
        function_name = inspect.stack()[0][3]
        raise NotImplementedError(f"Function not implemented ! '{function_name}' => %{file_name}%")

    # =============================================================================
    # PRIVATE FUNCTIONS

    # ---

    async def __update_attribute_initial(self):
        """Function to perform the initial init
        """
        await self.__att_direction_full_update()
        await self.__att_state_full_update()


    # ---

    async def __handle_cmds_set_direction(self, cmd_att):
        """
        """
        update_obj = {}
        await self._prepare_update(update_obj, 
                            "direction", cmd_att,
                            "value", [str]
                            , self._PZA_DRV_DIO_set_direction_value
                            , self._PZA_DRV_DIO_get_direction_value)
        await self._prepare_update(update_obj, 
                            "direction", cmd_att,
                            "pull", [str]
                            , self._PZA_DRV_DIO_set_direction_pull
                            , self._PZA_DRV_DIO_get_direction_pull)
        await self._update_attributes_from_dict(update_obj)

    # ---

    async def __handle_cmds_set_state(self, cmd_att):
        """
        """
        update_obj = {}
        await self._prepare_update(update_obj, 
                            "state", cmd_att,
                            "active", [bool]
                            , self._PZA_DRV_DIO_set_state_active
                            , self._PZA_DRV_DIO_get_state_active)
        await self._prepare_update(update_obj, 
                            "state", cmd_att,
                            "active_low", [bool]
                            , self._PZA_DRV_DIO_set_state_activeLow
                            , self._PZA_DRV_DIO_get_state_activeLow)
        await self._update_attributes_from_dict(update_obj)

    # ---

    async def __att_direction_full_update(self):
        """Just update all field of direction
        """
        await self._update_attributes_from_dict({
            "direction": {
                "value": await self._PZA_DRV_DIO_get_direction_value(),
                "pull": await self._PZA_DRV_DIO_get_direction_pull(),
                "polling_cycle": 1
            }
        })

    # ---

    async def __att_state_full_update(self):
        """Just update all field of direction
        """
        await self._update_attributes_from_dict({
            "state": {
                "active": await self._PZA_DRV_DIO_get_state_active(),
                "active_low": await self._PZA_DRV_DIO_get_state_activeLow(),
                "polling_cycle": 1
            }
        })

    
    async def __poll_trigger(self):
        
        if self.trigger:
            
            # v = await self._PZA_DRV_DIO_get_state_active()
            # w = await self._PZA_DRV_DIO_get_state_activeLow()
            # x = await self._PZA_DRV_DIO_get_direction_pull()
            # y = await self._PZA_DRV_DIO_get_direction_value()

            # await self._update_attribute("state", "active", v, 'always') 
            # await self._update_attribute("state", "active_low", w, 'always') 
            # await self._update_attribute("direction", "pull", x, 'always') 
            # await self._update_attribute("direction", "value", y, 'always') 

            await self.__update_attribute_initial()

            self.trigger = False



    # async def __poll_att_state(self):
        
    #     polling_cycle = float(self._get_field("state", "polling_cycle"))
        
    #     if polling_cycle < 0:
    #         return
    #     if (time.perf_counter() - self.__polling_cycle) > polling_cycle:
    #         p = False
    #         p = await self._update_attribute("state", "active_low", await self._PZA_DRV_DIO_get_state_activeLow(), 'always') or p
    #         p = await self._update_attribute("state", "active", await self._PZA_DRV_DIO_get_state_active(), 'always') or p

    #     self.__polling_cycle = time.perf_counter()
           

    
    # async def __poll_att_direction(self):

    #     polling_cycle = float(self._get_field("direction", "polling_cycle"))
        
    #     if polling_cycle < 0:
    #         return
    #     if (time.perf_counter() - self.__polling_cycle) > polling_cycle:
    #         p = False
    #         p = await self._update_attribute("direction", "pull", await self._PZA_DRV_DIO_get_direction_pull(), False) or p
    #         p = await self._update_attribute("direction", "value", await self._PZA_DRV_DIO_get_direction_value(), False) or p

    #         if p:
    #             await self._push_attribute("direction")
    #         self.__polling_cycle = time.perf_counter()
            


    
