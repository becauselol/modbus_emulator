import serial

# Replace '/dev/ttyUSB0' with the appropriate serial port on your system
ser = serial.Serial('/dev/ttyUSB0', 9600)  # Adjust baudrate as needed

try:
    while True:
        # Read a line of data from the serial port
        data = ser.readline().decode().strip()
        
        # Do something with the received data
        print("Received:", data)

except KeyboardInterrupt:
    # Close the serial port when Ctrl+C is pressed
    ser.close()
