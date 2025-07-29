from machine import Pin
import time

# --- CONFIGURATION ---

KILL_SWITCH_PIN = 2   # Replace with your actual pin number for kill switch
LED_PIN = 0           # Replace with your actual pin number for LED
DEBOUNCE_TIME = 50    # ms
HOLD_TIME = 1000      # ms

# --- SETUP ---

kill_switch = Pin(KILL_SWITCH_PIN, Pin.IN, Pin.PULL_UP)
led = Pin(LED_PIN, Pin.OUT)

muted = False
last_button_state = 1
last_debounce_time = 0
button_pressed_time = 0
holding = False

def set_mute(state):
    global muted
    muted = state
    led.value(1 if muted else 0)  # LED ON = muted

# --- MAIN LOOP ---

print("Smart Kill Switch Firmware Running")

while True:
    now = time.ticks_ms()
    reading = kill_switch.value()

    # Detect edge with debounce
    if reading != last_button_state:
        last_debounce_time = now

    if (now - last_debounce_time) > DEBOUNCE_TIME:
        if reading == 0 and not holding:
            # Button pressed — start timing
            if button_pressed_time == 0:
                button_pressed_time = now
        elif reading == 1:
            # Button released
            if holding:
                # Just ended a hold
                holding = False
                button_pressed_time = 0
            elif button_pressed_time != 0:
                # Short press → toggle mute
                set_mute(not muted)
                print("Toggled mute:", muted)
                button_pressed_time = 0

    # Check for long hold
    if button_pressed_time and not holding:
        if (now - button_pressed_time) > HOLD_TIME:
            print("Hold detected — flashing LED")
            holding = True
            # Blink LED rapidly while held
            for _ in range(5):
                led.value(1)
                time.sleep(0.1)
                led.value(0)
                time.sleep(0.1)
            set_mute(False)  # Optional: unmute after hold

    last_button_state = reading
    time.sleep(0.01)
