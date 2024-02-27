import asyncio
from core.platform_driver import PlatformDriver

class InterfacePanduzaPlatform(PlatformDriver):
    """
    """

    def _PZA_DRV_config(self):
        """From PlatformDriver
        """
        return {
            "info": {
                "type": "platform",
                "version": "0.0"
            }
        }


    async def _PZA_DRV_loop_init(self):
        """From PlatformDriver
        """

        self.hunting = False

        # Set command handlers
        self.__cmd_handlers = {
            "dtree": self.__handle_cmds_set_dtree,
            "devices": self.__handle_cmds_set_devices,
        }

        # Append a task to refresh platform data
        self.load_worker_task(self.__refresh_platform_data_task())


        # status
            # state => string
            # report => json

        await self._update_attribute("info", "dying_gasp", False)


        # devices

        # Tell the platform that the init state end sucessfuly
        self._PZA_DRV_init_success()

    # ---

    async def _PZA_DRV_cmds_set(self, payload):
        """From MetaDriver
        """
        cmds = self.payload_to_dict(payload)
        for att in self.__cmd_handlers:
            if att in cmds:
                await self.__cmd_handlers[att](cmds[att])

   # ---
    
    async def _PZA_DRV_dying_gasp(self):
        # [REQ_ITF_PLATFORM_0020_00] - Info 'dying_gasp' field
        await self._update_attribute("info", "dying_gasp", True)

    # ---

    async def __refresh_platform_data_task(self):
        """Refresh important data count
        """
        while self.alive:
            await asyncio.sleep(1)

            await self._update_attribute("info", "interfaces", self.platform.get_number_of_interfaces())

            await self._update_attributes_from_dict({
                "info": {
                    "number_of_devices": self.platform.get_number_of_device(),
                }
            })

            await self._update_attributes_from_dict({
                "dtree": {
                    "name": "tree.json",
                    "saved": True,
                    "list": [],
                    "content": self.platform.dtree,
                }
            })

            await self._update_attributes_from_dict({
                "devices": {
                    "hunting": False,
                    "max": 0,
                    "hunted": 0,
                    "store": self.platform.device_factory.get_devices_store(),
                }
            })

    # ---

    async def __handle_cmds_set_dtree(self, cmd_att):
        """
        """
        update_obj = {}
        self.log.info(cmd_att)

        await self._prepare_update(update_obj, 
                            "dtree", cmd_att,
                            "content", [dict]
                            , self.__set_config_content
                            , self.__get_config_content)
        
        # await self._prepare_update(update_obj, 
        #                     "enable", cmd_att,
        #                     "polling_cycle", [float, int]
        #                     , self.__set_poll_cycle_enable
        #                     , self.__get_poll_cycle_enable)
        await self._update_attributes_from_dict(update_obj)

    # ---

    async def __set_config_content(self, value):
        self.log.info(value)
        await self.platform.load_config_content_task(value)

    # ---

    async def __get_config_content(self):
        return self.platform.dtree

    # ---

    async def __handle_cmds_set_devices(self, cmd_att):
        """
        """
        update_obj = {}
        self.log.info(cmd_att)

        await self._prepare_update(update_obj, 
                            "devices", cmd_att,
                            "hunting", [bool]
                            , self.__set_device_hunting
                            , self.__get_device_hunting)
        
        # await self._prepare_update(update_obj, 
        #                     "enable", cmd_att,
        #                     "polling_cycle", [float, int]
        #                     , self.__set_poll_cycle_enable
        #                     , self.__get_poll_cycle_enable)



        await self._update_attributes_from_dict(update_obj)

    # ---

    async def __set_device_hunting(self, value):
        self.log.info(value)

        if value == True:
            if self.hunting:
                pass
                # already hunting
            else:
                self.hunting = True
                self.platform.load_task(self.hunt_task())
        else:
            # stop hunting
            self.log.warning("stop huntin not implemented")

    # ---

    async def __get_device_hunting(self):
        return self.hunting

    # ---

    async def hunt_task(self):
        print("!!!!!!!!!!!!!! HUNT !!!!!!!!!!!!!!!")
        await self.platform.device_factory.hunt_start()
        while True:
            has_next = await self.platform.device_factory.hunt_next()
            if not has_next:
                break
        self.hunting = False

        await self._update_attributes_from_dict({
                "devices": {
                    "hunting": self.hunting,
                    "max": self.platform.device_factory.get_number_of_drivers(),
                    "hunted": 1,
                    "store": self.platform.device_factory.get_devices_store(),
                }
            })
        print(f"!!!!!!!!!!!!!! HUNT !!!!!!!!!!!!!!!")


