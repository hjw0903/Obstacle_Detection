# This code is made by using the VL53L0X refference example code.
# Modified by Jung Won Hwang (hjw0903@gmail.com) for using the pigpio libraty.

import pigpio
import time
import VL53L0X

# GPIO for Sensor 1 shutdown pin
sensor1_shutdown = 6
# GPIO for Sensor 2 shutdown pin
sensor2_shutdown = 5

pi = pigpio.pi()

shutdown1_mode = pi.get_mode(sensor1_shutdown)
shutdown2_mode = pi.get_mode(sensor2_shutdown)

# Setup GPIO for shutdown pins on each VL53L0X
pi.set_mode(sensor1_shutdown, pigpio.OUTPUT)
pi.set_mode(sensor2_shutdown, pigpio.OUTPUT)

# Set all shutdown pins low to turn off each VL53L0X
pi.set_mode(sensor1_shutdown, shutdown1_mode)
pi.set_mode(sensor2_shutdown, shutdown2_mode)

pi.write(sensor1_shutdown, 0)
pi.write(sensor2_shutdown, 0)

# Keep all low for 500 ms or so to make sure they reset
time.sleep(0.50)

# Create one object per VL53L0X passing the address to give to each.
tof = VL53L0X.VL53L0X(address=0x2B)
tof1 = VL53L0X.VL53L0X(address=0x2D)

# Set shutdown pin high for the first VL53L0X then
# call to start ranging
pi.write(sensor1_shutdown, 1)
time.sleep(0.50)
tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

# Set shutdown pin high for the second VL53L0X then
# call to start ranging
pi.write(sensor2_shutdown, 1)
time.sleep(0.50)
tof1.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

'''
timing = tof.get_timing()
if (timing < 20000):
    timing = 20000

# To get a distance data, you can call "tof.get_distance()" function.
distance = tof.get_distance()
distance1 = tof1.get_distance()

time.sleep(timing/1000000.00)

tof1.stop_ranging()
pi.write(sensor2_shutdown, 0)
tof.stop_ranging()
pi.write(sensor1_shutdown, 0)

pi.stop()
'''
