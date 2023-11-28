from .spi_master_base import ConnectorSPIMasterBase

import aardvark_py


class ConnectorSPIMasterAardvark(ConnectorSPIMasterBase):
    """The aardvark spi client connector
    """

    # Contains instances
    __instances = {}

    ###########################################################################
    ###########################################################################

    @staticmethod
    def aardvark_find_unique_id():
        n, devices = aardvark_py.aa_find_devices(10)
        id_list = {}
        for device in range(n):
            if (devices[device] & aardvark_py.AA_PORT_NOT_FREE):
                devices[device] = None
                continue

            handle = aardvark_py.aa_open(devices[device])
            id_list.update({device: aardvark_py.aa_unique_id(handle)})
            aardvark_py.aa_close(handle)

        return id_list

    # WARNING : bitorder argument is not used
    # It seems unsuported by pyftdi
    @staticmethod
    def Get(**kwargs):
        """
        Singleton main getter
        Get metadata to identify device (vendor_id, product_id ...)
        Returns the corresponding connector instance
        """
        unique_id = kwargs.get("unique_id", None)
        frequency = kwargs.get("frequency", 125)
        cs_count = kwargs.get("cs_count", 1)
        polarity = kwargs.get("polarity", 0)
        phase = kwargs.get("phase", 0)
        bitorder = kwargs.get("bitorder", 0)

        candidates = ConnectorSPIMasterAardvark.aardvark_find_unique_id()
        
        if unique_id is not None:
            instance_name = unique_id
            port = list(candidates.keys())[list(candidates.values()).index(int(unique_id))]
        elif len(candidates) == 1:
            instance_name = candidates[0]
            port = 0
        else:
            raise Exception(
                f"{len(candidates)} devices detected: please specify unique_id")

        # Create the new connector
        if not (instance_name in ConnectorSPIMasterAardvark.__instances):
            ConnectorSPIMasterAardvark.__instances[instance_name] = None
        else:
            raise Exception(f'trying to configure an instance already existing')
        try:
            new_instance = ConnectorSPIMasterAardvark(key=instance_name,
                                                      port=port,
                                                      bitrate_khz=frequency,
                                                      cs_count=cs_count,
                                                      polarity=polarity,
                                                      phase=phase, 
                                                      bitorder=bitorder)
            ConnectorSPIMasterAardvark.__instances[instance_name] = new_instance
        except Exception as e:
            ConnectorSPIMasterAardvark.__instances.pop(instance_name)
            raise Exception('Error during initialization').with_traceback(
                e.__traceback__)

        # Return the previously created
        return ConnectorSPIMasterAardvark.__instances[instance_name]

    def __init__(self, **kwargs):
        """
        Constructor
        """

        key = kwargs.get('key', None)
        port = kwargs.get('port', 0)
        bitrate_khz = kwargs.get('bitrate_khz', 125)
        cs_count = kwargs.get('cs_count', 1)
        polarity = kwargs.get('polarity', 0)
        phase = kwargs.get('phase', 0)
        bitorder = kwargs.get('bitorder', 0)

        if not (key in ConnectorSPIMasterAardvark.__instances):
            raise Exception(
                "You need to pass through Get method to create an instance")
        else:
            self.log = logger.bind(driver_name=key)
            self.log.info(f"attached to the Aardvark SPI Serial Connector")

        # creates the spi master
        self.spi = aardvark_py.aa_open(port)
        aardvark_py.aa_spi_configure(self.spi, polarity, phase, bitorder)
        aardvark_py.aa_spi_bitrate(self.spi, bitrate_khz)
        

        # TODO add multiple slaves support
        # the connector only handles masters with a single slave
        # should give in args an array for freq and mode for all spi slaves

        # self.slaves = []
        # for i in range(0, cs_count):
        #         self.slaves.append(self.spi_master.get_port(cs = i, freq = frequency[i], mode = mode[i]))

        # disconnect device
        # TODO close spi
        # self.client.close(freeze = true)

    # TODO should add the cs value in these functions

    def spi_transfer(self, data):
        """
        Write function of the connector
        Calls the write function of the driver
        """
        from array import array
        rx = aardvark_py.array_u08(len(data))
        tx = array('B', data)
        
        status, rx = aardvark_py.aa_spi_write(self.spi, tx, rx)
        if status < 0:
            self.log.error("aardvark error")
        return list(rx)

    def hunt():
        raise Exception("NOT IMPLEMENTED")