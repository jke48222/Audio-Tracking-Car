"""
The main code file that houses the dip switch controls,
and will call the different functions depending on the input state
Dependent files include rpm_motor_controller, adc_logic, figure_drawing, and audio_tracking

"""


from gpiozero import Button, LED
from gpiozero.tools import negated
import time
import figure_drawing as fd
import audio_tracking as at
import adc_logic as adc


# create button classes for the dip switch
DIP_bit_2 = Button(19, bounce_time=.3)  # the audio or draw bit
DIP_bit_1 = Button(13, bounce_time=.3)  # subcategory
DIP_bit_3 = Button(26, bounce_time=.3)  # the stop or go bit
DIP_bit_0 = Button(6,  bounce_time=.3)  # subcategory


# create led class for the matching LEDS
DIP_LED_3 = LED(21)  # red
DIP_LED_2 = LED(20)  # yellow
DIP_LED_1 = LED(16)  # blue
DIP_LED_0 = LED(12)  # green


state_dict = {0: "Don't Move", 1: "single", 2: "multiple",
              3: "straight", 4: "figure 8", 5: "square", 6: "debug", 7: "nothing"}


class BitMap():
    def __init__(self):
        """
        Holds the states of the 4 different bits to update the output function
        """
        self.state = 0
        self.bit_3 = bool(DIP_bit_3.value)
        self.bit_2 = bool(DIP_bit_2.value)
        self.bit_1 = bool(DIP_bit_1.value)
        self.bit_0 = bool(DIP_bit_0.value)

    def change_state(self):
        """check the state of the combined bits to set the output state for the actions for the cars"""
        self.bit_3 = bool(DIP_bit_3.value)
        self.bit_2 = bool(DIP_bit_2.value)
        self.bit_1 = bool(DIP_bit_1.value)
        self.bit_0 = bool(DIP_bit_0.value)

        # creates a 3-bit binary to check the states
        bit_list = (self.bit_2, self.bit_1, self.bit_0)
        if self.bit_3 == False:
            match bit_list:
                case (False, False, False):
                    self.state = 1
                case (False, False, True):
                    self.state = 2
                case (False, True, False):
                    self.state = 7
                case (False, True, True):
                    self.state = 7
                case (True, False, False):
                    self.state = 3
                case (True, False, True):
                    self.state = 4
                case (True, True, False):
                    self.state = 5
                case (True, True, True):
                    self.state = 6
                case _:  # this is a catch all in none of the others worked
                    self.state = 0

            # prints the state as it changes in real time
            print(state_dict[self.state])


def led_setup():
    # used to reference the bitmap functions
    DIP_LED_3.source = DIP_bit_3
    DIP_LED_2.source = DIP_bit_2
    DIP_LED_1.source = DIP_bit_1
    DIP_LED_0.source = DIP_bit_0
    bit_map.change_state()  # makes sure the LEDs match on startup

def adc_c8_led():
    DIP_LED_3.source = negated(adc.right_adc1)
    DIP_LED_2.source = negated(adc.right_adc1)
    DIP_LED_1.source = negated(adc.right_adc3)
    DIP_LED_0.source = negated(adc.right_adc4)
    

def adc_c6_led():
    DIP_LED_3.source = negated(adc.left_adc1)
    DIP_LED_2.source = negated(adc.left_adc2)
    DIP_LED_1.source = negated(adc.left_adc3)
    DIP_LED_0.source = negated(adc.left_adc4)

def switch_setup():
    # callback functions to update the bitmap
    for button in [DIP_bit_0, DIP_bit_1, DIP_bit_2, DIP_bit_3]:
        button.when_activated = bit_map.change_state
        button.when_deactivated = bit_map.change_state


def main_loop():
    """Main loop that handles the dip switch input, and 6 state output"""
    try:
        while True:
            print("Waiting on input")
            DIP_bit_3.wait_for_active(10)  # stands by waiting for bit 3

            while bit_map.bit_3:
                print("3")
                # three second grace period to un-flip bit 3 or run away before it drives
                time.sleep(1)
                print("2")
                time.sleep(1)
                print("1")
                time.sleep(1)
                if DIP_bit_3.value == 0:  # checks to cancel if bit was flipped, acting as a debounce method
                    print("Canceled")
                    break
                bit_map.change_state()

                try:
                    match bit_map.state:  # main function choices to execute code
                        case 1:
                            # Single audio tracking
                            adc_c8_led()
                            at.single_source(adc.adc_c8)
                        case 2:
                            # Multiple audio tracking
                            adc_c8_led()
                            at.multiple_source(adc.adc_c8)
                            adc_c6_led()
                            at.multiple_source(adc.adc_c6)
                        case 3:
                            # straight
                            fd.straight()
                        case 4:
                            # Figure 8
                            fd.figure_8()
                        case 5:
                            # Square
                            fd.square()
                        case 6:
                            # debug, for checking gain on mics
                            print("checking c8")
                            adc_c8_led()
                            adc.adc_level_check(adc.adc_c8)
                            print("next frequency C^")
                            time.sleep(2)
                            adc_c6_led()
                            adc.adc_level_check(adc.adc_c6)

                        case 7:
                            print("Not assigned, still didn't moved")
                        case _:
                            # usually can happen on startup
                            print("something is wrong, nothing happened . . .")

                except:
                    # if a function fails it doesn't break the loop
                    print("error try again")
                led_setup()
                print("Complete, please reset")  # always triggers unless break
                DIP_bit_3.wait_for_inactive()  # have to unset bit 3 to re-loop

    except:
        print("\nExiting...")


bit_map = BitMap()  # main class object created that is referenced for all of the decisions


if __name__ == "__main__":  # only runs the code when this file in run directly, great for imports later if needed
    print("startup")
    led_setup()
    switch_setup()
    main_loop()
