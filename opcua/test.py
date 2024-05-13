from opcua import Server
from random import randint
import datetime
import time


server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:48040/freeopcua/server/")


uri = "http://example.org"
idx = server.register_namespace(uri)


obj = server.nodes.objects.add_object(idx, "MyObject")


temp = obj.add_variable(idx, "Temperature", 0)
pressure = obj.add_variable(idx, "Pressure", 0)


temp.set_writable()
pressure.set_writable()


server.start()
print("Server started at {}".format(server.endpoint))

try:
    while True:
        # Update the temperature and pressure with random values
        temperature = randint(20, 30)
        pres = randint(200, 300)

        print("Temperature: {} °C, Pressure: {} kPa".format(temperature, pres))

        # Set the values for the variables
        temp.set_value(temperature)
        pressure.set_value(pres)

        # Sleep for some time
        time.sleep(2)

except KeyboardInterrupt:
    print("Server shutdown")
    server.stop()
