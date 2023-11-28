from .fake_dio_controller           import DevicePanduzaFakeDioController
from .fake_bps.dev_fake_bps         import DevicePanduzaFakeBps
from .fake_relay_controller         import DevicePanduzaFakeRelayController
from .server.dev_server             import DevicePanduzaServer
from .fake_webcam.dev_fake_webcam   import DevicePanduzaFakeWebcam

PZA_DEVICES_LIST= [ 
    DevicePanduzaFakeDioController,
    DevicePanduzaFakeBps,
    DevicePanduzaFakeRelayController,
    DevicePanduzaServer,
    DevicePanduzaFakeWebcam
]

