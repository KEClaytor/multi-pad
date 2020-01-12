# Trellis pad with 14-segement display

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

class Button():
    """ Button convience class.

    Create a button:
    >>> button = Button(board.D3, digitalio.Pull.UP)
    Update the button state:
    >>> button.update()
    And then check for conditions:
    >>> if button.pressed():
    >>>     ...
    >>> if button.just_pressed():
    >>>     ...
    >>> if button.just_released():
    >>>     ...
    """

    def __init__(self, pin, mode):
        """ Create a new Button.
        """
        self.button = digitalio.DigitalInOut(pin)
        self.button.switch_to_input(pull=mode)
        self.mode = mode
        self.last_state = False
        self.state = False

    def update(self):
        """ Read the current button state and update internal state.
        """
        # Update the last state
        self.last_state = self.state
        # Read the current state
        if self.mode == digitalio.Pull.DOWN:
            self.state = self.button.value
        elif self.mode == digitalio.Pull.UP:
            self.state = not self.button.value
        # Update the pressed / released states
        self.edge_up = self.state and not self.last_state
        self.edge_down = not self.state and self.last_state

    def pressed(self):
        """ Returns true if currently pressed.
        """
        return self.state

    def just_pressed(self):
        """ Returns true if just pressed
        True for released -> pressed transition.
        """
        return self.edge_up

    def just_released(self):
        """ Returns true if just released
        True for pressed -> released transition.
        """
        return self.edge_down


# Button
button_mode = Button(board.D3, digitalio.Pull.UP)
button_sel = Button(board.D4, digitalio.Pull.UP)

trellis.led.fill(True)

# Defines
MODE = 0
FREE = 0
GAME = 1
ADD = 2
SUB = 3
MODE_LABELS = ["FREE", "GAME", "ADD ", "SUB "]
addition_goal = 16
subtraction_goal = 16


def init_free():
    trellis.led.fill(False)


def logic_free():
    """ Free play

    Trellis button press changes LED state.
    """
    just_pressed, released = trellis.read_buttons()
    for b in just_pressed:
        trellis.led[b] = not trellis.led[b]


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
    just_pressed, released = trellis.read_buttons()
    for b in just_pressed:
        game_button_press(b)


def init_add():
    """ Create a new addition problem

    Choose a + b = c such that a, b < 10, and c <= 16
    These conditions ensure that "a+b=" is pritable, and reachable
    """
    global addition_goal

    trellis.led.fill(False)
    a = random.randint(1, 10)
    b = random.randint(1, 16-a)
    if b > 9:
        b = 9
    c = a + b
    display.print("{a:d}+{b:d}=".format(a=a, b=b))
    print(a, b, c)
    addition_goal = c


def get_active():
    """ Return an array of pressed buttons.
    """
    return [ii for ii in range(16) if trellis.led[ii]]


def logic_add():
    """ Game play

    Toggle buttons and see if we "win".
    """
    global addition_goal

    just_pressed, released = trellis.read_buttons()
    for b in just_pressed:
        trellis.led[b] = not trellis.led[b]

    active = get_active()
    print(len(active), addition_goal)
    if len(active) == addition_goal:
        display.print(" ={c:2d}".format(c=addition_goal))
        for b in range(16):
            trellis.led[b] = not trellis.led[b]


def init_sub():
    """ Create a new subtraction problem

    Choose a - b = c such that a > 1, b > 0, and c > 0
    """
    global subtraction_goal

    trellis.led.fill(False)
    a = random.randint(1, 10)
    b = random.randint(0, a)
    c = a - b
    display.print("{a:d}-{b:d}=".format(a=a, b=b))
    print(a, b, c)
    subtraction_goal = c


def logic_sub():
    """ Game play

    Toggle buttons and see if we "win".
    """
    global subtraction_goal

    just_pressed, released = trellis.read_buttons()
    for b in just_pressed:
        trellis.led[b] = not trellis.led[b]

    active = get_active()
    if len(active) == subtraction_goal:
        display.print(" ={c:2d}".format(c=subtraction_goal))
        for b in range(16):
            trellis.led[b] = not trellis.led[b]


def init():
    """ Initalize the given mode.
    """
    if MODE == FREE:
        init_free()
    elif MODE == GAME:
        init_game()
    elif MODE == ADD:
        init_add()
    elif MODE == SUB:
        init_sub()


init()
display.print(MODE_LABELS[MODE])
pressed_buttons = set()
while True:
    # Change modes
    button_mode.update()
    button_sel.update()

    if button_mode.pressed():
        if button_sel.just_released():
            MODE = (MODE + 1) % len(MODE_LABELS)
        display.print(MODE_LABELS[MODE])
    else:
        if button_mode.just_released() or button_sel.just_released():
            init()

    # Main logic
    if MODE == FREE:
        logic_free()
    elif MODE == GAME:
        logic_game()
    elif MODE == ADD:
        logic_add()
    elif MODE == SUB:
        logic_sub()

    time.sleep(.1)
