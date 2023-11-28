from hamcrest import assert_that, has_key, instance_of
from meta_drivers.dio import MetaDriverDio
from connectors.boundary_scan_ftdi import ConnectorBoundaryScanFtdi

class DriverBoundaryScanDio(MetaDriverDio):

    # =============================================================================
    # FROM MetaDriverDio

    def _PZA_DRV_DIO_config(self):
        return {
            "name": "ftdi.boudary_scan.dio",
            "description": "Virtual DIO"
        }

    # ---

    async def _PZA_DRV_loop_init(self):
        """Init function
        Reset fake parameters
        """

        # Load settings
        assert_that(tree, has_key("settings"))
        settings = tree["settings"]
        assert_that(settings, instance_of(dict))

        # Checks
        assert_that(settings, has_key("usb_vendor"))
        assert_that(settings, has_key("usb_model"))
        assert_that(settings, has_key("usb_serial_short"))
        assert_that(settings, has_key("jtag_frequency"))
        assert_that(settings, has_key("jtag_bsdl_folder"))
        assert_that(settings, has_key("pin"))
        assert_that(settings, has_key("device_number"))
        #assert_that(settings, has_key("pins_wanted"))
        

        self.pin = settings["pin"]
        self.device_number = settings["device_number"]
        
        global previous_device_number, previous_pins
        previous_device_number = self.device_number
        
        previous_pins = []
        previous_pins.append(self.pin)

        # Get the gate connector
        self.jtag_connector = await ConnectorBoundaryScanFtdi.Get(**settings)

        
        self.__fakes = {
            "direction": {
                "value": "in",
                "pull": "open"
            },
            "state": {
                "active": False,
                "active_low": False
            }
        }

        # Call meta class PSU ini
        await super()._PZA_DRV_loop_init()



    # ---

    async def _PZA_DRV_DIO_get_direction_value(self):
        """From MetaDriverDio
        """
        self.log.info(f"read direction value : {self.__fakes['direction']['value']} !")
        return self.__fakes["direction"]["value"]

    # ---

    async def _PZA_DRV_DIO_set_direction_value(self, value):
        """ set value of direction value

        -  Args
            value : value to be set : in or out
        """
        self.log.info(f"set direction value : {value}")
        self.__fakes["direction"]["value"] = value

    # ---

    async def _PZA_DRV_DIO_get_direction_pull(self):
        """ get direction pull
        """
        self.log.info(f"read direction pull : {self.__fakes['direction']['pull']}!")
        return self.__fakes["direction"]["pull"]

    # ---

    async def _PZA_DRV_DIO_set_direction_pull(self, v):
        """ set the pull direction
        -Args
        value : value to be set : up, down or open
        """
        self.log.info(f"set direction pull : {v}")
        self.__fakes["direction"]["pull"] = v

    # ---

    async def _PZA_DRV_DIO_get_state_active(self):
        """ get the active state
        """
        direction = self.__fakes["direction"]["value"]
        self.__fakes["state"]["active"] = await self.jtag_connector.async_read_pin(self.device_number,self.pin,direction)
        self.log.info(f'the state of the device {self.device_number} {self.pin} ({direction}) is {self.__fakes["state"]["active"]}')

        return self.__fakes["state"]["active"]

    # ---

    async def _PZA_DRV_DIO_set_state_active(self,v):
        """ get the active state
        -Args
        value : value to be set : True or False
        """
        global previous_device_number,previous_pins
        #self.log.info(f' 1 pre : {previous_device_number} ; mtn : {self.device_number}')
        #self.log.info(f'1 pins : {previous_pins} ')
        if (previous_device_number != self.device_number):
            for pins in previous_pins : 
                self.log.info(f'write on previous device {previous_device_number} {pins} with {not(v)}')
                await self.jtag_connector.async_write_pin(int(previous_device_number),pins,not(v))
            previous_pins.clear()


        #self.log.info(f'2 pins : {previous_pins} ')
        self.log.info(f'write on device {self.device_number} {self.pin} with {v}')
        self.__fakes["state"]["active"] = v
        
        active_low = self.__fakes["state"]["active_low"]
        pin_value = not v if active_low else v
        await self.jtag_connector.async_write_pin(int(self.device_number), self.pin, pin_value)
      
        previous_device_number = self.device_number
        if self.pin not in previous_pins :
            previous_pins.append(self.pin)

        #self.log.info(f'2 pre : {previous_device_number} ; mtn : {self.device_number}')
        #self.log.info(f'3 pins : {previous_pins} ')
        

    # ---

    async def _PZA_DRV_DIO_get_state_activeLow(self):
        """ get the active low state
        """
        self.log.info(f"read state active low : {self.__fakes['state']['active_low']}!")
        return self.__fakes["state"]["active_low"]

    # ---

    async def _PZA_DRV_DIO_set_state_activeLow(self,v):
        """
        """
        self.log.info(f"set state active low : {v}")
        self.__fakes["state"]["active_low"] = v

   
   




