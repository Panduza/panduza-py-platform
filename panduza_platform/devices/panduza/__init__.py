from .fake_dio_controller           import DevicePanduzaFakeDioController
from .fake_bps.dev_fake_bps         import DevicePanduzaFakeBps
from .fake_relay_controller         import DevicePanduzaFakeRelayController
from .server.dev_server             import DevicePanduzaServer
from .fake_webcam.dev_fake_webcam   import DevicePanduzaFakeWebcam

from .voxpower_inhibiter.dev_voxpower_inhibiter import DeviceVoxpowerInhibiter

from .fake_laser.dev_fake_laser             import DevicePanduzaFakeLaser
from .fake_powermeter.dev_fake_powermeter   import DevicePanduzaFakePowermeter


PZA_DEVICES_LIST= [ 
    DevicePanduzaFakeDioController,
    DevicePanduzaFakeBps,
    DevicePanduzaFakeRelayController,
    DevicePanduzaServer,
    DevicePanduzaFakeWebcam,
    DevicePanduzaFakeLaser,
    DevicePanduzaFakePowermeter,
    DeviceVoxpowerInhibiter
]

