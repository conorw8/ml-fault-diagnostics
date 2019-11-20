import logging
import sys
import time
import matplotlib.pyplot as plt
import numpy as np
import math
import rospy
from network_faults.msg import IMU
from Adafruit_BNO055 import BNO055

# Create and configure the BNO sensor connection.  Make sure only ONE of the
# below 'bno = ...' lines is uncommented:
# Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
bno = BNO055.BNO055(serial_port='/dev/ttyUSB0', rst=18)
CALIBRATION_FILE = 'data/calibration.json'

# Load calibration from disk.
with open(CALIBRATION_FILE, 'r') as cal_file:
    data = json.load(cal_file)
# Grab the lock on BNO sensor access to serial access to the sensor.
with bno_changed:
    bno.set_calibration(data)

# Enable verbose debug logging if -v is passed as a parameter.
if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
    logging.basicConfig(level=logging.DEBUG)

# Initialize the BNO055 and stop if something went wrong.
if not bno.begin():
    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

# Print system status and self test result.
status, self_test, error = bno.get_system_status()
print('System status: {0}'.format(status))
print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
# Print out an error if system status is in error mode.
if status == 0x01:
    print('System error: {0}'.format(error))
    print('See datasheet section 4.3.59 for the meaning.')

# Print BNO055 software revision and other diagnostic data.
sw, bl, accel, mag, gyro = bno.get_revision()
print('Software version:   {0}'.format(sw))
print('Bootloader version: {0}'.format(bl))
print('Accelerometer ID:   0x{0:02X}'.format(accel))
print('Magnetometer ID:    0x{0:02X}'.format(mag))
print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

print('Reading BNO055 data, press Ctrl-C to quit...')
rospy.init_node('read_imu')
imu_pub = rospy.Publisher('/imu', IMU, queue_size=1, tcp_nodelay=True)
imu_msg = IMU()

rate = rospy.Rate(10.0)
while not rospy.is_shutdown():
    # Read the Euler angles for heading, roll, pitch (all in degrees).
    heading, roll, pitch = bno.read_euler()
    # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
    # sys, gyro, accel, mag = bno.get_calibration_status()
    # Print everything out.
    print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
          heading, roll, pitch, sys, gyro, accel, mag))
    # Other values you can optionally read:
    # Orientation as a quaternion:
    #x,y,z,w = bno.read_quaterion()
    # Sensor temperature in degrees Celsius:
    #temp_c = bno.read_temp()
    # Magnetometer data (in micro-Teslas):
    #x,y,z = bno.read_magnetometer()
    # Gyroscope data (in degrees per second):
    #x,y,z = bno.read_gyroscope()
    # Accelerometer data (in meters per second squared):
    accel_x,accel_y,accel_z = bno.read_accelerometer()
    # Linear acceleration data (i.e. acceleration from movement, not gravity--
    # returned in meters per second squared):
    lin_x,lin_y,lin_z = bno.read_linear_acceleration()
    # Gravity acceleration data (i.e. acceleration just from gravity--returned
    # in meters per second squared):
    #x,y,z = bno.read_gravity()
    # Sleep for a second until the next reading.
    imu_msg.roll = heading
    imu_msg.pitch = roll
    imu_msg.yaw = pitch
    imu_msg.accel_x = accel_x
    imu_msg.accel_y = accel_y
    imu_msg.accel_z = accel_z
    imu_msg.lin_x = lin_x
    imu_msg.lin_y = lin_y
    imu_msg.lin_z = lin_z
    imu_pub.publish(imu_msg)
    rate.sleep()
#
# while True:
#     # Read the Euler angles for heading, roll, pitch (all in degrees).
#     heading, roll, pitch = bno.read_euler()
#     # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
#     sys, gyro, accel, mag = bno.get_calibration_status()
#     # Print everything out.
#     print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
#           heading, roll, pitch, sys, gyro, accel, mag))
#     # Other values you can optionally read:
#     # Orientation as a quaternion:
#     #x,y,z,w = bno.read_quaterion()
#     # Sensor temperature in degrees Celsius:
#     #temp_c = bno.read_temp()
#     # Magnetometer data (in micro-Teslas):
#     #x,y,z = bno.read_magnetometer()
#     # Gyroscope data (in degrees per second):
#     #x,y,z = bno.read_gyroscope()
#     # Accelerometer data (in meters per second squared):
#     #x,y,z = bno.read_accelerometer()
#     # Linear acceleration data (i.e. acceleration from movement, not gravity--
#     # returned in meters per second squared):
#     #x,y,z = bno.read_linear_acceleration()
#     # Gravity acceleration data (i.e. acceleration just from gravity--returned
#     # in meters per second squared):
#     #x,y,z = bno.read_gravity()
#     # Sleep for a second until the next reading.
#     time.sleep(0.1)
