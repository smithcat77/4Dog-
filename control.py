from maestro import Controller
import time

class Wheels():

    def __init__(self):
        self.control = Controller()
        self.control.setTarget(0, 5900)
        self.control.setTarget(1, 5900)
        self.control.setAccel(0, 0)
        self.control.setAccel(1, 0)
        self.distance_scale = 42
        self.left_scale = 21
        self.right_scale = 22

    def forward(self, distance=None):
        self.control.setTarget(0, 5200)
        self.control.setTarget(1, 6800)
        if distance:
            time.sleep(distance / self.distance_scale)
            self.stop()

    def reverse(self, distance=None):
        self.control.setTarget(0, 6800)
        self.control.setTarget(1, 5200)
        if distance:
            time.sleep(distance / self.distance_scale)
            self.stop()

    def right(self, angle=None):
        self.control.setTarget(0, 5700)
        self.control.setTarget(1, 5900)
        if angle:
            time.sleep(angle / self.right_scale)
            self.stop()

    def left(self, angle=None):
        self.control.setTarget(0, 5900)
        self.control.setTarget(1, 6300)
        if angle:
            time.sleep(angle / self.left_scale)
            self.stop()

    def stop(self):
        self.control.setTarget(0, 5900)
        self.control.setTarget(1, 5900)



if __name__=="__main__":
    wheels = Wheels()
    wheels.right(90)
    time.sleep(1)
    wheels.left(90)
    time.sleep(1)
    wheels.stop()

