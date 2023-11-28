import time
import numpy as np
from panduza import Bpc

ADDR="localhost"
PORT=1883

# power_channel = Bpc(addr=ADDR, port=PORT, topic="pza/default/Hanmatek_Hm310t/bpc")
# power_channel = Bpc(addr=ADDR, port=PORT, topic="pza/default/Panduza_FakeBps/channel_1")
# power_channel = Bpc(addr=ADDR, port=PORT, topic="pza/default/Tenma_722710/bpc")
# power_channel = Bpc(addr=ADDR, port=PORT, topic="pza/default/fake/:channel_0:_ctrl")
power_channel = Bpc(addr=ADDR, port=PORT, topic="pza/default/xavier/:channel_0:_ctrl")


# Read from interface
MIN_VOLTAGE=0
MAX_VOLTAGE=10
STP_VOLTAGE=0.1
DEC_VOLTAGE=1



for i in range(0, 20):
    state_value = bool(i%2)
    print(f"set enable {state_value}")
    power_channel.enable.value.set(state_value)


for voltage in np.arange(MIN_VOLTAGE, MAX_VOLTAGE, STP_VOLTAGE):
    voltage = round(voltage, DEC_VOLTAGE)
    print(f"set voltage {voltage}V")
    power_channel.voltage.value.set(voltage, ensure=True)


for voltage in np.arange(MIN_VOLTAGE, MAX_VOLTAGE, STP_VOLTAGE):
    voltage = round(voltage, DEC_VOLTAGE)
    print(f"set voltage {voltage}V")
    power_channel.voltage.value.set(voltage, ensure=False)







