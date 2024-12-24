import sys
import serial
sys.path.insert(0,"..") # Makes the program look into parent directory, Cookie_Bot_ver1.1
import cv2 as cv
import classes.g_code_classes as g
import classes.vision_classes as v

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
            print("q was pressed: destroying window")
            break


        Cookie_V.find_cookie(capture, main_display) #Find the cookie, then set machine mode to home

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
