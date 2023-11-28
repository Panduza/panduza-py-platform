
from core.platform_device import PlatformDevice

class DevicePanduzaFakeDioController(PlatformDevice):
    
    def _PZA_DEV_config(self):
        """
        """
        return {
            "family": "TBD",
            "model": "FakeDioController",
            "manufacturer": "Panduza"
        }

    def _PZA_DEV_interfaces_generator(self):
        """
        """
        number_of_dio = int( self.get_settings().get("number_of_dio", 1) )
        interfaces = []
        for id in range(0, number_of_dio):
            interfaces.append(
                {
                    "name": f"dio_{id}",
                    "driver": "panduza.fake.dio"
                }
            )
        return interfaces


