""" 
Different driving functions performed by the car
Including straight, stop, turn_90_left, square, and figure 8
functions
"""

import time
import rpm_motor_controller as rpm_mc


def stop():
    """
    Stops the car and sleeps .2 seconds. Always important
    """
    rpm_mc.audio_car.stop()
    time.sleep(.2)


def straight():
    """
    drives the car 3 ft forward straight
    """
    rpm_mc.setup()
    rpm_mc.left_rpm.set_target(100)
    rpm_mc.right_rpm.set_target(100)
    time_start = time.time()
    while True:
        dt = time.time() - time_start
        rpm_mc.calculate_rpm()
        if dt > 3:
            break
    stop()


def turn_90_left():
    """
    Turns 90 deg left
    """
    rpm_mc.setup()
    rpm_mc.left_rpm.set_target(100)
    rpm_mc.right_rpm.set_target(-100)
    time_start = time.time()
    while True:
        dt = time.time() - time_start
        rpm_mc.calculate_rpm()
        if dt > .55:  # drives for enough seconds to turn
            break

def square():
    """
    Uses the straight and 90 deg functions to draw a square 2x

    """
    for i in range(8):
        straight()
        turn_90_left()
    stop()


def figure_8():
    """
    Uses the straight function and a curve to draw figure_8 2x

    """

    for i in range(2):
        straight()
        rpm_mc.audio_car.forward(curve_left=.5)
        time.sleep(5)
        stop()
        straight()
        rpm_mc.audio_car.forward(curve_right=.5)
        time.sleep(5)
    stop()
