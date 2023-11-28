from core.platform_device import PlatformDevice

from .itf_fake_video_stream import InterfacePanduzaFakeVideoStream

class DevicePanduzaFakeWebcam(PlatformDevice):
    """
    """

    # ---

    def _PZA_DEV_config(self):
        """
        """
        return {
            "family": "??",
            "model": "FakeWebcam",
            "manufacturer": "Panduza"
        }

    # ---

    async def _PZA_DEV_mount_interfaces(self):
        """
        """

        self.mount_interface(
            InterfacePanduzaFakeVideoStream(name="stream")
        )

