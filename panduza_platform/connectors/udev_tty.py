import pyudev
import logging

# True to enable deep debug logs
# ENABLE_LOCAL_DEBUG=True
ENABLE_LOCAL_DEBUG=False

# ---

def SerialPortFromUsbSetting(**kwargs):
    """Find serial port from usb settings

    :param \**kwargs:
        See below

    :Keyword Arguments:
        * *usb_vendor* (``str``) --
            ID_VENDOR_ID
        * *usb_model* (``str``) --
            ID_MODEL_ID
        * *usb_serial_short* (``str``) --
            ID_SERIAL_SHORT

    """
    # Deep debug
    if ENABLE_LOCAL_DEBUG:
        print(f"kwargs={kwargs}\n")

    # Get parameters
    usb_vendor          = None if "usb_vendor"       not in kwargs else kwargs["usb_vendor"]
    usb_model           = None if "usb_model"        not in kwargs else kwargs["usb_model"]
    usb_serial_short    = None if "usb_serial_short" not in kwargs else kwargs["usb_serial_short"]

    # Deep debug
    if ENABLE_LOCAL_DEBUG:
        print(f"usb_vendor={usb_vendor}, usb_model={usb_model}\n")

    # Basic checks
    if not usb_vendor:
        raise Exception("At least, USB vendor must be provided for this to work")

    # Explore usb device with tty subsystem
    udev_context = pyudev.Context()
    for device in udev_context.list_devices(SUBSYSTEM='tty'):
        properties = dict(device.properties)
        
        # Deep debug
        if ENABLE_LOCAL_DEBUG:
            print(f"\tproperties={properties}\n")

        # Skip if there is no vendor in the entry
        if 'ID_VENDOR_ID' not in properties or not properties['ID_VENDOR_ID'].startswith(usb_vendor):
            continue

        # Checks
        if usb_vendor and (usb_vendor != properties["ID_VENDOR_ID"]):
            if ENABLE_LOCAL_DEBUG:
                print(f"\t--bad usb_vendor!")
            continue
        if usb_model and (usb_model != properties["ID_MODEL_ID"]):
            if ENABLE_LOCAL_DEBUG:
                print(f"\t--bad usb_model!")
            continue
        if usb_serial_short and (usb_serial_short != properties["ID_SERIAL_SHORT"]):
            if ENABLE_LOCAL_DEBUG:
                print(f"\t--bad serial short!")
            continue
        
        # Return the /dev/XXXXX
        return properties["DEVNAME"]

    # Fail to find
    raise Exception(f"ERROR: device tty for [{usb_vendor}:{usb_model}:{usb_serial_short}] not found !")




def HuntUsbDevs(usb_vendor, usb_model=None, subsystem=None):
    """Return a list with devices fond with those criterias
    """
    results = []

    # Explore usb device with tty subsystem
    udev_context = pyudev.Context()

    # Convert properties
    # I don't understand how th pyudev filters works
    for device in udev_context.list_devices():
        properties = dict(device.properties)

        if usb_vendor is not None and properties.get("ID_VENDOR_ID") != usb_vendor:
            continue
        if usb_model is not None and properties.get("ID_MODEL_ID") != usb_model :
            continue
        if subsystem is not None and properties.get("SUBSYSTEM") != subsystem:
            continue

        results.append(properties)
        # For debugging purpose
        # logger.debug(f"{properties}")

    return results

