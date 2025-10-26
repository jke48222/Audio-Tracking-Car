"""
Houses the single and the multiple source audio tracking functions, as well as dependent functions 
including rotate and align, and max value angle. (great name btw)
"""

import time
from adc_logic import adc_c6, adc_c8, ADC, bump_switch, BumpSwitchException
from rpm_motor_controller import audio_car, left_motor, right_motor


def max_value_angle(values):
    """
    Takes a list input, finds the maximum value levels, and return the location of the middle value for the list.

    """
    max_value = max(values)  # finds that max signal strength that was measured
    # returns a list of the locations of the max values
    max_indices = [i for i, value in enumerate(values) if value == max_value]
    print(max_indices)
    if len(max_indices) > 1:
        # returns the location of the middle value, the probable location of the audio source
        middle_max = max_indices[len(max_indices) // 2]
    else:
        middle_max = (max_indices[0])  # If list was 1 long, returns itself

    # calculates the "angle" of the value relative to the length of the list
    return (middle_max/len(values))


def rotate_and_align(adc: ADC, seconds, hard_adjustment=0):
    """
    Spins for a duration collecting adc data. Then calculates the max value and turns back to face the direction of the max strength
    If needed, can input hard adjustment to compensate for motor acceleration
    """
    left_motor.backward(.8)  # creates a spin in place movement
    right_motor.forward(.8)
    adc_data = []  # list that stores the history of the adc values
    counts = seconds * 20
    for t in range(1, counts):  # runs 20 times a second, for duration of the circle
        # bump switch break
        if bump_switch.value == True:
            # breaks the loop, if needed
            break
        adc_data.append(adc.adc_value())  # iteratively constructs the list
        time.sleep(.05)

    audio_car.stop()  # small pause
    time.sleep(.5)
    print(f"max value angle is {max_value_angle(adc_data)}")
    print(f"turning {seconds*(1 - (max_value_angle(adc_data)))} seconds")

    # calculates the seconds the turn to line up with the highest signal strength
    # takes the "angle" and translates it to seconds to turn back to face the source
    rotation_correction = seconds*(1 - (max_value_angle(adc_data)))

    # activates the motors, spins them in the reversed direction of the circle
    left_motor.forward(.8)
    right_motor.backward(.8)

    # timing to line up to the audio source
    time.sleep(rotation_correction + hard_adjustment)
    audio_car.stop()


def single_source(adc):
    """
    Uses the rotate_and_align function with the C8 adc, then drives straight until bump switch activation
    """

    # input seconds to turn and check for sources, should be about 1 rotation
    rotate_and_align(adc, 2)
    time.sleep(.5)
    try:
        audio_car.forward()
        while True:
            if bump_switch.value == True:
                raise BumpSwitchException()
            time.sleep(0.1)

    finally:  # stops the car at its destination
        audio_car.stop()


def multiple_source(adc):
    """
    First uses rotate_and_align with C8 to drive towards the source. Then backs up to the center and repeats with C6
    Backs up once complete
    """

    # Input seconds to rotate, should be about 1 full rotation
    rotate_and_align(adc, 2)
    time.sleep(.5)
    try:
        start_time = time.time()  # timing to make it back to the center
        audio_car.forward()
        while True:
            if bump_switch.value == True:
                raise BumpSwitchException("Bump switch activated")
            time.sleep(0.1)

        # resetting the position
    except BumpSwitchException:  # this code will back up the car to reset it to the middle
        audio_car.stop()
        end_time = time.time()
        time.sleep(0.5)
        audio_car.backward()
        # backs up the same amount as it drove towards the source
        time.sleep(end_time-start_time-.5) # the .5 is to compensate to the flywheel
        audio_car.stop()
        time.sleep(0.5)


if __name__ == "__main__":
    single_source()
