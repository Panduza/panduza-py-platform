from meta_drivers.relay import MetaDriverRelay

class DrvPanduzaFakeRelay(MetaDriverRelay):
    """
    """

    # =============================================================================
    # FROM MetaDriverRelay

    # ---

    def _PZA_DRV_RELAY_config(self):
        """
        """
        return {
            "name": "panduza.fake.relay",
            "description": "Virtual Relay"
        }

    # ---

    async def _PZA_DRV_loop_init(self):
        """
        """
        self.__fakes = {
            "state": {
                "open": False
            }
        }

        # Call meta class BPC ini
        await super()._PZA_DRV_loop_init()

    # ---

    async def _PZA_DRV_RELAY_read_state_open(self):
        """
        """
        return self.__fakes["state"]["open"]

    # ---

    async def _PZA_DRV_RELAY_write_state_open(self, v):
        """
        """
        self.__fakes["state"]["open"] = v

