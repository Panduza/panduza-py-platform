import os
import sys
import time
import json
import pkgutil
import argparse
import traceback
import threading
import importlib
import socket

import asyncio
import aiofiles
import aiomonitor



from sys import platform

from core.monitored_event_loop import MonitoredEventLoop

from .conf import PLATFORM_VERSION
from log.platform import platform_logger


# from .platform_client import PlatformClient
from .platform_errors import InitializationError

from .mqtt_async_client import MqttAsyncClient

# from .platform_driver_factory import PlatformDriverFactory
from .platform_device_factory import PlatformDeviceFactory


# STATUS_FILE_PATH="/etc/panduza/log/status.json"


class Platform:
    """ Main class to manage the platform
    """

    # =============================================================================
    # PUBLIC FUNCTIONS

    # ---

    def __init__(self, run_dir="/etc"):
        """ Constructor
        """
        # Init the platform logger
        self.log = platform_logger()
        self.run_dir = run_dir

        # Debug logs to structure log file
        self.log.info("==========================================")
        self.log.info(f"= PANDUZA PYTHON PLATFORM          {PLATFORM_VERSION} =")
        self.log.info("==========================================")

        # Create Factories
        self.device_factory = PlatformDeviceFactory(self)

        # Threads
        self.threads = []

        # Drivers
        self.drivers = []

        # List of device instances managed by this platform
        self.devices = []

        # Interfaces
        self.interfaces = []

        # Tree that must be loaded at startup
        self.dtree_filepath = None

        #
        self.force_log = False

        # If true, it means that the platform event loop can continue to run and work 
        self.alive = True

        # Event loop object holder
        self.event_loop = None

        # To enable or disable event loop monitoring
        # Should be false for release
        self.event_loop_debug = True

        # Mqtt Clients
        self.clients = {}

        # Current config content
        self.dtree = {}

    # ---

    def run(self):
        """Starting point of the platform
        """
        # First go into factories initialization
        try:
            self.device_factory.discover()
        except InitializationError as e:
            self.log.critical(f"Error during platform initialization: {e}")
            sys.exit(-1)

        # Run the operationnal mode and measure alive time
        start_time = time.time()
        self.__oper_mode()
        alive_time = round(time.time()-start_time, 2)
        self.log.info(f"Platform alive time {alive_time}s")

    # ---

    def load_task(self, coro, name = None):
        """Load a new task into the event loop
        """
        return self.task_group.create_task( coro, name=name )

    # ---

    def load_worker(self, worker):
        """Load worker into the event loop
        """
        self.log.info(f"Load '{worker}'")
        self.load_task( worker.task(), name=f"WORKER>{worker.PZA_WORKER_name()}" )

    # ---

    async def mount_client(self, name, host_addr, host_port):
        """Mount a mqtt client
        """ 
        self.log.info(f"Mount client '{name}'")
        mqtt_client = MqttAsyncClient(self, host_addr, host_port)
        self.clients[name] = mqtt_client
        self.load_worker(mqtt_client)

    # ---

    async def unmount_client(self, name):
        self.log.info(f"Unmount client '{name}'")
        self.clients[name].stop()
        self.clients.remove(name)

    # ---

    async def unmount_all_clients(self, force=False):
        for client in self.clients:
            if force or (not client.keep_mounted):
                await self.unmount_client(client)

    # ---

    async def mount_device(self, client_name, group_name, device_cfg, keep_mounted = False):
        """Mount a device
        """
        # Debug log
        self.log.info(f"Mount device '{device_cfg}'")

        # Produce the device instance
        device_instance = self.device_factory.produce_device(self.clients[client_name], group_name, device_cfg, keep_mounted)

        # Mount interfaces
        await device_instance.mount_interfaces()

        # Store device instance
        self.devices.append(device_instance)

    # ---

    async def unmount_device(self, device):
        self.log.info(f"Unmount device {device}")
        await device.unmount_interfaces()
        self.devices.remove(device)

    # ---

    async def unmount_all_devices(self, force=False):
        self.log.warning(self.devices)
        for device in self.devices:
            print("PAFF ")
            if force or (not device.keep_mounted):
                print("!!!!!!!!!!! ", device)
                await self.unmount_device(device)
            else:
                print("??????????? NOOO ", device)
        print("ENNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNND")

    # ---

    def get_number_of_device(self):
        """Number fo devices mounted on this platform
        """
        return len(self.devices)

    # ---

    def get_number_of_interfaces(self):
        """Return the total number of interfaces across all devices
        """
        nb = 0
        for device in self.devices:
            nb += device.get_number_of_interfaces()
        return nb

    # ---

    async def load_config_content_task(self, new_dtree):
        """
        """
        # Parse configs
        self.log.debug(f"load config:{json.dumps(new_dtree, indent=1)}")

        # Remove mounted device from the previous configuration
        await self.unmount_all_devices()

        # Mount each device
        devices = new_dtree.get("devices", [])
        for device_cfg in devices:
            await self.mount_device("primary", "default", device_cfg)

        # Internal store of the platform config
        self.dtree = new_dtree

    # ---

    async def handle_worker_panic(self, name, status):
        # 
        self.log.error(f"PANIC: {name}")

        self.log.error( str(status.get("name", "")) + "\n" )
        self.log.error( str(status.get("final_state", "")) + "\n" )
        self.log.error( str(status.get("error_string", "")) + "\n" )

        # Remove mounted device from the previous configuration
        await self.unmount_all_devices()

    # ---

    # =============================================================================
    # PRIVATE FUNCTIONS

    # ---

    async def __idle_task(self):
        """Idle Task of the platform
        """
        # Start idle task
        self.log.info(f"Idle task start")

        # Start the global task group
        async with asyncio.TaskGroup() as self.task_group:

            self.log.warning("1")
            # Connect to primary broker
            await self.mount_client("primary", "localhost", 1883)

            self.log.warning("2")
            # Mount the device interfaces of the server
            await self.mount_device("primary", "server", 
                {
                    "name": socket.gethostname(),
                    "ref": "Panduza.Server",
                },
                keep_mounted=True
            )

            self.log.warning("3")
            # Task that load the config tree
            await self.__load_tree_task()

            # Wait for ever
            while(self.alive):
                await asyncio.sleep(1)


        self.log.warning("END OF IDLE !")
        self.event_loop.stop()


    # ---

    def __oper_mode(self):
        """Run the operational mode
        """
        # Create the Monitored loop
        self.event_loop = MonitoredEventLoop(self)
        asyncio.set_event_loop(self.event_loop)

        # Create the idle task
        self.event_loop.create_task(self.__idle_task(), name="IDLE")

        # 
        monitor = None
        if self.event_loop_debug:
            monitor = aiomonitor.Monitor(self.event_loop)
            monitor.start()

        # try:
        self.log.info("platform run")
        self.event_loop.run_forever()
        # finally:
        #     # loop.run_until_complete(loop.shutdown_asyncgens())
        #     # loop.close()
        #     pass


        # # 
        # if self.event_loop_debug:
        #     with aiomonitor.start_monitor(self.event_loop):
        #         self.event_loop.run_until_complete(self.__idle_task())
        # else:
        #     self.event_loop.run_until_complete(self.__idle_task())
 
        # except InitializationError as e:
        #     self.log.critical(f"Error during platform initialization: {e}")
        #     self.generate_early_status_report(str(e))
        # except KeyboardInterrupt:
        #     self.log.warning("ctrl+c => user stop requested")
        #     self.stop()
        # except FileNotFoundError:
        #     self.log.critical(f"Platform configuration file 'tree.json' has not been found at location '{self.dtree_filepath}' !!==>> STOP PLATFORM")

    # ---

    async def __load_tree_task(self):
        """Load the configuration tree into the platform
        """

        # Load a default tree path if not provided
        if not self.dtree_filepath:
            # Set the default tree path on linux
            if platform == "linux" or platform == "linux2":
                self.dtree_filepath = f"{self.run_dir}/panduza/tree.json"

        # Control that the file exist
        new_dtree = {}
        if not os.path.isfile(self.dtree_filepath):
            self.log.warning(f"No default config defined at {self.dtree_filepath}")

        else:
            # Load tree file
            async with aiofiles.open(self.dtree_filepath) as tree_file:
                content = await tree_file.read()
            new_dtree = json.loads(content)

        # Load config
        await self.load_config_content_task(new_dtree)

    # ---

    def stop(self):
        """To stop the entire platform
        """
        # Stop alive flag
        self.alive = False

        # 
        self.event_loop.create_task(self.unmount_all_devices(force=True), name="CLEAR")
         
        #
        self.event_loop.create_task(self.unmount_all_clients(force=True), name="CLEAR")


    # ---

    # def generate_early_status_report(self, error_string):
    #     """Generate a status report when something went wrong during initialization
    #     """
    #     status_obj = {}

    #     status_obj["final_state"] = "initialization"
    #     status_obj["error_string"] = error_string
    #     status_obj["threads"] = []

    #     # Write the status file
    #     with open(STATUS_FILE_PATH, "w") as json_file:
    #         json.dump(status_obj, json_file)

    # # ---

    # def generate_status_reports(self):
    #     """Generate a json report status and log it to the console
    #     """

    #     status_obj = {}
    #     status_obj["final_state"] = "running"

    #     # Gather the status of each thread
    #     thread_status = []
    #     for thr in self.threads:
    #         thread_status.append(thr.get_status())

    #     # 
    #     status_obj["threads"] = thread_status

    #     # Write the status file
    #     with open(STATUS_FILE_PATH, "w") as json_file:
    #         json.dump(status_obj, json_file)

    #     # Print into the console
    #     report  = "\n"
    #     for thr in thread_status:
    #         report += "=================================\n"
    #         report +=f"== {thr['name']} \n"
    #         report += "=================================\n"

    #         for w in thr['workers']:
    #             report += "\n"
    #             report += str(w.get("name", "")) + "\n"
    #             report += str(w.get("final_state", "")) + "\n"
    #             report += str(w.get("error_string", "")) + "\n"
    #     self.log.info(report)


 




    # ---

    def load_tree_overide(self, tree_filepath):
        """platform will use the given tree filepath
        """
        self.dtree_filepath = tree_filepath
        self.log.debug(f"force tree:{self.dtree_filepath}")
