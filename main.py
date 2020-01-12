# Trinket IO demo
# Welcome to CircuitPython 3.1.1 :)

import time
import busio
import board
import random
import digitalio
import adafruit_trellis

import adafruit_ht16k33.segments

i2c = busio.I2C(board.SCL, board.SDA)
trellis = adafruit_trellis.Trellis(i2c)
display = adafruit_ht16k33.segments.Seg14x4(i2c, address=0x72)

# Button
button = digitalio.DigitalInOut(board.D3)
button.switch_to_input(pull=digitalio.Pull.UP)

trellis.led.fill(True)
display.fill(0)
display.show()

# Defines
FREE = 0
GAME = 1
ADD = 2
MULT = 3
CALC = 4
MODES = [FREE, GAME, ADD]
MODE = ADD


def logic_free():
    """ Free play

    Trellis button press changes LED state.
    """
    try:
        just_pressed, released = trellis.read_buttons()
        for b in just_pressed:
            print('pressed:', b)
            # trellis.led[b] = True
            trellis.led[b] = not trellis.led[b]
        pressed_buttons.update(just_pressed)
        for b in released:
            print('released:', b)
            # trellis.led[b] = False
        pressed_buttons.difference_update(released)
        for b in pressed_buttons:
            print('still pressed:', b)
            # trellis.led[b] = True
    except Exception as ex:
        print("exception with trellis: ", ex)

    try:
        display.print("FREE")
    except Exception as ex:
        print("exception with ht16k33: ", ex)


def game_button_press(b):
    """ Invert button b and neighbors.
    """
    print("game button: ", b)
    # Convert button index to row and column
    i = b // 4
    j = b % 4
    # Get coordinates of button and neighbors
    px = [(i, j), (i-1, j), (i+1, j), (i, j-1), (i, j+1)]
    for (i, j) in px:
        if (0 <= i) and (i < 4) and (0 <= j) and (j < 4):
            idx = (i * 4) + j
            trellis.led[idx] = not trellis.led[idx]


def init_game():
    """ Create a new random game board.

    "press" a random button between 8-12 times
    """
    trellis.led.fill(True)
    for press in range(random.randint(8, 13)):
        b = random.randint(0, 16)
        game_button_press(b)
        display.print(press)
        time.sleep(0.2)


def logic_game():
    """ Game play

    Trellis button press inverts button and neighbors.
    """
    try:
        just_pressed, released = trellis.read_buttons()
        for b in just_pressed:
            pass
        pressed_buttons.update(just_pressed)
        for b in released:
            game_button_press(b)
        pressed_buttons.difference_update(released)
        for b in pressed_buttons:
            pass
    except Exception as ex:
        print("exception with trellis: ", ex)

    try:
        display.print("GAME")
    except Exception as ex:
        print("exception with ht16k33: ", ex)


def init_add():
    """ Create a new addition problem

    Choose a + b = c such that a, b < 10, and c <= 16
    """
    trellis.led.fill(False)
    a = random.randint(1, 10)
    b = random.randint(1, 16-a)
    if b > 9:
        b = 9
    display.print("{a:d}+{b:d}=".format(a=a, b=b))
    print(a, b, a+b)
    return a+b


def get_active():
    """ Return an array of pressed buttons.
    """
    return [ii for ii in range(16) if trellis.led[ii]]


def logic_add(c):
    """ Game play

    Trellis button press inverts button and neighbors.
    """
    try:
        just_pressed, released = trellis.read_buttons()
        for b in just_pressed:
            trellis.led[b] = not trellis.led[b]
        pressed_buttons.update(just_pressed)
        for b in released:
            pass
        pressed_buttons.difference_update(released)
        for b in pressed_buttons:
            pass
    except Exception as ex:
        print("exception with trellis: ", ex)

    active = get_active()
    print(len(active), c, active)
    if len(active) == c:
        try:
            display.print(" ={c:2d}".format(c=c))
        except Exception as ex:
            print("exception with ht16k33: ", ex)
        time.sleep(1)
        blink_win(active)


# init_game()
c = init_add()
pressed_buttons = set()
while True:
    # Check for mode increment

    if MODE == FREE:
        logic_free()
    elif MODE == GAME:
        logic_game()
    elif MODE == ADD:
        logic_add(c)

    time.sleep(.1)
