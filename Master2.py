import threading
import time
from imu import IMU
from lidar import Lidar
from control import Wheels
from Tag import PositionTracker
from gridspace import Gridspace
import numpy as np
import math

class Master:
    def __init__(self):
        self.lidar = Lidar(0x10, [0x5A, 0x05, 0x00, 0x01, 0x60])
        self.imu = IMU()
        self.wheels = Wheels()
        self.tag = PositionTracker()
        self.grid = Gridspace()
        self.stop_event = threading.Event()
        self.obstacle_threshold = 50  # Set threshold distance in cm
        self.is_grid_initialized = False
        self.average_position = {}
        self.previous_position = {}
        self.current_position = {}
        self.current_angle = 0
        self.obstructed = True
        self.logging_lidar = False
        self.logging_imu = False
        self.logging_tag = True

    def run(self):
        threading.Thread(target=self.lidar_monitor).start()
        threading.Thread(target=self.imu_monitor).start()
        threading.Thread(target=self.tag_monitor).start()
        threading.Thread(target=self.navigation_loop).start()

    def lidar_monitor(self):
        if(self.logging_lidar): print("Lidar monitoring started\n")
        while not self.stop_event.is_set():
            try:
                lidar_dict = self.lidar.getLidarData()
                self.object_distance = lidar_dict['distance']
                if self.object_distance and self.object_distance < self.obstacle_threshold:
                    print("Obstacle detected, recalculating path.")
                    self.obstructed = True
                    while self.object_distance and self.object_distance < self.obstacle_threshold and not self.stop_event.is_set():
                        time.sleep(0.1)
                        self.wheels.stop()
                    print("Object clear!")
                else:
                    self.obstructed = False
                if(self.logging_lidar):print(f"Distance: {self.object_distance} cm\n")
            except Exception as e:
                if(self.logging_lidar):print(f"Error reading from LiDAR: {e}")
            time.sleep(0.2)
        if(self.logging_lidar):print("Lidar monitoring stopped\n")

    def imu_monitor(self):
        if(self.logging_imu): print("IMU monitoring started\n")
        while not self.stop_event.is_set():
            try:
                imu_dict = self.imu.read_sensor_data()
                angle_z = imu_dict['angle_z']
                if(self.logging_imu):print(f"Angle Z: {angle_z}\n")
                average_z = self.imu.calc_z_average(10)
                if(self.logging_imu):print("Average Z", average_z)
            except Exception as e:
                if(self.logging_imu):print(f"Error reading from IMU: {e}")
            time.sleep(0.2)
        if(self.logging_imu):print("IMU monitoring stopped\n")

    def tag_monitor(self):
        """
        Continuously monitors and updates the UWB tag positions, managing the grid state accordingly.
        This function runs in a loop until a stop event is set, indicating the monitoring should cease.
        """
        if(self.logging_tag):print("Tag monitor started.\n")
        while not self.stop_event.is_set():
            try:
                # Retrieve the current positions of all UWB anchors.
                anchors = self.tag.getAnchorPositions()
                # Retrieve the averaged position of the tag which can be more stable.
                self.average_position = self.tag.getAveragedPosition()
                if anchors and all(p['x'] >= 0 and p['y'] >= 0 for p in anchors.values()):
                    if not self.is_grid_initialized:
                        # Use specific anchors to define the grid dimensions.
                        x_size = anchors['anchor3']['x']  # Horizontal size based on 'anchor3'
                        y_size = anchors['anchor2']['y']  # Vertical size based on 'anchor2'
                        self.grid.initialize_grid(x_size, y_size)  # Initialize the grid with these dimensions.
                        self.is_grid_initialized = True  # Prevent re-initialization.
                        self.current_position = {'x': 0, 'y': 0}
                    self.grid.update_position(self.grid.label['current'], self.average_position['x'], self.average_position['y'])
                else:
                    print()
                    # Handle cases where position data is invalid or incomplete.
                    if(self.logging_tag): print("Invalid or incomplete anchor position data received. Monitoring continues.")
            except Exception as e:
                # General exception handling for any errors that occur during the monitoring process.
                if(self.logging_tag): print(f"Error encountered while retrieving positions: {str(e)}")
            time.sleep(0.25)
        if(self.logging_tag): print("Tag monitoring stopped.")
        
    def navigation_loop(self):
        while not self.stop_event.is_set():
            if not self.is_grid_initialized:
                time.sleep(0.1)
                break
        while True:
            position = self.grid.get_grid_position()
            path = self.grid.find_path(position, self.grid.label['destination b'])
            print(path)
            if path and not self.obstructed:
                print("movin")
                self.move_along_path(path)
            elif path:
                print("Obstructed! Rerouting...")
                try:
                    match self.current_angle:
                        case 0:
                            self.grid.update_grid(self.grid.label['obstacle'], position[0], position[1] + 1)
                        case 90:
                            self.grid.update_grid(self.grid.label['obstacle'], position[0] + 1, position[1])
                        case 180:
                            self.grid.update_grid(self.grid.label['obstacle'], position[0], position[1] - 1)
                        case 270:
                            self.grid.update_grid(self.grid.label['obstacle'], position[0] - 1, position[1])
                except Exception as e:
                    print(e)

    def move_along_path(self, path):
        for i in range(len(path) - 1):
            current = path[i]
            print(current)
            next = path[i + 1]
            required_angle = self.calculate_turn_angle(current, next)
            self.turn_to(required_angle)            
            self.wheels.forward(50)  # Assume each grid cell is 1 unit of movement

    def follow_path(self, path):
        print("Following Path")
        for i in range(len(path) - 1):
            if self.object_distance and self.object_distance < self.obstacle_threshold:
                print("Obstacle detected, recalculating path.")
                while self.object_distance and self.object_distance < self.obstacle_threshold and not self.stop_event.is_set():
                    time.sleep(0.1)
                print("Object clear!")
            current = path[i]
            print(current)
            next = path[i + 1]
            required_angle = self.calculate_turn_angle(current, next)
            self.turn_to(required_angle)
            time.sleep(1)
            self.wheels.forward(50)  # Assume each grid cell is 1 unit of movement
            print(self.object_distance)
            

    def calculate_turn_angle(self, current, next):
        # Calculate the required turn angle based on current and next coordinates
        direction_vector = (next[0] - current[0], next[1] - current[1])
        return self.vector_to_angle(direction_vector)

    def vector_to_angle(self, vector):
        # Convert direction vector to navigational angle
        x, y = vector
        if x == 1: return 90  # East
        if x == -1: return 270  # West
        if y == 1: return 0  # North
        if y == -1: return 180  # South

    def turn_to(self, angle):
        print(f"Turning to {angle} degrees from current angle {self.current_angle}")
        match angle:
            case 0:  # North
                match self.current_angle:
                    case 0:
                        print("Already facing North, no turn needed.")
                    case 90:
                        self.wheels.left(90)
                        self.current_angle = 0
                        print("Turned left from East to North.")
                    case 180:
                        self.wheels.right(180)
                        self.current_angle = 0
                        print("Turned around from South to North.")
                    case 270:
                        self.wheels.right(90)
                        self.current_angle = 0
                        print("Turned right from West to North.")

            case 90:  # East
                match self.current_angle:
                    case 0:
                        self.wheels.right(90)
                        self.current_angle = 90
                        print("Turned right from North to East.")
                    case 90:
                        print("Already facing East, no turn needed.")
                    case 180:
                        self.wheels.left(90)
                        self.current_angle = 90
                        print("Turned left from South to East.")
                    case 270:
                        self.wheels.right(180)
                        self.current_angle = 90
                        print("Turned around from West to East.")

            case 180:  # South
                match self.current_angle:
                    case 0:
                        self.wheels.right(180)
                        self.current_angle = 180
                        print("Turned around from North to South.")
                    case 90:
                        self.wheels.right(90)
                        self.current_angle = 180
                        print("Turned right from East to South.")
                    case 180:
                        print("Already facing South, no turn needed.")
                    case 270:
                        self.wheels.left(90)
                        self.current_angle = 180
                        print("Turned left from West to South.")

            case 270:  # West
                match self.current_angle:
                    case 0:
                        self.wheels.left(90)
                        self.current_angle = 270
                        print("Turned left from North to West.")
                    case 90:
                        self.wheels.right(180)
                        self.current_angle = 270
                        print("Turned around from East to West.")
                    case 180:
                        self.wheels.right(90)
                        self.current_angle = 270
                        print("Turned right from South to West.")
                    case 270:
                        print("Already facing West, no turn needed.")


            
    
    def stop(self):
        self.stop_event.set()
        self.wheels.stop()
        print("Robot stopped.")

if __name__ == "__main__":
    master = Master()
    try:
        master.run()
        while not master.is_grid_initialized:
            try:
                print("Waiting for intialization...")
                time.sleep(1)
            except KeyboardInterrupt:
                print("Interrupt received, stopping the robot.")
                master.stop()
        time.sleep(1)
        master.grid.update_grid('destination b', 5, 5)
        master.grid.update_grid('obstacle', 3, 0)
        master.grid.update_grid('obstacle', 3, 1)
        master.grid.update_grid('obstacle', 3, 2)
        master.grid.update_grid('obstacle', 3, 3)
        time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupt received, stopping the robot.")
        master.stop()
