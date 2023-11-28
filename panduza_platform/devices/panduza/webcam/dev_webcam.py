from core.platform_device import PlatformDevice

# from .itf_platform import InterfacePanduzaPlatform

class DevicePanduzaWebcam(PlatformDevice):
    """Represent the machine on which the platform is running
    """

    # ---

    def _PZA_DEV_config(self):
        """
        """
        return {
            "family": "??",
            "model": "Webcam",
            "manufacturer": "Panduza"
        }

    # ---

    async def _PZA_DEV_mount_interfaces(self):
        """
        """

        # itf_platform = InterfacePanduzaPlatform(name="test")
        # self.mount_interface(itf_platform)

        pass
