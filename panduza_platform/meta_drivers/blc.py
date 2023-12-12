import abc
import time
import asyncio
from collections import ChainMap
from core.platform_driver import PlatformDriver

class MetaDriverBlc(PlatformDriver):
    """Abstract Driver with helper class to manage Bench Laser Control interfaces
    """

    # =============================================================================
    # PLATFORM DRIVERS FUNCTIONS

    def _PZA_DRV_config(self):
        """Driver base configuration
        """
        base = {
            "info": {
                "type": "blc",
                "version": "0.0"
            }
        }
        return base
    
    # =============================================================================
    # TO OVERRIDE IN DRIVER

    # ---

    async def _PZA_DRV_BPC_read_enable_value(self):
        """Must get the state value on the BPC and return it
        """
        raise NotImplementedError("Must be implemented !")

    async def _PZA_DRV_BPC_write_enable_value(self, v):
        """Must set *v* as the new state value on the BPC
        """
        raise NotImplementedError("Must be implemented !")

    # ---

    async def _PZA_DRV_BPC_read_power_value(self):
        """Must get the power value value on the BPC and return it
        """
        raise NotImplementedError("Must be implemented !")

    async def _PZA_DRV_BPC_write_power_value(self, v):
        """Must set *v* as the new power value value on the BPC
        """
        raise NotImplementedError("Must be implemented !")

    async def _PZA_DRV_BPC_power_value_min_max(self):
        """Must return the power value range of the power supply
        """
        return {"min": 0, "max": 0 }

    async def _PZA_DRV_BPC_read_power_decimals(self):
        """Must return the number of decimals supported for the power
        """
        raise NotImplementedError("Must be implemented !")

    # ---

    async def _PZA_DRV_BPC_read_current_value(self):
        """Must get the current value value on the BPC and return it
        """
        raise NotImplementedError("Must be implemented !")

    async def _PZA_DRV_BPC_write_current_value(self, v):
        """Must set *v* as the new current value value on the BPC
        """
        raise NotImplementedError("Must be implemented !")

    async def _PZA_DRV_BPC_current_value_min_max(self):
        """Must return the current range of the power supply
        """
        return {"min": 0, "max": 0 }

    async def _PZA_DRV_BPC_read_current_decimals(self):
        """Must return the number of decimals supported for the amperage
        """
        raise NotImplementedError("Must be implemented !")

    ###########################################################################
    ###########################################################################
    #
    # FOR SUBCLASS USE ONLY
    #
    ###########################################################################
    ###########################################################################

    # ---

    async def _PZA_DRV_loop_init(self):
        # Set command handlers
        self.__cmd_handlers = {
            "enable": self.__handle_cmds_set_enable,
            "power": self.__handle_cmds_set_power,
            "current": self.__handle_cmds_set_current,
            # "settings": self.__handle_cmds_set_settings,
        }

        # First update
        await self.__update_attribute_initial()

        # Polling cycle reset
        start_time = time.perf_counter()
        self.polling_ref = {
            "enable": start_time,
            "power" : start_time,
            "current"  : start_time,
        }

        # Start polling task
        self.load_worker_task(self.__polling_task_att_enable())
        self.load_worker_task(self.__polling_task_att_power())
        self.load_worker_task(self.__polling_task_att_current())

        # Init success, the driver can pass into the run mode
        self._PZA_DRV_init_success()

    # ---

    async def _PZA_DRV_cmds_set(self, payload):
        """From MetaDriver
        """
        cmds = self.payload_to_dict(payload)
        # self.log.debug(f"cmds as json : {cmds}")
        for att in self.__cmd_handlers:
            if att in cmds:
                await self.__cmd_handlers[att](cmds[att])

    # =============================================================================
    # PRIVATE FUNCTIONS

    # ---

    async def __set_poll_cycle_enable(self, v):
        self.polling_ref["enable"] = v

    async def __get_poll_cycle_enable(self):
        return self.polling_ref["enable"]

    # ---

    async def __set_poll_cycle_power(self, v):
        self.polling_ref["power"] = v

    async def __get_poll_cycle_power(self):
        return self.polling_ref["power"]

    # ---

    async def __set_poll_cycle_current(self, v):
        self.polling_ref["current"] = v

    async def __get_poll_cycle_current(self):
        return self.polling_ref["current"]

    # ---

    async def __polling_task_att_enable(self):
        """Task to poll the value
        """
        while self.alive:
            await asyncio.sleep(self.polling_ref["enable"])
            await self._update_attributes_from_dict({
                "enable": {
                    "value": await self._PZA_DRV_BPC_read_enable_value()
                }
            })

    # ---

    async def __polling_task_att_power(self):
        """Task to poll the value
        """
        while self.alive:
            await asyncio.sleep(self.polling_ref["power"])
            await self._update_attributes_from_dict({
                "power": {
                    "value": await self._PZA_DRV_BPC_read_power_value()
                }
            })

    # ---

    async def __polling_task_att_current(self):
        """Task to poll the value
        """
        while self.alive:
            await asyncio.sleep(self.polling_ref["current"])
            await self._update_attributes_from_dict({
                "current": {
                    "value": await self._PZA_DRV_BPC_read_current_value()
                }
            })

    # ---

    async def __update_attribute_initial(self):
        """
        """
        await self.__att_enable_full_update()
        await self.__att_power_full_update()
        await self.__att_current_full_update()

    # ---

    async def __handle_cmds_set_enable(self, cmd_att):
        """Manage output enable commands
        """
        update_obj = {}
        await self._prepare_update(update_obj, 
                            "enable", cmd_att,
                            "value", [bool]
                            , self._PZA_DRV_BPC_write_enable_value
                            , self._PZA_DRV_BPC_read_enable_value)
        await self._prepare_update(update_obj, 
                            "enable", cmd_att,
                            "polling_cycle", [float, int]
                            , self.__set_poll_cycle_enable
                            , self.__get_poll_cycle_enable)
        await self._update_attributes_from_dict(update_obj)

    # ---

    async def __handle_cmds_set_power(self, cmd_att):
        """Manage power commands
        """
        update_obj = {}
        
        # TODO
        # if self._get_field("power", "min") <= v <= self._get_field("power", "max"):
                
        await self._prepare_update(update_obj, 
                            "power", cmd_att,
                            "value", [float, int]
                            , self._PZA_DRV_BPC_write_power_value
                            , self._PZA_DRV_BPC_read_power_value)
        
        await self._prepare_update(update_obj, 
                            "power", cmd_att,
                            "polling_cycle", [float, int]
                            , self.__set_poll_cycle_power
                            , self.__get_poll_cycle_power)
        
        await self._update_attributes_from_dict(update_obj)

    # ---

    async def __handle_cmds_set_current(self, cmd_att):
        """Manage ampere commands
        """
        update_obj = {}
        
        # TODO
        # if self._get_field("current", "min") <= v <= self._get_field("current", "max"):
                
        await self._prepare_update(update_obj, 
                            "current", cmd_att,
                            "value", [float, int]
                            , self._PZA_DRV_BPC_write_current_value
                            , self._PZA_DRV_BPC_read_current_value)
        
        await self._prepare_update(update_obj, 
                            "current", cmd_att,
                            "polling_cycle", [float, int]
                            , self.__set_poll_cycle_current
                            , self.__get_poll_cycle_current)
        
        await self._update_attributes_from_dict(update_obj)

    # ---

    async def __att_enable_full_update(self):
        """
        """
        await self._update_attributes_from_dict({
            "enable": {
                "value": await self._PZA_DRV_BPC_read_enable_value(),
                "polling_cycle": 1
            }
        })

    # ---

    async def __att_power_full_update(self):
        """
        """
        min_max = await self._PZA_DRV_BPC_power_value_min_max()
        await self._update_attributes_from_dict({
            "power": {
                "min": min_max.get("min", 0),
                "max": min_max.get("max", 0),
                "value": await self._PZA_DRV_BPC_read_power_value(),
                "decimals": await self._PZA_DRV_BPC_read_power_decimals(),
                "polling_cycle": 1
            }
        })

    # ---

    async def __att_current_full_update(self):
        """
        """
        min_max = await self._PZA_DRV_BPC_current_value_min_max()
        await self._update_attributes_from_dict({
            "current": {
                "min": min_max.get("min", 0),
                "max": min_max.get("max", 0),
                "value": await self._PZA_DRV_BPC_read_current_value(),
                "decimals": await self._PZA_DRV_BPC_read_current_decimals(),
                "polling_cycle": 1
            }
        })

