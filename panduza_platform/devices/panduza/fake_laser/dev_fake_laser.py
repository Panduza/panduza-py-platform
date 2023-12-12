from core.platform_device import PlatformDevice, array_name

from .itf_fake_blc import InterfacePanduzaFakeBlc
from .itf_fake_thermometer import InterfacePanduzaFakeThermometer

class DevicePanduzaFakeLaser(PlatformDevice):

    # ---

    def _PZA_DEV_config(self):
        return {
            "family": "LASER",
            "model": "FakeLaser",
            "manufacturer": "Panduza",
            "settings_props": [
                {
                    'name': 'number_of_channel',
                    'type': 'int'
                },
                {
                    'name': 'has_thermometer',
                    'type': 'bool'
                }
            ]
        }

    # ---

    async def _PZA_DEV_mount_interfaces(self):
        """
        """

        number_of_channel = self.settings.get("number_of_channel", 1)
        has_thermo = self.settings.get("has_thermometer", False)
        
        for chan in range(0, number_of_channel):

            self.mount_interface(
                InterfacePanduzaFakeBlc(name=array_name("channel", chan, "ctrl"))
            )

            if has_thermo:
                self.mount_interface(
                    InterfacePanduzaFakeThermometer(name=array_name("channel", chan, "am"))
                )

    # ---

