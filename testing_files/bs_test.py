import cv2 as cv
import numpy as np

# KNN Subtractor (other is MOG2: it was found KNN works best)
backSub = cv.createBackgroundSubtractorKNN()

# Camera capture
capture = cv.VideoCapture(0)
# Check if camera was opened
if not capture.isOpened():
    print("Error opening camera: couldn't be opened")
    exit()

frameNumSinceTest = 1 # Capturing the frame number since the testing began
font = cv.FONT_HERSHEY_SIMPLEX # Font type
wait_for_respose = False
# Main loop
while True:
    key_press = cv.waitKey(1) # Detect any keys that were pressed
    ret, frame = capture.read() # read the camera
    # Check to see if the frame was read correctly
    if frame is None:
        print("Error reading frame: quitting")
        break

    cv.rectangle(frame, (10,2), (225,20), (255,255,255), -1)
    # Use the first 100 frames as masking "learning" data
    print(frameNumSinceTest)
    if frameNumSinceTest < 100:
        fgMask = backSub.apply(frame) # Apply masking to video feed using first frame
        cv.putText(frame,'Learning: Please Wait',(15,15), font, 0.5, (0,0,0))
        frameNumSinceTest += 1
    elif wait_for_respose == False:
        # print("Done Testing")
        cv.putText(frame,'Place Cookie on Platform',(15,15), font, 0.5, (0,0,0))

    # Record after the cookie is placed
    if key_press == ord('s'):
        fgMask = backSub.apply(frame)
        wait_for_respose = True

    # If the user recorded the cookie, display the threshold for user to verify
    # if the cookie shape looks correct
    if wait_for_respose == True:
        cv.imshow('Frame', fgMask)
        cv.rectangle(fgMask, (10,2), (225,20), (255,255,255), -1)
        cv.putText(fgMask,'Correct? (Y/N)',(15,15), font, 0.5, (0,0,0))
        if key_press == ord('y'):
            print("Saving Image")
            break
        elif key_press == ord('n'):
            wait_for_respose = False
            frameNumSinceTest = 1 # Set the number of frames to 1 so model can relearn
    else:
        cv.imshow('Frame', frame)

    if key_press == ord('q'):
        print("'q' was pressed: quitting")
        break

capture.release() # Stop the camera
cv.destroyAllWindows() # Destroy all windows created by OpenCV
