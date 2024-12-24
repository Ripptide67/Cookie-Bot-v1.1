import cv2
import serial
import time
import numpy as np
import os

class GCode:
    """
    Purpose: To generate and excecute g-code to the cookie robot
    Instance Variables:
        self.coordinates (lst): list of [x,y] coordinates outputed from vision_classes.
        self.x_length (int): The width (x) size of the platform the cookie is
            being printed on
        self.y_length (int): The length (y) size of the platform the cookie is
            being printed on
        self.imgx_length (int): How many pixels are in the x-direction in the image
        self.imgy_length (int): How many pixels are in the y-direction in the image
    Methods:
        self.generate_gcode(self, file_name): Generates g_code for the input image
            - file_name corresponds to the file that will be created that will
            hold the g-code in
        self.send_gcode(self, file_name): Sends the gcode to the correct COM port
            - file_name corresponds to the file that holds the g-code to be sent

    """

    def __init__(self, file, coordinates, x_length, y_length):
        self.coordinates = coordinates
        self.x_length = x_length
        self.y_length = y_length
        image = cv2.imread(file)
        self.imgx_length = image.shape[1]
        self.imgy_length = image.shape[0]

    def generate_gcode(self, file_name):
        # 1st, convert coordinates in image to mm
        coordinates_in_mm = []
        for i in range(0, len(self.coordinates)):
            x_coord_pix = self.coordinates[i][0]
            y_coord_pix = self.coordinates[i][1]
            img_x = self.imgx_length
            img_y = self.imgy_length
            x_coord_mm = round(x_coord_pix * (self.x_length / img_x), 2)
            y_coord_mm = round(y_coord_pix * (self.y_length / img_y), 2)
            coordinates_in_mm.append([x_coord_mm, y_coord_mm])
        # 2nd, need to figure out how much frosting to extrude and write the
        # code to the file (file_name)
        try:
            f = open(file_name, 'w')
            zi = 0
            c = 0.1
            for i in range(0, len(coordinates_in_mm)):
                x = coordinates_in_mm[i][0]
                y = coordinates_in_mm[i][1]
                xi = coordinates_in_mm[i-1][0]
                yi = coordinates_in_mm[i-1][1]
                if i == 0:
                    f.write("G00 X" + str(x) + " Y" + str(y) + " Z" + str(zi) + " F500 \r\n")
                elif i > 0:
                    delta_z = ((x-xi)**2 + (y-yi)**2) ** 0.5 #Figures out how long the line is
                    # This function takes the distance (delta_z) and multiplies it
                    # by a constant, c, and adds it to the initial z-coordinate, zi
                    z = round(zi + (c * delta_z), 2)
                    # g-code to move the probe to a point [x,y] and extrudes 'z' amount
                    # of frosting
                    f.write("G01 X" + str(x) + " Y" + str(y) + " Z" + str(z) + " \r\n")
                    zi = z
            f.write("G00 X0 Y0") #Return to the origin once cookie is printed
            f.close()
            print("G-Code generated!")
        except:
            print("Error occured while generating gcode")
            f.close()



    def send_gcode(self, file_name):
        try:
            print("Opening file and port...")
            f = open(file_name, 'r')
            ser = serial.Serial('COM7', 115200, timeout=1)
            time.sleep(2)
            print("Opened " + str(ser.name) + " and " + file_name)
            # Deliver gcode to the 3D printer
            for line in f.readlines():
                ser.write(str.encode(line))
                time.sleep(1)

            """
            ser = serial.Serial('COM7', 115200, timeout=1)
            time.sleep(2)
            print(ser.name)
            ser.write(str.encode('G00 X100 Y100\r\n'))
            time.sleep(1)
            ser.write(str.encode('G00 X0 Y0\r\n'))
            time.sleep(1)
            ser.close()
            """
            f.close()
            ser.close()
        except Exception as e:
            print(e)
            print("Error occured while trying to open COM7")
            f.close()
            ser.close()

class GCode_EX:
    """
    Purpose: To execute g_code to the robot given a text file
    Instance Variables:
        self.file (str): file where g_code is stored

    Methods:
        self.generate_gcode(self, coordinates file_name): Generates g-code given
            coordinates.
            - coordinates (dbl lst of flt [x y]): List of coordinates to generate
            g-code (in mm)
            - file_name (str): File name to save the g-code in.
            - extrude_rate (float): Rate to extrude icing
            - z-start (float): Where to start z-axis (used in cases where frosting
            multiple cookies in the same run)
        self.send_gcode(self, file_name): Sends the gcode to the correct COM port
            - file_name corresponds to the file that holds the g-code to be sent
    """

    def __init__(self, ser):
        self.ser = ser

    def generate_gcode(self, coordinates, file_name = 'Trial.txt', extrude_rate = 0.1, z_start = 0):
        print("Hello World")
        coordinates_z = np.ones((len(coordinates), 1)) # Initialize array to store z-coordinates
        zi = z_start
        coordinates_z[0] = zi # Start coordinate for z-axis
        for i in range(1, len(coordinates)):
            x = coordinates[i][0]
            y = coordinates[i][1]
            xi = coordinates[i-1][0]
            yi = coordinates[i-1][1]
            # Find the del_z that the extruder needs to move
            delta_z = ((x-xi)**2 + (y-yi)**2) ** 0.5 #Figures out how long the line is
            # This function takes the distance (delta_z) and multiplies it
            # by a constant, extrude_rate, and adds it to the initial z-coordinate, zi
            z = round(zi + (extrude_rate * delta_z), 2)
            coordinates_z[i] = z
            # Update zi so the next z-coordinate is stationed
            zi = z
        # Once all of the z-axis coordinates are generated, put two matrices together
        coordinates_w_z = np.column_stack((coordinates, coordinates_z))
        # Print out success
        print("G-Code generated!")
        print(coordinates_w_z)

        print("Writing to file")
        path = 'C:/Users/hsima/Documents/Cookie_Bot_ver1.1/gcode_scripts/generated_code/'
        file_path = path + file_name
        try:
            first_line = True
            # Erase original file if the original file is held here with name
            if os.path.isfile(file_path):
                f = open(file_path, 'w').close()

            f = open(file_path, 'w') # Open file
            f.write('(File Creation: ' + str(time.ctime()) + ') \n')
            # Write the g-code to the file
            f.write('% \n')
            f.write('G90 \n')
            for i in coordinates_w_z:
                if first_line == True:
                    f.write('G00 X' + str(i[0]) + ' Y' + str(i[1]) + ' Z' + str(i[2]) + '\n')
                    f.write('G01 F500' + '\n') # Feed rate is arbitrary: using Z as feed rate
                    first_line = False
                else:
                    f.write('G01 X' + str(i[0]) + ' Y' + str(i[1]) + ' Z' + str(i[2]) + '\n')
            # Put robot into the scan position and end the program
            f.write('G00 X00 Y-42 \n')
            f.write('M30 \n')
            f.write('% \n')
            f.close()
        except:
            print("Error occured while generating gcode")
            f.close()



    def send_gcode(self, file_name):
        try:
            print("Opening file and port...")
            f = open(file_name, 'r')
            # ser = serial.Serial(self.COM, 115200, timeout=1)
            # Wake up Arduino & flush the input of the serial stream
            self.ser.write(str.encode("\r\n\r\n"))
            time.sleep(4)
            self.ser.flushInput()
            
            print("Opened " + str(self.ser.name) + " and " + file_name)
            # Deliver gcode to the 3D printer
            """
            for line in f.readlines():
                self.ser.write(str.encode(line))
                print(">> Sent command: " + str(line))
                output = self.ser.readline() # Wait for grbl to respond
                print(">> " + str(output))
                # time.sleep(0.1)
            f.close()
            """
            # Keep track of the lines sent to the arduino
            num_char_sent = [] # Number of characters sent from each line
            for line in f.readlines():
                line_send = line.strip() # Get rid of EOL characters
                num_char_sent.append(len(line_send)+1) # Append the number of characters sent to the arduino
                print("Sum of number of characters to send:", sum(num_char_sent))
                while sum(num_char_sent) >= 126: # Can send up to 127 characters before buffer is full
                    output = self.ser.readline().strip() # Read line & strip any unneccessary characters
                    if output.find(b'ok') >= 0:
                        print("Output found: deleting first entry")
                        del num_char_sent[0] # Delete the number of characters sent already
                        break # Break out of while loop
            
                self.ser.write((line_send + '\n').encode('utf-8')) # Send line to arduino once buffer is clear
                print(">> Sent line:", line_send)

            f.close()

             
            # ser.close()
        except Exception as e:
            print(e)
            print("Error occured while trying to open port")
            f.close()
