# Platform Design

## 

The platform can dynamically mount and unmount:

- MQTT Clients
- Test Benches
- Devices (mounting device will load attached interfaces, unmounting device will unload them)




## Starting sequence

- start the running event loop
- connect a primary client to the primary broker (defined in the platform admin config)
- mount device 'machine' for this server
- read actif tree and mount each device



