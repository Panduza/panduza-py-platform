from hamcrest import assert_that, has_key, instance_of
from meta_drivers.voltmeter import MetaDriverVoltmeter
from connectors.modbus_client_serial import ConnectorModbusClientSerial

class InterfaceHanmatekHM310tVoltmeter(MetaDriverVoltmeter):
    """
    """

    # ---

    def __init__(self, name=None, modbus_settings={}) -> None:
        """Constructor
        """
        self.modbus_settings = modbus_settings
        super().__init__(name=name)

    # ---

    async def _PZA_DRV_loop_init(self):
        """Driver initialization
        """

        # Get the gate
        self.modbus = await ConnectorModbusClientSerial.Get(**self.modbus_settings)

        # 
        self.modbus_unit = 1

        # Call meta class BPC ini
        await super()._PZA_DRV_loop_init()

    # ---

    async def _PZA_DRV_VOLTMETER_read_measure_value(self):
        addr = 0x0010
        regs = await self.modbus.read_holding_registers(addr, 1, self.modbus_unit)
        # self.log.debug(f"read real current addr={hex(addr)} regs={regs}")
        float_value = float(regs[0]) / 100.0
        return float_value

    # ---

