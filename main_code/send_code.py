# Created on 12/16/23
"""
Purpose: Test sending code to the robot
"""
# import numpy as np
import time
import cv2 as cv
# import math
import sys
import serial
# Import vision_classes from sub-file
sys.path.insert(0,"..") # Makes the program look into parent directory, Cookie_Bot_ver1.1
import classes.g_code_classes as g
import classes.vision_classes as v
# import vision_classes as vc

# Main code (opening serial port until user is done)
try:
    # Setup the serial port and prepare robot to execute code
    ser = serial.Serial('COM7', 115200, timeout=1)
    Robot = g.GCode_EX(ser)

    # Prepare vision code
    Cookie_V = v.Cookie_Vision()
    # Send the gcode 
    Robot.send_gcode("C:/Users/hsima/Documents/Cookie_Bot_ver1.1/gcode_scripts/generated_code/Trial.txt")
    # Robot.send_gcode("C:/Users/hsima/Documents/Cookie_Bot_ver1.1/gcode_scripts/corners.txt")

    ser.close()
    # capture.release()
    cv.destroyAllWindows()
except Exception as e:
    print(e)
    print("Error occured while trying to run main code")
    ser.close()
    cv.destroyAllWindows()
    # capture.release()
