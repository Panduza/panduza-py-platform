# Test for serial tty

Tests performed with an arduino in echo mode

```c
void setup() {
  Serial.begin(9600); // Set the baud rate of the serial communication
}

void loop() {
  while (Serial.available()) { // Check if there is any data available on the serial port
    char incomingByte = Serial.read(); // Read the incoming byte
    Serial.write(incomingByte); // Send the incoming byte back out the serial port
  }
}
```

