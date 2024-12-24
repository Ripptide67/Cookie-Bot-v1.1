"""
tracking_test.py
GOAL: Track the red square on the platform using the web camera
MODULES USED:
- numpy as np
- cv2 as cv
FUNCTIONS:
Function:
Purpose:



"""
# Import modules
import numpy as np
import cv2 as cv

# Start the web camera
cap = cv.VideoCapture(1) # Define camera object (0 = Main Camera, 1 = Web Camera)
# If the camera couldn't be opened, exit program and print error message
if not cap.isOpened():
    print("Can't open camera")
    exit()

while True:
    # Capture the video frame by frame
    ret, frame = cap.read()

    # If the frame is read correctly, ret = True
    if not ret:
        print("Frame read incorrectly, exiting program")
        break
    # Convert image from BGR to HSV (easier to detect color ranges)
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    # Define the upper and lower threshold of the filter (H-0-180)
    red_lower = np.array([0,150,50])
    red_upper = np.array([180,255,255])

    # Apply mask with the upper and lower bounds
    mask = cv.inRange(hsv, red_lower, red_upper)

    # Remove noise by eroding and dilating image
    kernel = np.ones((25,25),np.uint8)
    opening = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)

    # Find and draw contours on binary image
    contours, hirarchy = cv.findContours(opening, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # print(contours)
    # cv.drawContours(frame, contours, -1, (0,255,0), 3)
    # If there are contours, draw contours
    if contours != ():
        bounding_rect = cv.minAreaRect(contours[0])
        # print(bounding_rect)
        box = cv.boxPoints(bounding_rect)
        print(box)
        box = np.int0(box) # Convert box into integer values
        # print(box)
        cv.drawContours(frame, [box],0,(0,0,255),2)

        # Take the calibration square and scale-up to printable area
        rsq_l = np.int0(bounding_rect[1]) # Red SQuare length
        l_avg = int((rsq_l[0] + rsq_l[1])/2)
        l_platform = int(8.8 * l_avg)
        w_platform = int(7.3 * l_avg)
        # Draw this on the frame
        bounding_platform = (bounding_rect[0], (w_platform, l_platform), bounding_rect[2])
        box_platform = cv.boxPoints(bounding_platform)
        box_platform = np.int0(box_platform)

        cv.drawContours(frame, [box_platform],0,(0,255,0),2)



    # Display the resulting frame
    cv.imshow('frame', frame)
    # cv.imshow('mask',mask) # Mask display
    # cv.imshow('opening',opening) # Dialation display

    # Quit image capture by pressing 'q'
    if cv.waitKey(1) == ord('q'):
        break

# When everything is done, release capture (VERY IMPORTANT!!)
cap.release()
cv.destroyAllWindows()
