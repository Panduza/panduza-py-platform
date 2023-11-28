import abc
import sys
import time
import json
import socket
import asyncio
import traceback
import threading
import paho.mqtt.client as mqtt
import logging

from fnmatch import fnmatch
from log.client import client_logger
from .platform_worker import PlatformWorker

# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================

class TopicListener:

    def __init__(self, wildcard, topic) -> None:
        """Constructor
        """
        self.subscribed = False
        self.topic = topic
        self.wildcard = wildcard
        self.callbacks = []

    def append_callback(self, callback, **kwargs):
        """Append a new callback
        """
        # Check that callback is not already registered, and register
        if callback in self.callbacks:
            raise Exception(
                f"callback {callback} already registered for topic {self.wildcard}")

        # Append callback
        self.callbacks.append(callback)

# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================

class TopicListeners:

    def __init__(self) -> None:
        """Constructor
        """
        self.entries = []

    def register_entry_from_topic(self, topic):
        """Get entry associated to this topic
        """
        # Compose the wildcard from the topic
        wildcard = topic.replace("/+", "/*").replace("/#", "/*")

        # Check that the new wildcard is not already in the store
        for tl in self.entries:
            if tl.wildcard == wildcard:
                return tl

        # Append a new topic listeners
        entry = TopicListener(wildcard, topic)
        self.entries.append(entry)

        # return
        return entry

    def trigger_callbacks(self, topic, payload):
        """
        """
        # Check that the new wildcard is not already in the store
        for entry in self.entries:
            if fnmatch(topic, entry.wildcard):
                for cb in entry.callbacks:
                    cb(topic, payload)


# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================

class MqttAsyncClient(PlatformWorker):
    """Mqtt Client used by the platform and compatible with PlatformThreads
    """

    # ---

    def __init__(self, platform, addr, port) -> None:
        """Constructor
        """
        # Build parent
        super().__init__(platform)

        # Save address and port
        self.addr = addr
        self.port = port

        # Create the logger
        self.log = client_logger(str(addr) + ":" + str(port))
        self.worker_name = f"CLIENT>{str(addr)}:{str(port)}"

        # Mqtt connection
        self.mqtt_client = None

        # Initialize state machine
        self.__state = "init"
        self.__state_prev = None

        # States
        self.__states = {
            'init': self.__state_init,
            'connecting': self.__state_connecting,
            'running': self.__state_running,
            'error': self.__state_error,
            'disconnecting': self.__state_disconnecting
        }

        # Topic listeners will store callbacks that must be triggered when
        # a message for a given topic arrive.
        self.__listeners = TopicListeners()

    # =============================================================================
    # PUBLIC FUNCTIONS

    # ---

    def is_running(self):
        """Return True if the client is connected and running, False else
        """
        return self.__state == 'running'

    # ---

    def subscribe(self, topic: str, callback, **kwargs):
        """Registers a listener
        """
        # Debug log
        self.log.debug(f"Register listener for topic '{topic}'")

        # Create set if not existing for topics
        entry = self.__listeners.register_entry_from_topic(topic)

        # Append callback to the listener
        entry.append_callback(callback, **kwargs)

    # ---

    async def publish(self, topic, payload: bytes, qos=0, retain=False):
        """Helper to publish raw messages
        """
        # Debug
        self.log.debug(f"MSG_OUT %{topic}% {payload} QOS={qos}")

        # Publish the message and wait for it to be complete
        request = self.mqtt_client.publish(topic, payload, qos=qos, retain=retain)

        # Wait for publish but async way
        while(not request.is_published):
            await asyncio.sleep(0.01)

        # Debug
        # self.log.debug(f"MSG_OUT OK")

    # ---

    async def publish_json(self, topic, req: dict, qos=0, retain=False):
        """Helper to publish json messages
        """
        await self.publish(
            topic=topic,
            payload=json.dumps(req).encode("utf-8"),
            qos=qos,
            retain=retain
        )

    # =============================================================================
    # WORKER FUNCTIONS

    def stop(self):
        self.mqtt_client.disconnect()
        super().stop()

    # ---

    def PZA_WORKER_name(self):
        """From Worker
        """
        return self.worker_name

    # ---

    def PZA_WORKER_log(self):
        """From Worker
        """
        return self.log

    # ---

    def PZA_WORKER_status(self):
        """From Worker
        """
        status = {}
        status["name"] = self.PZA_WORKER_name()
        status["final_state"] = f'{self.__state}'
        return status

    # ---

    async def PZA_WORKER_task(self):
        """
        """
        # Log state transition
        if self.__state != self.__state_prev:

            # Managed message
            self._state_started_time = time.time()
            self.log.debug(f"STATE CHANGE ::: {self.__state_prev} => {self.__state}")
            self.__state_prev = self.__state

        # Execute the correct callback
        if not (self.__state in self.__states):
            # error critique !
            pass
        await self.__states[self.__state]()

    # =============================================================================
    # STATES FUNCTIONS

    async def __state_init(self):
        """Initialization state
        """
        
        # Start connection
        self.mqtt_client = mqtt.Client()
        # self.mqtt_client.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

        # self.mqtt_client.keep_alive = 45


        self.mqtt_client.on_message = self.__on_message

        self.mqtt_client.on_connect = self.__on_connect

        # self.mqtt_client.on_disconnect = self.__on_disconnect
        # self.mqtt_client.on_subscribe = self.__on_subscribe
        # self.mqtt_client.on_unsubscribe = self.__on_unsubscribe
        # self.mqtt_client.on_publish = self.__on_publish
        # self.mqtt_client.on_log = self.__on_log

        self.mqtt_client.on_socket_open = self.__on_socket_open
        self.mqtt_client.on_socket_close = self.__on_socket_close
        self.mqtt_client.on_socket_register_write = self.__on_socket_register_write
        self.mqtt_client.on_socket_unregister_write = self.__on_socket_unregister_write
        self.mqtt_client.connect(self.addr, self.port, keepalive=60)

        # Go connecting state
        self.__state = 'connecting'
        self.log.info("Connecting...")

    # ---

    async def __state_connecting(self):
        """Running state
        """
        await asyncio.sleep(0.5)

    # ---

    async def __state_running(self):
        """Running state
        """
        # Make sure subscribes are done after the connection
        for entry in self.__listeners.entries:
            if not entry.subscribed:
                self.log.debug(f"subscribe topic '{entry.topic}'")
                self.mqtt_client.subscribe(entry.topic)
                entry.subscribed = True

    # ---

    async def __state_error(self):
        """
        """
        await asyncio.sleep(1)

    # ---

    async def __state_disconnecting(self):
        """
        """
        await asyncio.sleep(1)

    # =============================================================================
    # CLIENT CALLBACKS

    # ---

    def __on_connect(self, client, userdata, flags, rc):
        """On connect callback
        """
        if self.__state == 'connecting':
            self.__state = 'running'
            self.log.info(f"Connected ! ({str(rc)})")
        else:
            self.log.warning(f"Wierd connection status ? ({str(rc)})")

    # ---

    def __on_disconnect(self, client, userdata, flags, rc):
        self.log.warning(f"Disconnected !")
    
    # ---

    def __on_subscribe(self, client, userdata, mid, granted_qos):
        self.log.warning(f"__on_subscribe")
    
    # ---
    
    def __on_unsubscribe(self, userdata, mid):
        self.log.warning(f"__on_unsubscribe")
    
    # ---

    def __on_publish(self, client, userdata, result):
        self.log.warning(f"__on_publish({result})")

    # ---

    def __on_log(self, client, userdata, level, buff):
        self.log.warning(f"__on_log({level}, {buff})")

    # ---

    def __on_message(self, client, userdata, msg):
        """Callback to manage incomming mqtt messages

        Args:
            - client: from paho.mqtt.client
            - userdata: from paho.mqtt.client
            - msg: from paho.mqtt.client
        """
        # Get the topix string
        topic_string = str(msg.topic)

        # Debug purpose
        self.log.info(f"MSG_IN < %{topic_string}% {msg.payload}")

        self.__listeners.trigger_callbacks(topic_string, msg.payload)

    # ---

    async def misc_loop(self):
        self.log.debug("misc_loop started")
        while self.client.loop_misc() == mqtt.MQTT_ERR_SUCCESS:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
        self.log.debug("misc_loop finished")

    # ---

    def __on_socket_open(self, client, userdata, sock):
        self.log.debug("Socket opened")

        def cb():
            # Debug
            # self.log.debug("Socket is readable, calling loop_read")
            client.loop_read()

        asyncio.get_event_loop().add_reader(sock, cb)
        self.misc = asyncio.get_event_loop().create_task(self.misc_loop())

    # ---

    def __on_socket_close(self, client, userdata, sock):
        asyncio.get_event_loop().remove_reader(sock)
        self.misc.cancel()

        self.log.warning("Socket closed")

        # self.__state = "error"
        # self.worker_panic()

    # ---

    def __on_socket_register_write(self, client, userdata, sock):
        # Debug
        # self.log.debug("Watching socket for writability.")

        def cb():
            # Debug
            # self.log.debug("Socket is writable, calling loop_write")
            client.loop_write()

        asyncio.get_event_loop().add_writer(sock, cb)

    # ---

    def __on_socket_unregister_write(self, client, userdata, sock):
        # Debug
        # self.log.debug("Stop watching socket for writability.")
        asyncio.get_event_loop().remove_writer(sock)

    # ---
