# This code is made by using the on-line library for Ultrasonic sensor and servo motor.
# For the Ultrasonic senor, it is modified by using the pigpio library. 

import time
import pigpio
import subprocess

import math
import numpy as np

class Ultraservo:

      """
      This class encapsulates a type of acoustic ranger.  In particular
      the type of ranger with separate trigger and echo pins.

      A pulse on the trigger initiates the sonar ping and shortly
      afterwards a sonar pulse is transmitted and the echo pin
      goes high.  The echo pins stays high until a sonar echo is
      received (or the response times-out).  The time between
      the high and low edges indicates the sonar round trip time.
      """

      def __init__(self, pi, servo, trigger, echo, OFFSET=0, MIN_ANGLE = 10, MAX_ANGLE = 160, STEP = 10, TooLong=23509):

            """
            The class is instantiated with the Pi to use and the
            gpios connected to the trigger and echo pins.  If the
            echo is longer than toolong it is assumed to be an
            outlier and is ignored.
            """

            self.pi = pi
            self.trigger = trigger
            self.echo = echo
            self.TooLong = TooLong
            self.OFFSET = OFFSET
            self.STEP = STEP
            self.MIN_ANGLE = MIN_ANGLE
            self.MAX_ANGLE = MAX_ANGLE
            self.servoPin = servo

            self.high_tick = None

            self.echo_time = TooLong
            self.echo_tick = pi.get_current_tick()

            self.trigger_mode = pi.get_mode(trigger)
            self.echo_mode = pi.get_mode(echo)

            pi.set_PWM_frequency(self.servoPin, 50)
            pi.set_PWM_range(self.servoPin, 40000)

            self.initPosition(1500)

            pi.set_mode(trigger, pigpio.OUTPUT)
            pi.set_mode(echo, pigpio.INPUT)

            self.cb = pi.callback(echo, pigpio.EITHER_EDGE, self._cbf)

            self.inited = True

      def _cbf(self, gpio, level, tick):
            if level == 1:
                  self.high_tick = tick
            elif level == 0:
                  if self.high_tick is not None:
                        echo_time = tick - self.high_tick
                        if echo_time < self.TooLong:
                              self.echo_time = echo_time
                              self.echo_tick = tick
                        else:
                              self.echo_time = self.TooLong
                              self.high_tick = None

      def initPosition(self, init_duty=1500):
            self.pi.set_PWM_dutycycle(self.servoPin,init_duty)

      def read(self):
            """
            The returned reading is the number
            of microseconds for the sonar round-trip.

            round trip cms = round trip time / 1000000.0 * 34030
            """
            if self.inited:
                  return self.echo_time
            else:
                  return None

      def readAngleRange(self, startAngle, endAngle, STEP = 0):
            startAngle = int(startAngle)
            endAngle = int(endAngle)
            if STEP == 0:
                  step = self.STEP
            else:
                  step = STEP
            if(startAngle > endAngle):
                  step = self.STEP * -1
                  startAngle = max(startAngle, self.MAX_ANGLE)
                  endAngle = min(endAngle, self.MIN_ANGLE)
            else:
                  startAngle = min(startAngle, self.MIN_ANGLE)
                  endAngle = max(endAngle, self.MAX_ANGLE)

      def trig(self):
            """
            Triggers a reading.
            """
            if self.inited:
                  self.pi.gpio_trigger(self.trigger)

      def readAngle(self, angle, sample = 1):
            self.moveServo(angle)
            distance = []
            for i in range(0, sample, 1):
                  self.trig()
                  distance.append(self.read())
                  time.sleep(0.03) # for sound travel 0.03 seconds, to detect obstacles 5 meters away

            report_angle = self.OFFSET - angle

            if(report_angle>360):
                  report_angle -= 360
            if(report_angle<=0):
                  report_angle += 360

            return ( report_angle, np.mean(distance) / pow(10,6) * 34330 / 2 / 100)

      def moveServo(self, angle):
            if angle < self.MIN_ANGLE:
                  angle = self.MIN_ANGLE
            if angle > self.MAX_ANGLE:
                  angle = self.MAX_ANGLE

            duty = 1500 + (angle * 22.2)
            self.pi.set_PWM_dutycycle(self.servoPin,duty)


      def cancel(self):
            if self.inited:
                  self.inited = False
            self.cb.cancel()
            self.pi.set_mode(self.trigger, self.trigger_mode)
            self.pi.set_mode(self.echo, self.echo_mode)

if __name__ == "__main__":

      pi = pigpio.pi()
      while pi.connected == False:
            subprocess.run("sudo pigpiod", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pi = pigpio.pi()


      us_front_left = Ultraservo(pi, 12, 24, 25,360)
      us_front_right = Ultraservo(pi, 13, 5, 4, 120)  #180
      us_back = Ultraservo(pi, 20, 6, 18, 240)   #270

      us_back.moveServo(90)
      us_front_left.moveServo(90)
      us_front_right.moveServo(90)

'''
      text = None
      while text != '':
            text = input("Please confirm that all servo are set to 90 degree \nthen Press enter key:")

      while True:
            for angle in range(0,160, 10):
                  print('front_left : ', angle, us_front_left.readAngle(angle))
                  print('front_right: ', angle, us_front_right.readAngle(angle))
                  print('       back: ', angle, us_back.readAngle(angle))

            for angle in range(160,0, -10):
                  print('front_left : ',us_front_left.readAngle(angle))
                  print('front_right: ',us_front_right.readAngle(angle))
                  print('       back: ',us_back.readAngle(angle))
'''
