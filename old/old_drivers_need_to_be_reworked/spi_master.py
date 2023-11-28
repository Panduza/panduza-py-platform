from ..meta_driver import MetaDriver
from ..connectors.spi_master_ftdi import ConnectorSPIMasterFTDI
from ..connectors.spi_master_aardvark import ConnectorSPIMasterAardvark
from connectors.udev_tty import HuntUsbDevs


class MetaDriverSpiMaster(MetaDriver):
    """
    Driver for drive SPI master
    """

    ###########################################################################
    ###########################################################################

    # must match with tree.json content
    def _PZA_DRV_config(self):
        return {
            "name": "GenericSPIMaster",
            "description": "Generic Spi master interface",
            "info": {"type": "spi_master", "version": "0.1"},
        }

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_loop_init(self):
        self.__cmd_handlers = {"transfer": self.__handle_cmd_transfer}

        self._PZA_DRV_init_success()

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_hunt_instances(self):
        raise NotImplementedError("Must be implemented !")

    def __tgen(driver, vendor, model, serial_short, name_suffix):
        return {
            "name": "spi:" + name_suffix,
            "driver": driver,
            "settings": {
                "vendor": vendor,
                "model": model,
                "serial_short": serial_short,
            },
        }

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_loop_run(self, loop):
        """ """
        raise NotImplementedError("Must be implemented !")

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_loop_err(self):
        """ """
        raise NotImplementedError("Must be implemented !")

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_cmds_set(self, payload):
        """From MetaDriver"""
        cmds = self.payload_to_dict(payload)
        for att in self.__cmd_handlers:
            if att in cmds:
                self.__cmd_handlers[att](cmds[att])

    ###########################################################################
    ###########################################################################

    def __handle_cmd_transfer(self, cmd_att):
        """
        Command handler for the write function
        Called when the user writes in the write attribute
        """
        self.log.debug(f"CMD_ATT = {cmd_att}")
        if "tx" in cmd_att:
            values = cmd_att["tx"]
            try:
                # TODO give the cs to the spi write
                read_values = self._PZA_DRV_SPIM_transfer(values)
                self.log.debug("update")
                self._update_attribute("transfer", "rx", list(read_values), push='always')
            except Exception as e:
                self.log.error(f"{e}")

    def _PZA_DRV_SPIM_transfer(self, data):
        """
        default behavior: return the write data as data read
        """
        return data
        