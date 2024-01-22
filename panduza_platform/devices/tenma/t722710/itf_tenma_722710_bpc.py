from hamcrest import assert_that, has_key, instance_of
from meta_drivers.bpc import MetaDriverBpc
from connectors.serial_tty import ConnectorSerialTty

STATE_VALUE_ENUM = { True : 1, False: 0  }
VOLTAGE_BOUNDS     = { "min": 0, "max": 30 }
CURRENT_BOUNDS      = { "min": 0, "max": 5 }


COMMAND_TIME_LOCK=0.1


def int_to_state_string(v_int):
    key_list = list(STATE_VALUE_ENUM.keys())
    val_list = list(STATE_VALUE_ENUM.values())
    position = val_list.index(v_int)
    return key_list[position]

class InterfaceTenma722710Bpc(MetaDriverBpc):
    """ Driver to manage the Tenma power supply
    """

    # ---

    def __init__(self, name=None, settings={}) -> None:
        """Constructor
        """
        self.settings = settings
        super().__init__(name=name)

    # ---

    async def _PZA_DRV_loop_init(self):
        """Driver initialization
        """

        # Get the Serial Connector
        self.serial_connector = await ConnectorSerialTty.Get(**self.settings)
        
        # 
        self.channel = 1

        # Call meta class BPC ini
        await super()._PZA_DRV_loop_init()

    ###########################################################################
    ###########################################################################

    # STATE #

    async def _PZA_DRV_BPC_read_enable_value(self):
        # Send "STATUS?" to get back the output state

        statusBytes = await self.serial_connector.write_and_read_during("STATUS?\n", time_lock_s=COMMAND_TIME_LOCK, read_duration_s=0.1)

        self.log.debug(f"{statusBytes.strip()}")
        status = ord(statusBytes.strip())

        if status & 0x40:
           out = 1
        else:
            out = 0
        str_value = int_to_state_string(out)
        return str_value
    		
    # ---

    async def _PZA_DRV_BPC_write_enable_value(self, v):
    	# Send "OUT{v}" to enable output
        int16_value = STATE_VALUE_ENUM[v]
        await self.serial_connector.write(f"OUT{int16_value}\n", time_lock_s=COMMAND_TIME_LOCK)

    # VOLTAGE #

    async def _PZA_DRV_BPC_read_voltage_value(self):
        # Send "VSET1?" to get the voltage value
        voltage = await self.serial_connector.write_and_read_during(f"VSET{self.channel}?\n", time_lock_s=COMMAND_TIME_LOCK, read_duration_s=0.1)
        return float(voltage)

    # ---

    async def _PZA_DRV_BPC_write_voltage_value(self, v):
        # Send "VSET1:{v}" to set the voltage value
        await self.serial_connector.write(f"VSET{self.channel}:{v}\n", time_lock_s=COMMAND_TIME_LOCK)

    # ---

    async def _PZA_DRV_BPC_voltage_value_min_max(self):
        return VOLTAGE_BOUNDS

    # ---

    async def _PZA_DRV_BPC_read_voltage_decimals(self):
        return 2

    # CURRENT #

    async def _PZA_DRV_BPC_read_current_value(self):
        current = await self.serial_connector.write_and_read_during(f"ISET{self.channel}?\n", time_lock_s=COMMAND_TIME_LOCK, read_duration_s=0.1)
        return float(current)

    # ---

    async def _PZA_DRV_BPC_write_current_value(self, v):
        # Send "ISET1:{v}" to set the Current value
        await self.serial_connector.write(f"ISET{self.channel}:{v}\n", time_lock_s=COMMAND_TIME_LOCK)

    # ---

    async def _PZA_DRV_BPC_current_value_min_max(self):
        return CURRENT_BOUNDS

    # ---

    async def _PZA_DRV_BPC_read_current_decimals(self):
        return 3

