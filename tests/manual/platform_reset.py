import time
import numpy as np
from panduza import Client, Core, Platform

ADDR="localhost"
PORT=1883

Core.EnableLogging()

c = Client(url=ADDR, port=PORT)
c.connect()
platforms = c.scan_all_platform_interfaces()

platform_topic = next(iter(platforms.keys()))
print(platform_topic)

plat = Platform(addr=ADDR, port=PORT, topic=platform_topic)

plat.dtree.content.set({
})

