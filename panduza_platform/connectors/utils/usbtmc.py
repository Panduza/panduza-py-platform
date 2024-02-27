import usbtmc
import logging

def HuntUsbtmcDevs(usb_vendor, usb_model=None):
    """Return a list with devices fond with those criterias
    """
    results = []

    # Explore usbtmc devices
    usbtmc_devices = usbtmc.list_devices()

    # 
    for device in usbtmc_devices:
        
        if usb_vendor is not None and device.idVendor != usb_vendor:
            continue
        if usb_model is not None and device.idProduct != usb_model :
            continue

        results.append(device)
        # For debugging purpose
        # logger.debug(f"{properties}")

    return results


def FindUsbtmcDev(usb_vendor, usb_model=None, usb_serial_short=None):
    
    availables = HuntUsbtmcDevs(usb_vendor, usb_model)
    for dev in availables:
        # Check serial if required
        if usb_serial_short != None:
            if dev.serial_number == usb_serial_short:
                return dev
        
        # Else return the first in the list
        else:
            return dev
    
    return None


