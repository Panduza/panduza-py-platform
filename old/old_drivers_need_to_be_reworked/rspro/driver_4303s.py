import io
from collections import ChainMap
from meta_drivers.bpc import MetaDriverBpc
from connectors.serial_tty import ConnectorSerialTty

from connectors.udev_tty import HuntUsbDevs

IPS4303S_USBID_VENDOR="0403" # /!\ This is the VendorID and ProductID of the FT232 chip. Not a custome one!
IPS4303S_USBID_MODEL="6001"
IPS4303S_SERIAL_BAUDRATE=9600 # User manual indicates bullshit
IPS4303S_TTY_BASE="/dev/ttyUSB"

STATE_VALUE_ENUM = { "on": True, "off": False }
VOLTAGE_BOUNDS     = { "min": 0, "max": 30 }
CURRENT_BOUNDS      = { "min": 0, "max":  5 }


class DriverIPS4303S(MetaDriverBpc):
    """Driver for the device IPS4303S from RS Pro.

    At this time only the channel 1 is supported.
    Also note that the ProductID and VendorID returned by the BPC
    are the ones for a basic FT232RL chip.
    """
    
    ###########################################################################
    ###########################################################################

    def _PZA_DRV_config(self):
        # Extend the common bpc config
        return ChainMap(super()._PZA_DRV_config(), {
            "name": "Py_Bpc_IPS4303S",
            "description": "Power Supply IPS4303S",
            "compatible": [
                "ips4303s",
                "rspro.ips4303s",
                "bpc.rspro.ips4303s",
                "py.bpc.rspro.ips4303s"
            ]
        })

    def __tgen(serial_short, name_suffix):
        return {
            "name": "IPS4303S:" + name_suffix,
            "driver": "py.bpc.rspro.ips4303s",
            "settings": {
                "serial_short": serial_short
            }
        }

    def _PZA_DRV_tree_template(self):
        return DriverIPS4303S.__tgen("USB: Short Serial ID", "template")

    def _PZA_DRV_hunt_instances(self):
        instances = []
        usb_pieces = HuntUsbDevs(vendor=IPS4303S_USBID_VENDOR, model=IPS4303S_USBID_MODEL, subsystem="tty")
        for p in usb_pieces:
            iss = p["ID_SERIAL_SHORT"]
            instances.append(DriverIPS4303S.__tgen(iss, iss))
        return instances

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_loop_init(self):

        # Get settings from tree and append constant settings for this device
        settings = dict() if "settings" not in tree else tree["settings"]
        settings["vendor"] = IPS4303S_USBID_VENDOR
        settings["model"] = IPS4303S_USBID_MODEL
        settings["baudrate"] = IPS4303S_SERIAL_BAUDRATE
        settings["base_devname"] = IPS4303S_TTY_BASE
        
        # Get the connector
        self.serp = ConnectorSerialTty.Get(**settings)

        # TODO : Bad pratice "get_internal_driver" but used to speed up
        # https://stackoverflow.com/questions/10222788/line-buffered-serial-input
        self.io  = io.TextIOWrapper(
            self.serp.get_internal_driver(),
            encoding       = "ascii",
            newline        = None,
            line_buffering = False
        )
        self.io._CHUNK_SIZE= 1
        

        # TODO :Bad pratice with loopback variable instead of reading the value back
        self.state = "off"
        self.voltage = 0
        self.current = 0

        # Constants Fields settings
        self._PZA_DRV_BPC_update_voltage_min_max(VOLTAGE_BOUNDS["min"], VOLTAGE_BOUNDS["max"])
        self._PZA_DRV_BPC_update_current_min_max(CURRENT_BOUNDS["min"], CURRENT_BOUNDS["max"])

        # Misc
        self._PZA_DRV_BPC_update_misc("model", "IPS4303S (RS Pro)")

        # Call meta class BPC ini
        super()._PZA_DRV_loop_init(tree)


    ###########################################################################
    ###########################################################################

    def __write(self, *cmds):
        # Append new line terminator to all commands
        txt = "".join( map(lambda x: f"{x}\r\n", cmds) )

        self.log.debug(f"TX: {txt!r}")
        self.io.write(txt)
        self.io.flush()

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_BPC_read_enable_value(self):
        return self.state

    def _PZA_DRV_BPC_write_enable_value(self, v):
        self.state = v
        cmd = STATE_VALUE_ENUM[v]
        self.__write(f"OUT{int(cmd)}")

    def _PZA_DRV_BPC_read_voltage_value(self):
        return self.voltage

    def _PZA_DRV_BPC_write_voltage_value(self, v):
        self.voltage = v
        self.__write(f"VSET1:{v:.3f}")

    def _PZA_DRV_BPC_read_current_value(self):
        return self.current
    
    def _PZA_DRV_BPC_write_current_value(self, v):
        self.current = v
        self.__write(f"ISET1:{v:.3f}")

    ###########################################################################
    ###########################################################################

    def PZADRV_hunt():
        """
        """
        return None

