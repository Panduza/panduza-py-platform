from meta_drivers.spi_master import MetaDriverSpiMaster
from ...connectors.spi_master_ftdi import ConnectorSPIMasterFTDI
from connectors.udev_tty import HuntUsbDevs
from collections import ChainMap

class DriverFtdiSpiMaster(MetaDriverSpiMaster):
    """
    Driver for drive SPI master
    """

    ###########################################################################
    ###########################################################################

    # must match with tree.json content
    def _PZA_DRV_config(self):
        # Extend the common bpc config
        return ChainMap(
            super()._PZA_DRV_config(),
            {
                "name": "FTDI_spi_master",
                "description": "SPI master over FTDI chip",
                "compatible": ["ftdi_spi_master", "py.ftdi_spi_master"],
            },
        )

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_loop_init(self):
        # self.log.debug(f"{tree}")
        settings = tree["settings"]

        # Get the connector
        self.spi_connector = ConnectorSPIMasterFTDI.Get(**settings)

        super()._PZA_DRV_loop_init(tree)

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_hunt_instances(self):
        instances = [] # ConnectorSPIMasterFTDI.hunt()

        # 0403:6001 Future Technology Devices International, Ltd FT232 Serial (UART) IC
        # 0403:e0d0 Future Technology Devices International, Ltd Total Phase Aardvark I2C/SPI Host Adapter
        # note: also detect aardvark probe
        FTDI_UART_VENDOR = "0403"
        usb_pieces = HuntUsbDevs(vendor=FTDI_UART_VENDOR, subsystem="usb")
        for p in usb_pieces:
            iss = p.get("ID_SERIAL_SHORT")
            instances.append(
                MetaDriverSpiMaster.__tgen(
                    "py.ftdi_spi_master",
                    FTDI_UART_VENDOR,
                    p.get("ID_MODEL_ID", "DEVICE ID NOT AVAILABLE"),
                    iss,
                    iss,
                )
            )

        return instances


    ###########################################################################
    ###########################################################################

    def _PZA_DRV_loop_run(self, loop):
        """ """
        pass

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_loop_err(self):
        """ """
        pass

    ###########################################################################
    ###########################################################################
    
    def _PZA_DRV_SPIM_transfer(self, data):
        return self.spi_connector.transfer(data, len(data))