import time
from meta_drivers.relay import MetaDriverRelay
from connectors.serial_tty import ConnectorSerialTty

STATE_VALUE_ENUM = { True : 1, False: 0  }

COMMAND_TIME_LOCK=0.1

def cmd(cmd):
    """Append the correct command termination to the command
    """
    termination = "\r" # only one "\r" is OK, do not use "\n"
    return (cmd + termination)

class InterfaceVoxpowerInhibit(MetaDriverRelay):
    """ Driver to manage the voxpower inhibiter
    """

    # ---

    def __init__(self, name=None, channel=0, serial_settings={}) -> None:
        """Constructor
        """
        self.channel_id = channel
        self.serial_settings = serial_settings
        super().__init__(name=name)

    # =============================================================================
    # FROM MetaDriverRelay

    # ---
    
    async def _PZA_DRV_loop_init(self):
        """Driver initialization
        """

        # Get the gate
        self.serial_connector = await ConnectorSerialTty.Get(**self.serial_settings)

        # Call meta class Relay ini
        await super()._PZA_DRV_loop_init()

    # ---

    ###########################################################################
    ###########################################################################

    # STATE #
    
    def _PZA_DRV_RELAY_config(self):
        """Driver configuration
        """
        return super()._PZA_DRV_RELAY_config()

    async def _PZA_DRV_RELAY_read_state_open(self):
        """Get channel HIGH/LOW state
        """
        # L = LOW, voxpower channel enabled
        # H = HIGH, voxpower channel inhibited
        # statusBytes = await self.serial_connector.write_and_read_until(cmd("S{self.channel_id}"), expected=b"\n")
        statusBytes = await self.serial_connector.write_and_read_during("S{self.channel_id}\n", time_lock_s=COMMAND_TIME_LOCK, read_duration_s=0.1)
        print(statusBytes)

        status = statusBytes.decode('utf-8')
        print(status)

        # when the platform is started it detects a HIGH state on the channels
        if status == "HH":
            return True
        else:
            return False

    # ---
    
    async def _PZA_DRV_RELAY_write_state_open(self, value):
        """Set channel HIGH/LOW state
        """
        # To inhibit a Voxpower channel, send command IN with N the channel id
        # To enable a Voxpower channel, send command EN with N the channel id
        if value:
            self.log.info(f"write inhibit value for channel : {self.channel_id}")
            await self.serial_connector.write(f"I{self.channel_id}\n", time_lock_s=COMMAND_TIME_LOCK)
        else:
            self.log.info(f"write enable value for channel : {self.channel_id}")
            await self.serial_connector.write(f"E{self.channel_id}\n", time_lock_s=COMMAND_TIME_LOCK)