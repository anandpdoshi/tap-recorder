import serial
import requests
import sys

arduino = serial.Serial('/dev/tty.usbmodem1421', 9600, timeout=1)
print('Ready for arduino to start sending data...')

try:
    while True:
        data = arduino.readline()
        if data:
            state = data.strip().decode('utf-8').split(" = ")
            if len(state) == 2:
                command, value = state
                requests.get("http://localhost:8000/event", params={
                    "event_type": command,
                    "event_value": value
                })

except KeyboardInterrupt:
    print('')
    sys.exit(0)

finally:
    arduino.close()
