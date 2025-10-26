"""
Houses the adc class, that handles the digital logic.
Also handles the bump switch input.
Mainly called by the audio tracking file 
"""


from gpiozero import Button
from gpiozero.tools import negated
import time

left_adc1 = Button(5, bounce_time=.1,)  # currently hooked up to the C6 filter
left_adc2 = Button(11, bounce_time=.1)
left_adc3 = Button(9, bounce_time=.1)
left_adc4 = Button(10, bounce_time=.1)

right_adc1 = Button(7, bounce_time=.1)  # currently hooked up to the C8 filter
right_adc2 = Button(8, bounce_time=.1)
right_adc3 = Button(25, bounce_time=.1)
right_adc4 = Button(23, bounce_time=.1)

# bump switch is hooked up to gpio pin 4
bump_switch = Button(4, bounce_time=.01, pull_up=True)


class ADC:
    def __init__(self, level_1: Button, level_2: Button, level_3: Button, level_4: Button):
        """
        Class that takes 4 button inputs from the gpio class, and computes the strength reading of the adc.
        """
        self.level_1 = level_1
        self.level_2 = level_2
        self.level_3 = level_3
        self.level_4 = level_4
        self.value = 0
        self.update_value()  # called to match current state on startup

    def update_value(self):
        """
        Updates ADC value based on button states.
        Stores the value 0-4
        """
        self.value = sum([
            int(not self.level_1.is_active),
            int(not self.level_2.is_active),
            int(not self.level_3.is_active),
            int(not self.level_4.is_active)
        ])

    def adc_value(self):
        """
        Function to return the current adc value
        """
        self.update_value()
        print(f"level is {self.value}")
        return self.value


# class for handing the exception raised whenever the bump switch is activated
class BumpSwitchException(Exception):
    pass


def adc_level_check(adc:ADC):
    """
    Purely for testing and troubleshooting, this loop matches the led to the strength of the adc input.
    It cycles to the next adc on bump switch activation. A second press ends the loop.
    Also prints the values in to console
    """
    try:
        while True:  # continuous loop that runs until the bump switch is activated
            if bump_switch.value:
                raise BumpSwitchException
            adc.adc_value()  # checking the c8 filter first
            time.sleep(.05)
    except BumpSwitchException:
        pass


# inits to construct an adc for each of the filters
adc_c6 = ADC(left_adc1, left_adc2, left_adc3, left_adc4)
adc_c8 = ADC(right_adc1, right_adc2, right_adc3, right_adc4)

if __name__ == "__main__":  # only runs the code when this file is run directly, great for imports later
    adc_level_check()
