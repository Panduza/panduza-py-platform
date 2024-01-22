import asyncio

import time
from connectors.boundary_scan_ftdi import ConnectorBoundaryScanFtdi


device_number_1 = 1
device_number_3 = 3
pin_PA5 = "PA5"
pin_PA10 = "PA10"
pin_PC5 = "PC5"

async def nested():

    print("42")



async def blocking_io():
    print(f"start blocking_io at {time.strftime('%X')}")
    # Note that time.sleep() can be replaced with any blocking
    # IO-bound operation, such as file operations.
    for i in range (500):
        print("pok")
    print(f"blocking_io complete at {time.strftime('%X')}")



# Tâche pour l'écriture en boucle sur les broches
async def write_loop_task(connector):
   
    while True:
        
        # Écrire la valeur sur la broche
        await connector.async_write_pin(device_number_1, pin_PA5, 1)
        await connector.async_write_pin(device_number_1, pin_PA10, 1)
        await connector.async_write_pin(device_number_3, pin_PA5, 1)
        await connector.async_write_pin(device_number_3, pin_PA10, 1)


# Tâche pour la lecture de l'état des broches dès qu'une écriture est effectuée
async def read_on_write_task(connector):
    
    while True:

        await connector.async_read_pin(device_number_3,pin_PC5,"in")
        # await connector.async_read_pin(device_number_3,pin_PA5,"out")
        # await connector.async_read_pin(device_number_3,pin_PA10,"out")
        # await connector.async_read_pin(device_number_1,pin_PA5,"out")
        # await connector.async_read_pin(device_number_1,pin_PA10,"out")
        
    


async def main():
    print(f"started main at {time.strftime('%X')}")
    # Schedule nested() to run soon concurrently
    # with "main()".

    connector = ConnectorBoundaryScanFtdi()
    write_task = asyncio.create_task(write_loop_task(connector))
    read_task = asyncio.create_task(read_on_write_task(connector))

    await asyncio.gather(write_task,read_task)

    # task1 = asyncio.create_task(connector.async_read_number_of_devices())
    # await task1
   

    # await asyncio.gather(  

    #     connector.async_read_number_of_devices(),

    #     connector.async_get_idcodes(),

    #     connector.async_write_pin(1,"PA10",1),
        
    #     connector.async_write_pin(1,"PA5",1),
        
    #     connector.async_write_pin(3,"PA10",1),
        
    #     connector.async_write_pin(3,"PA5",1),
        
    #     connector.async_read_pin(3,"PC5","in"),
        
    #     connector.async_write_pin(1,"PA5",1),
        
    #     connector.async_write_pin(1,"PA10",1),
             
    # ) 
    
    print(f"finished main at {time.strftime('%X')}")




if __name__ == '__main__':
    asyncio.run(main())
