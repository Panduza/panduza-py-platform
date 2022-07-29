import time
import threading
from loguru import logger
from ..meta_driver_file import MetaDriverFile

class DriverIoFake(MetaDriverFile):
    
    ###########################################################################
    ###########################################################################

    def config(self):
        """ From MetaDriver
        """
        return {
            "compatible": "file_fake",
            "info": { "type": "file", "version": "1.0" },
            "settings": {
                "behaviour": { "type": "str", "desc": "fake behaviour of the io [static|auto_toggle]" },
                "loopback": { "type": "str", "desc": "to internaly loopback the value to an other fake_io interface" }
            }
        }
    
    ###########################################################################
    ###########################################################################

    def setup(self, tree):
        """ From MetaDriver
        """
        # Initialize basic properties
        # self.direction = 'in'
        # self.value=0
        # self.behaviour="static"
        # self.__loop = 0
        # self.loopback = None
        # self.mutex = threading.Lock()

        # # Configure the fake behaviour
        # # Static by default => just wait for commands
        # if "settings" in tree:
        #     settings = tree["settings"]

        #     #
        #     if "behaviour" in settings:
        #         target_behaviour = settings["behaviour"]
        #         if target_behaviour in ["static", "auto_toggle"]:
        #             self.behaviour = target_behaviour
        #         else:
        #             logger.error("unknown behaviour '{}' fallback to 'static'", target_behaviour)

        #     # 
        #     if "loopback" in settings:
        #         self.loopback = self.get_interface_instance_from_name(settings["loopback"])
        #         logger.info(f"loopback enabled : {self.loopback}")

        # Register commands
        # self.register_command("value/set", self.__value_set)
        # self.register_command("direction/set", self.__direction_set)

    ###########################################################################
    ###########################################################################

    def on_start(self):
        """On driver start, just update initiale attributes
        """
        # self.push_io_value(self.value)
        # self.push_io_direction(self.direction)
        pass

    ###########################################################################
    ###########################################################################

    def loop(self):
        """ From MetaDriver
        """
        return False
