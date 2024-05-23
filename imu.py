import smbus
import time
import math
import numpy as np

class IMU:

    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.accel_xout_h = 0x3B
        self.pwr_mgmt_1 = 0x6B
        self.address = 0x68
        self.angle_z_samples = [0] * 5
        self.average_pointer = 0
        self.setup()

    def setup(self):
        """Initialize the MPU-6050 sensor."""
        self.bus.write_byte_data(self.address, self.pwr_mgmt_1, 0)  # Wake up the MPU-6050

    def read_sensor_data(self):
        """Read and update acceleration data, then calculate angles."""
        raw_data = self.bus.read_i2c_block_data(self.address, self.accel_xout_h, 6)
        # Convert from 16-bit unsigned to signed if high bit is set (negative values)
        acc_x = self.convert_to_signed(raw_data[0], raw_data[1])
        acc_y = self.convert_to_signed(raw_data[2], raw_data[3])
        acc_z = self.convert_to_signed(raw_data[4], raw_data[5])

        angle_x = math.atan2(acc_y, acc_z + acc_z**0.5) * 180 / math.pi
        angle_y = math.atan2(-acc_x, math.sqrt(acc_y**2 + acc_z**2)) * 180 / math.pi
        angle_z = math.atan2(acc_x, acc_y) * 180 / math.pi
        #print(f"Sensor Data - AccX: {acc_x:.2f} g, AccY: {acc_y:.2f} g, AccZ: {acc_z:.2f} g, "
        #      f"AngX: {angle_x:.2f}°, AngY: {angle_y:.2f}°, AngZ: {angle_z:.2f}°")  
        
        self.angle_z_samples[self.average_pointer] = angle_z
        self.average_pointer = (self.average_pointer + 1) % len(self.angle_z_samples)
        
        return {
            'acc_x': acc_x, 'acc_y': acc_y, 'acc_z': acc_z,
            'angle_x': angle_x, 'angle_y': angle_y, 'angle_z': angle_z
        }
    
    def calc_z_average(self, count):
        """Calculate and return the average of angle_z after collecting the specified number of samples."""
        average_z = np.mean(self.angle_z_samples)
        return average_z

    def convert_to_signed(self, high, low):
        """Convert raw 16-bit unsigned data to signed."""
        value = (high << 8) | low
        if value >= 0x8000:  # If the high bit is set, the number is negative
            value = -(0x10000 - value)
        return value / 16384.0  # Convert to g-units (assuming ±2g scale for 16384 LSB/g)
'''
def main():
    imu = IMU()
    try:
        while True:
            imu.read_sensor_data()
            time.sleep(0.1)  
    except KeyboardInterrupt:
        print("Interrupted by user")

if __name__ == "__main__":
    main()
'''

'''
# Constants for MPU6050 registers
ACCEL_XOUT_H = 0x3B
PWR_MGMT_1 = 0x6B
ADDRESS = 0x68  # I2C address for MPU6050

bus = smbus.SMBus(1)

# Shared dictionary to store the IMU data
imu_data = {}

def setup_mpu():
    """Initialize the MPU-6050 sensor."""
    bus.write_byte_data(ADDRESS, PWR_MGMT_1, 0)  # Wake up the MPU-6050

def read_sensor_data():
    """Read sensor data and return acceleration values in g and calculated angles."""
    raw_data = bus.read_i2c_block_data(ADDRESS, ACCEL_XOUT_H, 6)
    acc_x = convert_to_signed(raw_data[0], raw_data[1])
    acc_y = convert_to_signed(raw_data[2], raw_data[3])
    acc_z = convert_to_signed(raw_data[4], raw_data[5])

    angle_x = math.atan2(acc_y, acc_z + acc_z**0.5) * 180 / math.pi
    angle_y = math.atan2(-acc_x, math.sqrt(acc_y**2 + acc_z**2)) * 180 / math.pi
    angle_z = math.atan2(acc_x, acc_y) * 180 / math.pi

    imu_data['acc_x'] = acc_x
    imu_data['acc_y'] = acc_y
    imu_data['acc_z'] = acc_z
    imu_data['angle_x'] = angle_x
    imu_data['angle_y'] = angle_y
    imu_data['angle_z'] = angle_z

    return imu_data

def convert_to_signed(high, low):
    """Convert raw 16-bit unsigned data to signed."""
    value = (high << 8) | low
    if value >= 0x8000:
        return -(0x10000 - value) / 16384.0
    return value / 16384.0

def main():
    setup_mpu()  # Set up the MPU-6050 sensor
    while True:
        data = read_sensor_data()
        time.sleep(0.1)

if __name__ == "__main__":
    main()

'''

