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

