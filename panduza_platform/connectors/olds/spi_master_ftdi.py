# Functions called by spi_master_base for ftdi chips

from .spi_master_base import ConnectorSPIMasterBase
import pyftdi.spi as Spi
from pyftdi.ftdi import Ftdi
from pyftdi.usbtools import UsbToolsError
from .udev_tty import HuntUsbDevs


# enum SpiPolarity
SPI_POL_RISING_FALLING = 0
SPI_POL_FALLING_RISING = 1

# enum SpiPhase
SPI_PHASE_SAMPLE_SETUP = 0
SPI_PHASE_SETUP_SAMPLE = 1

# enum SpiBitorder
SPI_BITORDER_MSB = 0
SPI_BITORDER_LSB = 1


class ConnectorSPIMasterFTDI(ConnectorSPIMasterBase):
    """The FtdiSpi client connector
    """

    # Contains instances
    __instances = {}

    ###########################################################################
    ###########################################################################

    # WARNING : bitorder argument is not used
    # It seems unsuported by pyftdi
    @staticmethod
    def Get(**kwargs):
        """
        Singleton main getter
        Get metadata to identify device (vendor_id, product_id ...)
        Returns the corresponding connector instance
        """
        usb_vendor_id = kwargs.get('usb_vendor_id', None)
        usb_product_id = kwargs.get('usb_product_id', None)
        usb_serial_id = kwargs.get('usb_serial_id', None)
        frequency = kwargs.get('frequency', 1E6)
        cs_count = kwargs.get('cs_count', 1)
        polarity = kwargs.get('polarity', SPI_POL_RISING_FALLING)
        phase = kwargs.get('phase', SPI_PHASE_SAMPLE_SETUP)
        bitorder = kwargs.get('bitorder', SPI_BITORDER_MSB)
        port = kwargs.get('port', 1)

        if usb_serial_id is not None:
            instance_name = usb_serial_id
        elif usb_vendor_id != None and usb_product_id != None:
            candidates = HuntUsbDevs(
                usb_vendor_id, model=usb_product_id, subsystem='usb')
            if len(candidates) == 1:
                instance_name = candidates[0].get('ID_SERIAL_SHORT')
            else:
                raise Exception(
                    "too many possible devices detected: please specify usb_serial")
        else:
            raise Exception("no way to identify the SPI port")

        # Create the new connector
        if not (instance_name in ConnectorSPIMasterFTDI.__instances):
            ConnectorSPIMasterFTDI.__instances[instance_name] = None
        else:
            raise Exception(
                'trying to configure an instance already existing')
        try:
            new_instance = ConnectorSPIMasterFTDI(key=instance_name,
                                                  usb_serial_id=usb_serial_id,
                                                  port=port,
                                                  frequency=frequency,
                                                  cs_count=cs_count,
                                                  polarity=SPI_POL_RISING_FALLING,
                                                  phase=SPI_PHASE_SAMPLE_SETUP)
            ConnectorSPIMasterFTDI.__instances[instance_name] = new_instance
        except Exception as e:
            ConnectorSPIMasterFTDI.__instances.pop(instance_name)
            raise Exception('Error during initialization').with_traceback(
                e.__traceback__)

        # Return the previously created
        return ConnectorSPIMasterFTDI.__instances[instance_name]

    def __init__(self, **kwargs):
        """Constructor
        """
        
        key = kwargs.get('key', None)
        usb_serial_id = kwargs.get('usb_serial_id', None)
        frequency = kwargs.get('frequency', 1E6)
        cs_count = kwargs.get('cs_count', 1)
        polarity = kwargs.get('polarity', SPI_POL_RISING_FALLING)
        phase = kwargs.get('phase', SPI_PHASE_SAMPLE_SETUP)
        port = kwargs.get('port', 1)
        
        if not (key in ConnectorSPIMasterFTDI.__instances):
            raise Exception(
                "You need to pass through Get method to create an instance")
        else:
            self.log = logger.bind(driver_name=key)
            self.log.info(f"attached to the FTDI SPI Serial Connector")

        # creates the spi master
        self.spi_master = Spi.SpiController(cs_count=cs_count)

        self.spi_master.configure(
            f'ftdi://ftdi:{usb_serial_id}/{port}', frequency=frequency)

        # get port for SPI
        mode = (polarity << 1) | phase

        # get_port creates a port whose number is cs and its parameters are the following args
        self.spi = self.spi_master.get_port(cs=0, freq=frequency, mode=mode)

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
        return self.spi.exchange(data, len(data), duplex=True)

    def hunt():
        raise Exception("NOT IMPLEMENTED")