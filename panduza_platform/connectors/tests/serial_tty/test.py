import asyncio
from panduza_platform.connectors.serial_tty import ConnectorSerialTty

# 
SERIALPORT="/dev/ttyACM0"
BAUDRATE=115200



async def main():
    c = await ConnectorSerialTty.Get(
        serial_port_name=SERIALPORT,
        serial_baudrate=BAUDRATE
        )

    test_string = "pok\r\n"

    print("write", test_string)
    result = await c.write_and_read_during(test_string)
    print("read", result)

    print("write", test_string)
    await c.write(test_string)
    result = await c.read_during()
    print("read", result)

    print("write", test_string)
    result = await c.write_and_read_until(test_string)
    print("read", result)

    print("write", test_string)
    await c.write(test_string)
    result = await c.read_until()
    print("read", result)

# Run test
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
