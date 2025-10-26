"""
Controls how the car will move, incorporates our transfer function, 
called by the audio tracking and figure drawing files

"""

from gpiozero import Motor, CompositeOutputDevice, DigitalInputDevice, PWMOutputDevice, Robot  # type: ignore
import time
import threading

"""
old init functions, used for reference

pin_17 = PWMOutputDevice(17,frequency=100)
pin_27 = PWMOutputDevice(27,frequency=100)
pin_14 = PWMOutputDevice(14,frequency=100)
pin_15 = PWMOutputDevice(15,frequency=100)

left_motor = CompositeOutputDevice(pin_17, pin_27)
right_motor = CompositeOutputDevice(pin_14, pin_15) 

audio_car = CompositeOutputDevice(left_motor, right_motor)
"""

# using built in gpiozero libraries to assign gpio pin outs
left_motor = Motor(27, 17)
right_motor = Motor(15, 14)
left_encoder = DigitalInputDevice(22)
right_encoder = DigitalInputDevice(18)
audio_car = Robot(left_motor, right_motor)

# constants
disk_slots = 20
target_rpm = 200


class RPM():
    """
    Calculates the rpm of the functions, handles the callback of the encoders,
    and updates the speed of the motors to using the transfer function 
    """

    def __init__(self, motor: Motor, slots, rpm):
        self.rpm = 0
        self.count = 0
        self.disk_slots = slots
        self.target_rpm = rpm
        self.start_time = time.time()
        self.duty = .8
        self.motor = motor
        self.start_count = 0

    def update(self):
        """ Callback to update with the optical encoders"""
        self.count += 1

    def set_target(self, rpm):
        """ Set the new target rpm """
        self.target_rpm = rpm

    def thread(self):
        """ Run to update RPM to Update speed"""
        self.end_count = self.count 
        self.diff_count = self.end_count - self.start_count #counts the time difference
        if self.diff_count == 0 or self.diff_count < 0:
            self.diff_count = 1

        self.rpm = min(1, ((self.diff_count)/.1 * (1/20))) #using the time difference, computes the rpm
        print(f"Motor Speed : {self.rpm:.2f} RPM")
        self.start_count = self.count

        self.motor_ratio = (abs(self.target_rpm)/self.rpm)
        self.duty = max(0.1, min(1, self.motor_ratio))
        self.set_speed() # updates the speed to match the speed of the target

    def set_speed(self):
        """ Run to update speed of the motors"""
        match self.target_rpm:
            case 0:
                self.motor.value = 0
            case n if n > 0:
                self.motor.value = (self.duty)
                print(self.motor.value)
            case n if n < 0:
                print(self.motor.value)
                self.motor.value = (-self.duty)


# main inits
left_rpm = RPM(left_motor, disk_slots, target_rpm)
right_rpm = RPM(right_motor, disk_slots, target_rpm)
left_encoder.when_activated = left_rpm.update
right_encoder.when_activated = right_rpm.update


# main loop type
def calculate_rpm():
    time.sleep(.1)
    left_rpm.thread()
    right_rpm.thread()

# can be re-run the clear variables


def setup():
    left_rpm = RPM(left_motor, disk_slots, target_rpm) #inits the rpm to control the specified motors
    right_rpm = RPM(right_motor, disk_slots, target_rpm)

    left_rpm.set_speed()
    right_rpm.set_speed()

# does not always need to be called


def loop():  # test loop that prints out the current RPMs of both motors
    while True:
        time.sleep(1)
        print(left_rpm.rpm)
        print(right_rpm.rpm)


# only runs when this file is run directly
if __name__ == "__main__":
    setup()
    threading.Thread(target=calculate_rpm, daemon=True).start()
    loop()
