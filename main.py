import socketio
from time import sleep
from chafon_rfid.transport_serial import SerialTransport
from chafon_rfid.base import CommandRunner
from config.settings import WS_API_URL, RELAY_PIN, BUTTON_PIN, FRIDGE_ID, PORT, RUNNING_MODE

if RUNNING_MODE == 'prod':
    from reader import get_tags
    from gpiozero import OutputDevice, Button


SENDER = ""

if RUNNING_MODE == 'prod':
    transport = SerialTransport(device=PORT)

button = Button(BUTTON_PIN)
relay = OutputDevice(RELAY_PIN, active_high=False, initial_value=False)

sio = socketio.Client()


@sio.event
def connect():
    sio.emit("join", {"clientId": FRIDGE_ID})
    print("Connected!")


@sio.event
def connect_error():
    print("The connection failed!")


@sio.event
def disconnect():
    print("Disconnected!")


@sio.on('open')
def on_open(data):
    global SENDER

    SENDER = data['sender']

    relay.on()
    sio.emit('direct', {
        'sender': FRIDGE_ID,
        'receiver': SENDER,
        'signal': 'locked',
        'state': False
    })

    sleep(3)

    relay.off()
    sio.emit('direct', {
        'sender': FRIDGE_ID,
        'receiver': SENDER,
        'signal': 'locked',
        'state': True
    })


def on_door_close():
    sio.emit('direct', {
        'sender': FRIDGE_ID,
        'receiver': SENDER,
        'signal': 'closed',
        'state': button.is_pressed
    })


def on_door_open():
    sio.emit('direct', {
        'sender': FRIDGE_ID,
        'receiver': SENDER,
        'signal': 'closed',
        'state': button.is_pressed
    })


def listen_gpio():
    button.when_pressed = on_door_close
    button.when_released = on_door_open


if __name__ == '__main__':
    sio.connect(WS_API_URL)
    task = sio.start_background_task(listen_gpio)
    sio.wait()
