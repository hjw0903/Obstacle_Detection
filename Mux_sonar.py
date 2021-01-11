# This code is based on the pigpio library example code. (http://abyz.me.uk/rpi/pigpio/examples.html#Python%20code)
# Modified by Jung Won Hwang (hjw0903@gmauil.com) for using the Multiplexer with the nine Ultrasonic sensors.

import time

import pigpio

class ranger:
   """
   This class encapsulates a type of acoustic ranger.  In particular
   the type of ranger with separate trigger and echo pins.

   A pulse on the trigger initiates the sonar ping and shortly
   afterwards a sonar pulse is transmitted and the echo pin
   goes high.  The echo pins stays high until a sonar echo is
   received (or the response times-out).  The time between
   the high and low edges indicates the sonar round trip time.
   """

   def __init__(self, pi, trigger, echo, Mux_S0, Mux_S1, Mux_S2, Mux_S3):
      """
      The class is instantiated with the Pi to use and the
      gpios connected to the trigger and echo pins.
      """
      self.pi    = pi
      self._trig = trigger
      self._echo = echo

      self._s0 = Mux_S0
      self._s1 = Mux_S1
      self._s2 = Mux_S2
      self._s3 = Mux_S3

      self._ping = False
      self._high = None
      self._time = None

      self._triggered = False

      self._trig_mode = pi.get_mode(self._trig)
      self._echo_mode = pi.get_mode(self._echo)

      self._muxS0_mode = pi.get_mode(self._s0)
      self._muxS1_mode = pi.get_mode(self._s1)
      self._muxS2_mode = pi.get_mode(self._s2)
      self._muxS3_mode = pi.get_mode(self._s3)

      pi.set_mode(self._trig, pigpio.OUTPUT)
      pi.set_mode(self._echo, pigpio.INPUT)

      pi.set_mode(self._s0, pigpio.OUTPUT)
      pi.set_mode(self._s1, pigpio.OUTPUT)
      pi.set_mode(self._s2, pigpio.OUTPUT)
      pi.set_mode(self._s3, pigpio.OUTPUT)

      self._cb = pi.callback(self._trig, pigpio.EITHER_EDGE, self._cbf)
      self._cb = pi.callback(self._echo, pigpio.EITHER_EDGE, self._cbf)

      self._inited = True

   def _cbf(self, gpio, level, tick):
      if gpio == self._trig:
         if level == 0: # trigger sent
            self._triggered = True
            self._high = None
      else:
         if self._triggered:
            if level == 1:
               self._high = tick
            else:
               if self._high is not None:
                  self._time = tick - self._high
                  self._high = None
                  self._ping = True

   def read(self):
      """
      Triggers a reading.  The returned reading is the number
      of microseconds for the sonar round-trip.

      round trip cms = round trip time / 1000000.0 * 34030
      """
      if self._inited:
         self._ping = False
         self.pi.gpio_trigger(self._trig)
         start = time.time()
         while not self._ping:
            if (time.time()-start) > 5.0:
               return 20000
            time.sleep(0.001)
         return self._time
      else:
         return None

   def cancel(self):
      """
      Cancels the ranger and returns the gpios to their
      original mode.
      """
      if self._inited:
         self._inited = False
         self._cb.cancel()
         self.pi.set_mode(self._trig, self._trig_mode)
         self.pi.set_mode(self._echo, self._echo_mode)

         self.pi.set_mode(self._s0, self._muxS0_mode)
         self.pi.set_mode(self._s1, self._muxS1_mode)
         self.pi.set_mode(self._s2, self._muxS2-mode)
         self.pi.set_mode(self._s3, self._muxS3-mode)

   def mux(self, SENSORS):
      COUNT = 0
      results = [0,0,0,0,0,0,0,0,0]

      for counter in range(0, SENSORS):

         if COUNT == 8:
             self.pi.write(self._s0, 0)
             self.pi.write(self._s1, 0)
             self.pi.write(self._s2, 0)
             self.pi.write(self._s3, 1)

         elif COUNT == 7:
             self.pi.write(self._s0, 1)
             self.pi.write(self._s1, 1)
             self.pi.write(self._s2, 1)
             self.pi.write(self._s3, 0)

         elif COUNT == 6:
             self.pi.write(self._s0, 0)
             self.pi.write(self._s1, 1)
             self.pi.write(self._s2, 1)
             self.pi.write(self._s3, 0)

         elif COUNT == 5:
             self.pi.write(self._s0, 1)
             self.pi.write(self._s1, 0)
             self.pi.write(self._s2, 1)
             self.pi.write(self._s3, 0)

         elif COUNT == 4:
             self.pi.write(self._s0, 0)
             self.pi.write(self._s1, 0)
             self.pi.write(self._s2, 1)
             self.pi.write(self._s3, 0)

         elif COUNT == 3:
             self.pi.write(self._s0, 1)
             self.pi.write(self._s1, 1)
             self.pi.write(self._s2, 0)

         elif COUNT == 2:
             self.pi.write(self._s0, 0)
             self.pi.write(self._s1, 1)
             self.pi.write(self._s2, 0)
             self.pi.write(self._s3, 0)

         elif COUNT == 1:
             self.pi.write(self._s0, 1)
             self.pi.write(self._s1, 0)
             self.pi.write(self._s2, 0)
             self.pi.write(self._s3, 0)

         else:
             self.pi.write(self._s0, 0)
             self.pi.write(self._s1, 0)
             self.pi.write(self._s2, 0)
             self.pi.write(self._s3, 0)

         time.sleep(0.01) # 0.06, 0.03
         trip = self.read()
         result = ((trip/2)/ 1000000.0 *34330) / 100 # change unit cm to m

         results[COUNT] = result
         COUNT += 1
         time.sleep(0.01) # 0.06, 0.03

      return results

if __name__ == "__main__":

   import time

   import pigpio

   import Mux_sonar

   pi = pigpio.pi()

   sonar = Mux_sonar.ranger(pi, 18, 24, 20, 21, 19, 16)

   end = time.time() + 600.0

   SENSORS = 9

   r = 1
   while time.time() < end:

      print (str(r)+'._______________________')
      sonar.mux(SENSORS)
      r += 1
      time.sleep(0.03)

   sonar.cancel()

   pi.stop()

