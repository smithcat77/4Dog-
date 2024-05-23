import smbus
import threading
import math
import time

class Lidar:
    def __init__(self, address, command):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.command = command
        
    def getLidarData(self):
        self.bus.write_i2c_block_data(self.address, 0x00, self.command)
        time.sleep(0.01)
        data = self.bus.read_i2c_block_data(self.address, 0x00, 9)
        distance = data[0] | (data[1] << 8)
        strength = data[2] | (data[3] << 8)
        temperature = (data[4] | (data[5] << 8)) / 100
        lidar_data = {
            'distance': distance,
            'strength': strength,
            'temperature': temperature
        }
        #print(f"Lidar Data - Distance: {distance} cm, Strength: {strength}, Temperature: {temperature:.2f} C")
        return lidar_data
    
def main():
    address = 0x10
    command = [0x5A, 0x05, 0x00, 0x01, 0x60]  
    lidar = Lidar(address, command)
    try:
        while True:
            lidar.getLidarData()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Interrupted by user")

if __name__ == "__main__":
    main()

'''
bus = smbus.SMBus(1)
address = 0x10
getLidarDataCmd = [0x5A, 0x05, 0x00, 0x01, 0x60] # Gets the distance value instruction

def getLidarData(addr, cmd):
	bus.write_i2c_block_data(addr, 0x00, cmd)
	time.sleep(0.01)
	data = bus.read_i2c_block_data(addr,0x00, 9)
	distance = data[0] | (data[1] << 8)
	strength = data[2] | (data[3] << 8)
	temperature = (data[4] | (data[5] << 8)) / 100
	print('distance = %5d cm, strength = %5d, temperature = %5d C'%(distance, strength, temperature))		
		
while True:
	getLidarData(address, getLidarDataCmd)
	time.sleep(0.1)
'''
