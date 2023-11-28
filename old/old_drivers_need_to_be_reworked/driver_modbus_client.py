import time
from ...meta_driver import MetaDriver
from ...connectors.modbus_client_serial import ConnectorModbusClientSerial

from connectors.udev_tty import HuntUsbDevs


class DriverModbusClient(MetaDriver):
    """Driver for modbus client
    """

    WATCHLIST = []

    HOLDING_REGS_VALUES = {}

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_config(self):
        return {
            "name": "ModbusClient",
            "description": "Generic Modbus Client",
            "info": {
                "type": "modbus.client",
                "version": "0.0"
            },
            "compatible": [
                "modbus.client",
                "py.modbus.client"
            ]
        }



    def _PZA_DRV_tree_template(self,
        name="template",
        vendor="USB: Vendor ID",
        model="USB: Model ID",
        serial_short= "USB: Short Serial ID",
        port_name = "/dev/ttyUSBxxx or COM"
    ):
        template = {
            "name": "modbus_client:" + name,
            "driver": "py.modbus.client",
            "settings": {
                "mode": "rtu",
                "vendor": vendor,
                "model": model,
                "serial_short": serial_short,
                "port_name": port_name,
                "baudrate": "int => 9600 | 115200 ..."
            }
        }

        if port_name is None:
            del template["settings"]["port_name"]

        return template

    def _PZA_DRV_hunt_instances(self):
        instances = []

        # 16de:0003 Telemecanique USB - RS485 SL cable
        TELEMEC_VENDOR="16de"
        TELEMEC_MODEL="0003"
        usb_pieces = HuntUsbDevs(vendor=TELEMEC_VENDOR, model=TELEMEC_MODEL, subsystem="tty")
        for p in usb_pieces:
            iss = p["ID_SERIAL_SHORT"]
            instances.append(self._PZA_DRV_tree_template(
                name=iss,
                vendor=TELEMEC_VENDOR,
                model=TELEMEC_MODEL,
                serial_short=iss,
                port_name=None))



        return instances

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_loop_init(self):

        # self.log.debug(f"{tree}")

        
        settings = dict() if "settings" not in tree else tree["settings"]
        settings["base_devname"] = "/dev/ttyUSB"

        # Get the gate
        self.modbus = ConnectorModbusClientSerial.GetV2(**settings)


        self.__cmd_handlers = {
            "holding_regs": self.__handle_cmds_set_holding_regs,
            "watchlist": self.__handle_cmds_set_watchlist,
        }

        self._PZA_DRV_init_success()


    ###########################################################################
    ###########################################################################

    def _PZA_DRV_loop_run(self, loop):
        """
        """
        
        for config in self.WATCHLIST:
            self.log.debug(f"{config}")
            regs = self.modbus.read_holding_registers(address=config["address"], size=config["size"], unit=config["unit"])
            self.log.debug(f"{regs}")

            self.HOLDING_REGS_VALUES.setdefault(config["unit"], {})
            u = self.HOLDING_REGS_VALUES[config["unit"]]
            u[str(config["address"])] = regs[0]

            self._update_attribute("holding_regs", "value", self.HOLDING_REGS_VALUES)

            # TODO Fix this BAD way of managing polling for multiple polling time
            time.sleep(float(config["polling_time_s"]))




    ###########################################################################
    ###########################################################################

    def _PZA_DRV_loop_err(self):
        """
        """
        pass

    ###########################################################################
    ###########################################################################

    def _PZA_DRV_cmds_set(self, payload):
        """From MetaDriver
        """
        cmds = self.payload_to_dict(payload)
        self.log.debug(f"cmds as json : {cmds}")
        for att in self.__cmd_handlers:
            if att in cmds:
                self.__cmd_handlers[att](cmds[att])

    ###########################################################################
    ###########################################################################

    def __handle_cmds_set_holding_regs(self, cmd_att):
        """
        """
        if "values" in cmd_att:
            values = cmd_att["values"]
            try:
                for u in values:
                    for addr in values[u]:
                        self.log.debug(f"on unit {u} write register {addr} with {values[u][addr]}")
                        self.modbus.write_register(int(addr), int(values[u][addr]), int(u) )

                # self._update_attribute("state", "value", v)
            except Exception as e:
                self.log.error(f"{e}")

    ###########################################################################
    ###########################################################################

    def __handle_cmds_set_watchlist(self, cmd_att):
        """
        """
        if "configs" in cmd_att:
            configs = cmd_att["configs"]
            try:
                # TODO need to check inputs here
                self.WATCHLIST = configs
                # for u in configs:
                #     for addr in configs[u]:
                #         self.log.debug(f"append watch on unit {u} register {addr} with {configs[u][addr]}")
                #         self.modbus.write_register(int(addr), int(configs[u][addr]), int(u) )
                # self._update_attribute("state", "value", v)
            except Exception as e:
                self.log.error(f"{e}")

