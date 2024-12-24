# Created on 12/16/23
"""
Purpose: Main code to the cookie robot.
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
    ser = serial.Serial('COM4', 115200, timeout=1)
    Robot = g.GCode_EX(ser)

    # Prepare vision code
    Cookie_V = v.Cookie_Vision()

    # GUI setup
    main_display = 'Cookie Robot v1.1'
    cv.namedWindow(main_display)

    # Video caputure
    capture = cv.VideoCapture(0)
    if not capture.isOpened():
        print("Cannot open camera")
        ser.close()
        exit()

    """
    Machine mode
    0 = HOME - Waiting to scan platform or calibrate platform/camera
    1 = CALIBRATION MODE - Moves the robot into position to scan, asks user to
    scan the platform w/red square, and records where red square/platform is.
    Converts to cookie scan mode once finished
    2 = COOKIE SCAN MODE - Move the robot into position to scan, scans cookie,
    and verifies with user if scan looks correct. Moves to mode 3 of choosing design
    3 = DESIGN SELECTION MODE - User chooses design by scrolling through images
    of potential designs they'd like on their cookie. Once design is selected,
    writes g-code to frost the cookie
    4 = EXECUTION OF G-CODE - G-code that is created in the previous mode is
    executed in this mode, and cookie returns to scan position for user to
    enjoy.
    5 = REPEAT PATTERN - Can be used once execution of code is done. Allows
    user to place new cookie on the platform and automatically apply the same
    pattern as used before

    """
    machine_mode = 0
    while True:
        # Capture frame by frame of camera feed
        ret, frame = capture.read()

        # See if frame is read correctly
        if not ret:
            print("Can't recieve frame, exiting...")
            break

        # Keyboard inputs
        key = cv.waitKey(1)
        # Program will quit whenever q is pressed
        if key == ord('q'):
            print("q was pressed: destroying window and homing")
            Robot.send_gcode("..\gcode_scripts\home.txt")
            break

        # Machine Logic
        # MODE 0 - HOME
        if machine_mode == 0:
            # Display settings in this machine mode
            cv.putText(frame, 'c=Calibrate s=Scan Cookie q=Quit', (10,450), cv.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv.LINE_AA)
            if key == ord('h'):
                Robot.send_gcode("..\gcode_scripts\home.txt") # Puts robot into its normal position
            elif key == ord('c'):
                print("Sucess")
                calibrated = False # Use this variable to help with machine logic
                Robot.send_gcode("..\gcode_scripts\scan_pos.txt") # Puts robot into position to scan cookie
                machine_mode = 1 # Puts the robot into calibration mode
            elif key == ord('s'):
                Robot.send_gcode("..\gcode_scripts\scan_pos.txt")
                machine_mode = 2 # Puts robot into scanning mdoe
        # MODE 1 - CALIBRATION MODE
        elif machine_mode == 1:
            if key == ord('c'):
                Cookie_V.calibrate(frame)
                print("Use This One")
                print(Cookie_V.box_platform)
                calibrated = True
            elif key == ord('h'):
                Robot.send_gcode("..\gcode_scripts\home.txt")
                machine_mode = 0
            elif key == ord('y') and calibrated == True:
                cv.destroyWindow('Calibration')
            elif key == ord('n') and calibrated == True:
                cv.destroyWindow('Calibration')
                Cookie_V.calibrate(frame)
            elif key == ord('s'):
                machine_mode = 2
            # Display settings in calibration mode
            cv.putText(frame, 'c=Calibrate h=Home q=Quit s=Scan Cookie', (10,450), cv.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv.LINE_AA)
        # MODE 2 - COOKIE SCAN MODE
        elif machine_mode == 2:
            Cookie_V.find_cookie(capture, main_display) #Find the cookie, then set machine mode to home
            Cookie_V.gen_g_code_outline()
            cookie_coordinates = Cookie_V.Xt_mm
            Robot.generate_gcode(cookie_coordinates)
            Robot.send_gcode("..\gcode_scripts\generated_code\Trial.txt")
            """
            print("self.box_platform")
            print(Cookie_V.box_platform)
            print("self.contours")
            print(Cookie_V.contours)
            print("self.Xt_mm")
            print(Cookie_V.Xt_mm)
            """
            # Robot.send_gcode("..\gcode_scripts\home.txt") #Set robot to home
            machine_mode = 0 # Set the machine mode to home




        # Display the camera feed w/keyboard shortcuts
        cv.imshow(main_display, frame)

    # Robot.send_gcode("..\gcode_scripts\scan_pos.txt") # Puts robot into position to scan cookie
    # Robot.send_gcode("..\gcode_scripts\home.txt") # Puts robot into its normal position
    ser.close()
    capture.release()
    cv.destroyAllWindows()
except Exception as e:
    print(e)
    print("Error occured while trying to run main code")
    ser.close()
    cv.destroyAllWindows()
    capture.release()
