from core.platform_device import PlatformDevice, array_name

from .itf_fake_powermeter import InterfacePanduzaFakePowermeter

class DevicePanduzaFakePowermeter(PlatformDevice):

    # ---

    def _PZA_DEV_config(self):
        return {
            "family": "LASER",
            "model": "FakePowermeter",
            "manufacturer": "Panduza",
            "settings_props": [
            ]
        }

    # ---

    async def _PZA_DEV_mount_interfaces(self):
        """
        """
    
        self.mount_interface(
            InterfacePanduzaFakePowermeter(name="power")
        )

    # ---

