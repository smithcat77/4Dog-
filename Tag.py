import serial
import time

class PositionTracker:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        self.serial_port = serial.Serial(port, baudrate)
        self.tag_positions = [(0, 0)] * 5  # Initialize buffer for 5 positions
        self.average_pointer = 0  # Pointer for the circular buffer        
        
    def getAnchorPositions(self):
        #Returns a dictionary of the most recent line from the serial port.
        line = self.read_line()
        if line:
            positions = list(map(float, line.split(',')))
            return {
                'anchor1': {'x': positions[0], 'y': positions[1]},
                'anchor2': {'x': positions[2], 'y': positions[3]},
                'anchor3': {'x': positions[4], 'y': positions[5]},
                'tag': {'x': positions[6], 'y': positions[7]}
            }
        return {}

    def getAveragedPosition(self):
        """Reads continuously and updates the average position whenever called."""
        line = self.read_line()
        while not line:
            #print("Waiting for data...")
            line = self.read_line()  # Keep trying until a line is read

        try:
            parts = list(map(float, line.split(',')))
            # Update the circular buffer with the new position
            self.tag_positions[self.average_pointer] = (parts[6], parts[7])
            self.average_pointer = (self.average_pointer + 1) % len(self.tag_positions)
            # Calculate the average of the positions in the buffer
            avg_x = sum(pos[0] for pos in self.tag_positions) / len(self.tag_positions)
            avg_y = sum(pos[1] for pos in self.tag_positions) / len(self.tag_positions)
            return {'x': avg_x, 'y': avg_y}
        except (IndexError, ValueError) as e:
            print(f"Error processing line: {line} with error {e}")
            return {}

    def getPosition(self):
        """Returns the most recent tag x and y coordinates."""
        line = self.read_line()
        if line:
            parts = list(map(float, line.split(',')))
            return {'x': parts[6], 'y': parts[7]}
        return {}

    def read_line(self):
        """Helper function to read a line from the serial port."""
        if self.serial_port.in_waiting > 0:
            return self.serial_port.readline().decode('utf-8').rstrip()
        return None

    def close(self):
        """Closes the serial connection."""
        self.serial_port.close()

if __name__ == "__main__":
    tracker = PositionTracker()
    try:
        while True:
            #print("Gridspace Positions:", tracker.getGridspacePositions())
            #print("Averaged Position:", tracker.getAveragedPosition())
            #print("Position:", tracker.getPosition())
            time.sleep(0.5) # Sleep for a short period to prevent excessive processing
    except KeyboardInterrupt:
        print("Program terminated!")
        tracker.close()

