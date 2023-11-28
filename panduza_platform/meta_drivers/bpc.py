import abc
import time
import asyncio
from collections import ChainMap
from core.platform_driver import PlatformDriver

class MetaDriverBpc(PlatformDriver):
    """ Abstract Driver with helper class to manage power supply interface
    """

    # =============================================================================
    # PLATFORM DRIVERS FUNCTIONS

    def _PZA_DRV_config(self):
        """Driver base configuration
        """
        base = {
            "info": {
                "type": "bpc",
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

    async def _PZA_DRV_BPC_read_voltage_value(self):
        """Must get the voltage value value on the BPC and return it
        """
        raise NotImplementedError("Must be implemented !")

    async def _PZA_DRV_BPC_write_voltage_value(self, v):
        """Must set *v* as the new voltage value value on the BPC
        """
        raise NotImplementedError("Must be implemented !")

    async def _PZA_DRV_BPC_voltage_value_min_max(self):
        """Must return the voltage value range of the power supply
        """
        return {"min": 0, "max": 0 }

    async def _PZA_DRV_BPC_read_voltage_decimals(self):
        """Must return the number of decimals supported for the voltage
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
            "voltage": self.__handle_cmds_set_voltage,
            "current": self.__handle_cmds_set_current,
            # "settings": self.__handle_cmds_set_settings,
        }

        # First update
        await self.__update_attribute_initial()

        # Polling cycle reset
        start_time = time.perf_counter()
        self.polling_ref = {
            "enable": start_time,
            "voltage" : start_time,
            "current"  : start_time,
        }

        # Start polling task
        self.load_worker_task(self.__polling_task_att_enable())
        self.load_worker_task(self.__polling_task_att_voltage())
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

    async def __set_poll_cycle_voltage(self, v):
        self.polling_ref["voltage"] = v

    async def __get_poll_cycle_voltage(self):
        return self.polling_ref["voltage"]

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

    async def __polling_task_att_voltage(self):
        """Task to poll the value
        """
        while self.alive:
            await asyncio.sleep(self.polling_ref["voltage"])
            await self._update_attributes_from_dict({
                "voltage": {
                    "value": await self._PZA_DRV_BPC_read_voltage_value()
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
        await self.__att_voltage_full_update()
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

    async def __handle_cmds_set_voltage(self, cmd_att):
        """Manage voltage commands
        """
        update_obj = {}
        
        # TODO
        # if self._get_field("voltage", "min") <= v <= self._get_field("voltage", "max"):
                
        await self._prepare_update(update_obj, 
                            "voltage", cmd_att,
                            "value", [float, int]
                            , self._PZA_DRV_BPC_write_voltage_value
                            , self._PZA_DRV_BPC_read_voltage_value)
        
        await self._prepare_update(update_obj, 
                            "voltage", cmd_att,
                            "polling_cycle", [float, int]
                            , self.__set_poll_cycle_voltage
                            , self.__get_poll_cycle_voltage)
        
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

    async def __att_voltage_full_update(self):
        """
        """
        min_max = await self._PZA_DRV_BPC_voltage_value_min_max()
        await self._update_attributes_from_dict({
            "voltage": {
                "min": min_max.get("min", 0),
                "max": min_max.get("max", 0),
                "value": await self._PZA_DRV_BPC_read_voltage_value(),
                "decimals": await self._PZA_DRV_BPC_read_voltage_decimals(),
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

