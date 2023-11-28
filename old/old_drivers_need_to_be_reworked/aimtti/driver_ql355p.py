import io
from collections import ChainMap
from meta_drivers.bpc import MetaDriverBpc
from connectors.serial_tty import ConnectorSerialTty

from connectors.udev_tty import HuntUsbDevs

QL355P_USBID_VENDOR="103e"
QL355P_USBID_MODEL="03e8"
QL355P_SERIAL_BAUDRATE=19200
QL355P_TTY_BASE="/dev/ttyUSB"

STATE_VALUE_ENUM = { True: 1, False: 0 }
VOLTAGE_BOUNDS     = { "min": 0, "max": 30 }
CURRENT_BOUNDS      = { "min": 0, "max":  5 }


class DriverQL355P(MetaDriverBpc):
    """Driver for the device QL355P from aim-TTI
    """
    
    ###########################################################################
    ###########################################################################

    def _PZA_DRV_config(self):
        # Extend the common bpc config
        return ChainMap(super()._PZA_DRV_config(), {
            "name": "Py_Bpc_QL355P",
            "description": "Power Supply QL355P",
            "compatible": [
                "ql355p",
                "aimtty.ql355p",
                "bpc.aimtty.ql355p",
                "py.bpc.aimtty.ql355p"
            ]
        })

    def __tgen(serial_short, name_suffix):
        return {
            "name": "QL355P:" + name_suffix,
            "driver": "py.bpc.aimtty.ql355p",
            "settings": {
                "serial_short": serial_short
            }
        }

    def _PZA_DRV_tree_template(self):
        return DriverQL355P.__tgen("USB: Short Serial ID", "template")

    def _PZA_DRV_hunt_instances(self):
        instances = []
        usb_pieces = HuntUsbDevs(vendor=QL355P_USBID_VENDOR, model=QL355P_USBID_MODEL, subsystem="tty")
        for p in usb_pieces:
            iss = p["ID_SERIAL_SHORT"]
            instances.append(DriverQL355P.__tgen(iss, iss))
        return instances

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_loop_init(self):

        # Get settings from tree and append constant settings for this device
        settings = dict() if "settings" not in tree else tree["settings"]
        settings["vendor"] = QL355P_USBID_VENDOR
        settings["model"] = QL355P_USBID_MODEL
        settings["baudrate"] = QL355P_SERIAL_BAUDRATE
        settings["base_devname"] = QL355P_TTY_BASE
        
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
        self._PZA_DRV_BPC_update_misc("model", "QL355P (AIM-TTI)")

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

    # STATE #

    def _PZA_DRV_BPC_read_enable_value(self):
        return self.state

    # ---

    def _PZA_DRV_BPC_write_enable_value(self, v):
        self.state = v
        cmd = STATE_VALUE_ENUM[v]
        self.__write(f"OP1 {int(cmd)}")

    # VOLTAGE #

    def _PZA_DRV_BPC_read_voltage_value(self):
        return self.voltage

    # ---

    def _PZA_DRV_BPC_read_voltage_real(self):
        return 0
    
    # ---

    def _PZA_DRV_BPC_write_voltage_value(self, v):
        self.voltage = v
        self.__write(f"V1 {v:.3f}")

    # ---

    def _PZA_DRV_BPC_voltage_value_min_max(self):
        return VOLTAGE_BOUNDS
    # ---

    def _PZA_DRV_BPC_read_voltage_decimals(self):
        return 2

    # CURRENT #
    
    def _PZA_DRV_BPC_read_current_value(self):
        return self.current

    # ---

    def _PZA_DRV_BPC_write_current_value(self, v):
        self.current = v
        self.__write(f"I1 {v:.3f}")

    # ---
    
    def _PZA_DRV_BPC_current_value_min_max(self):
        return CURRENT_BOUNDS
    
    # ---

    def _PZA_DRV_BPC_read_current_real(self):
        return 0

    # ---

    def _PZA_DRV_BPC_read_current_decimals(self):
        return 3
    
    # SETTINGS #

    def _PZA_DRV_BPC_settings_capabilities(self):
        return  {
            "ovp": False,
            "ocp": False,
            "silent": False,
        }
    
    ###########################################################################
    ###########################################################################

    def PZADRV_hunt():
        """
        """
        return None

