import io
from collections import ChainMap
from meta_drivers.serial import MetaDriverSerial
from connectors.serial_tty import ConnectorSerialTty

from connectors.udev_tty import HuntUsbDevs




class DriverSerial(MetaDriverSerial):
    """
    """
    
    ###########################################################################
    ###########################################################################

    def _PZA_DRV_config(self):
        # Extend the common bpc config
        return ChainMap(super()._PZA_DRV_config(), {
            "name": "Py_Serial",
            "description": "Generic Serial Interface",
            "compatible": [
                "serial",
                "py.serial"
            ]
        })


    def __tgen(vendor, model, serial_short, name_suffix):
        return {
            "name": "serial:" + name_suffix,
            "driver": "py.serial",
            "settings": {
                "vendor": vendor,
                "model": model,
                "serial_short": serial_short
            }
        }

    def _PZA_DRV_tree_template(self):
        return DriverSerial.__tgen(
            "USB: Vendor ID",
            "USB: Model ID",
            "USB: Short Serial ID",
            "template")

    def _PZA_DRV_hunt_instances(self):
        instances = []

        # 0403:6001 Future Technology Devices International, Ltd FT232 Serial (UART) IC
        FTDI_UART_VENDOR="0403"
        FTDI_UART_MODEL="6001"
        usb_pieces = HuntUsbDevs(vendor=FTDI_UART_VENDOR, model=FTDI_UART_MODEL, subsystem="tty")
        for p in usb_pieces:
            iss = p["ID_SERIAL_SHORT"]
            instances.append(DriverSerial.__tgen(FTDI_UART_VENDOR, FTDI_UART_MODEL, iss, iss))
        
        # 10c4:ea60 Silicon Labs CP210x UART Bridge
        SILLABS_CP210X_UART_VENDOR="10c4"
        SILLABS_CP210X_UART_MODEL="ea60"
        usb_pieces = HuntUsbDevs(vendor=SILLABS_CP210X_UART_VENDOR, model=SILLABS_CP210X_UART_MODEL, subsystem="tty")
        for p in usb_pieces:
            iss = p["ID_SERIAL_SHORT"]
            instances.append(DriverSerial.__tgen(SILLABS_CP210X_UART_VENDOR, SILLABS_CP210X_UART_MODEL, iss, iss))

        return instances

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_loop_init(self):

        # Get settings from tree and append constant settings for this device
        settings = dict() if "settings" not in tree else tree["settings"]
        settings["base_devname"] = "/dev/ttyUSB"
        
        # Get the connector
        self.serp = ConnectorSerialTty.Get(**settings)
 


        # Call meta class BPC ini
        super()._PZA_DRV_loop_init(tree)



    def _PZA_DRV_loop_run(self, loop):
        """
        """
        # Check if there is data waiting to be read
        if self.serp.get_internal_driver().in_waiting > 0:
            # Read the data
            data = self.serp.get_internal_driver().read(self.serp.get_internal_driver().in_waiting)
            self._PZA_DRV_SERIAL_data_received(data)

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_SERIAL_write(self, v):
        """
        """
        self.serp.get_internal_driver().write(v)
        

