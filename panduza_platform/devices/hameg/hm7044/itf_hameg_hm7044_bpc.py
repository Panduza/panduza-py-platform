import re
from functools import reduce
from hamcrest import assert_that, has_key, instance_of
from meta_drivers.bpc import MetaDriverBpc
from connectors.serial_tty import ConnectorSerialTty

STATE_VALUE_ENUM = { True : 1, False: 0  }
VOLTAGE_BOUNDS     = { "min": 0, "max": 30 }
CURRENT_BOUNDS      = { "min": 0, "max": 10 }


HM7044_THROTTLE_DELAY  = 0.025 # I want to die...


def int_to_state_string(v_int):
    key_list = list(STATE_VALUE_ENUM.keys())
    val_list = list(STATE_VALUE_ENUM.values())
    position = val_list.index(v_int)
    return key_list[position]

def cmd(cmd):
    """Append the correct command termination to the command
    """
    termination = "\r" # only one "\r" is OK, do not use "\n"
    return (cmd + termination)


class InterfaceHamegHm7044Bpc(MetaDriverBpc):
    """
    """

    # ---

    def __init__(self, name=None, channel=0, serial_settings={}, shared_data=None) -> None:
        """Constructor
        """
        self.channel_id = channel
        self.serial_settings = serial_settings
        self.channels_data = shared_data
        super().__init__(name=name)

    # ---
    
    def chan_data(self):
        return self.channels_data[self.channel_id]

    # =============================================================================
    # FROM MetaDriverBpc

    # ---

    async def _PZA_DRV_loop_init(self):
        """Driver initialization
        """

        # Get the gate
        self.serco = await ConnectorSerialTty.Get(**self.serial_settings)
        
        
        print("---------------------------------------")
        await self.state_sync()


        # Call meta class BPC ini
        await super()._PZA_DRV_loop_init()


    async def state_sync(self):
        buf_byte = await self.serco.write_and_read_until(cmd("READ"), expected=b"\r")
        
        buf = buf_byte.decode("utf-8")
        print(buf, type(buf))
        
        # Quick and dirty stuff parsing
        fields    = [x.strip() for x in buf.split(";")]
        SPACE_REG = re.compile(r"\s+")

        voltages  = [x.strip() for x in SPACE_REG.sub(" ", fields[0]).split(" ")]
        currents  = [x.strip() for x in SPACE_REG.sub(" ", fields[1]).split(" ")]
        flags     = [x.strip() for x in SPACE_REG.sub(" ", fields[2]).split(" ")]

        self.log.debug(voltages)
        self.log.debug(currents)
        self.log.debug(flags)

        for i in range(4):
            self.channels_data[i].volts = float(voltages[i].replace("V", "").strip())
            self.channels_data[i].amps  = float(currents[i].replace("A", "").strip())
            self.channels_data[i].on    = not(flags[i*2].startswith("OFF"))

    ###########################################################################
    ###########################################################################

    # STATE #

    async def _PZA_DRV_BPC_read_enable_value(self):
        await self.state_sync()
        return self.chan_data().on

    # ---

    async def _PZA_DRV_BPC_write_enable_value(self, v):
        
        print( await self.serco.write_and_read_until(cmd(f"SEL {self.channel_id+1}"), expected=b"\r") )

        goal_str = "ON" if v else "OFF"
        print( await self.serco.write_and_read_until(cmd(goal_str), expected=b"\r") )
        

        state = v
        if state:
            # Check wether we will need to enable output or not
            will_enable = not(reduce(lambda a,b: a and b, [x.on for x in self.channels_data], False))
            if will_enable:
                print( await self.serco.write_and_read_until(cmd("EN"), expected=b"\r") )
        else:
            # Check wether we will need to disable output or not
            will_disable = reduce(lambda a,b: a + (b==True), [x.on for x in self.channels_data], 0) == 1
            if will_disable:
                print( await self.serco.write_and_read_until(cmd("DIS"), expected=b"\r") )


        print( await self.serco.write_and_read_until(cmd(f"SEL N"), expected=b"\r") )
    
        pass

    # VOLTAGE #

    async def _PZA_DRV_BPC_read_voltage_value(self):
        await self.state_sync()
        print("r volts", self.chan_data().volts)
        return self.chan_data().volts

    # ---

    async def _PZA_DRV_BPC_write_voltage_value(self, v):
        # 
        print("------", v, type(v))
        
        volts_float = round(v, 2)
        print("------", volts_float)
        
        print( await self.serco.write_and_read_until(cmd(f"SEL {self.channel_id+1}"), expected=b"\r") )
        print( await self.serco.write_and_read_until(cmd(f"SET {volts_float}V"), expected=b"\r") )
        print( await self.serco.write_and_read_until(cmd(f"SEL N"), expected=b"\r") )
        
        while(self.chan_data().volts != volts_float):
            await self.state_sync()

    # ---

    async def _PZA_DRV_BPC_voltage_value_min_max(self):
        return VOLTAGE_BOUNDS

    # ---

    async def _PZA_DRV_BPC_read_voltage_decimals(self):
        return 2

    # CURRENT #

    async def _PZA_DRV_BPC_read_current_value(self):
        await self.state_sync()
        return self.chan_data().amps

    # ---

    async def _PZA_DRV_BPC_write_current_value(self, v):
        # 
        print("------", v, type(v))

        amps_float = round(v, 3)
        print("------", amps_float)
        
        print( await self.serco.write_and_read_until(cmd(f"SEL {self.channel_id+1}"), expected=b"\r") )
        print( await self.serco.write_and_read_until(cmd(f"SET {amps_float}A"), expected=b"\r") )
        print( await self.serco.write_and_read_until(cmd(f"SEL N"), expected=b"\r") )
        
        while(self.chan_data().amps != amps_float):
            await self.state_sync()

    # ---

    async def _PZA_DRV_BPC_current_value_min_max(self):
        return CURRENT_BOUNDS

    # ---

    async def _PZA_DRV_BPC_read_current_decimals(self):
        return 3

