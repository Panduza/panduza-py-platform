from panduza import Client

ADDR="localhost"
PORT=1883

client = Client(url=ADDR, port=PORT)
client.connect()
interfaces = client.scan_interfaces()

print("===")
for topic, info in interfaces.items():
    print(topic, " - ", info)

