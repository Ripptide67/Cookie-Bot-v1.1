import numpy as np
import cv2 as cv
import math

class Cookie_Vision:
    """
        Purpose: Calibrate, detect, and draw contours on cookie
        Instance Variables:
            self.file_name (str): The name of the file being used
            self.threshold_value (int): The threshold minimum for vision
            self.threshold_type (int): The type of thresholding taking place
                0: Binary
                1: Binary Inverted
                2: Threshold Truncated
                3: Threshold to Zero
                4: Threshold to Zero Inverted
                (see OpenCV documentation for more info)
            self.max_binary_value (int): The max threshold for vision (set to 255)
            self.image (img): Converts image file to something CV2 can operate on
            self.image_copy (img): Copy of self.image
            self.l_avg (int): Average length of red square (should be theoretically
                equivalent on each side). Used in other methods.
            self.box_platform (list of int): Locations of platform verticies
            self.contours (db list of x,y coord.): Coordinates of contours of cookie
        Methods:
            calibrate(self, frame_test, key, im_show = True)
                Takes webcam feed, records where the printable area verticies lay.
                Verticies are stored in self.box_platform
                - frame_test (img): Image to be calibrated
                - im_show (bool): Shows image in seperate window to verify the
                    calibration worked
            find_cookie(self, camera_feed, display_name)
                Find cookie on platform by using background subtraction. Please
                note that this method only works by making sure lighting and
                platform stays still when placing the cookie on the platform.
                Will operate by itself and operate within this function until
                prompted to exit.
                - camera_feed (obj): Uses current camera feed to use for learning
                - display_name (str): Name of the window the software will display
                to
            set_threshold(self, threshold_value, max_binary_value, threshold_type)
                Sets the threshold variables for use in the class. Displays a
                GUI to configure the webcam specs. If 's' is pressed, then the
                unthresholded image on the current screen is saved and is set to
                self.image. The threshold values are also saved. If 'q' is
                pressed, nothing is saved and nothing will change in the object.
            find_contours(self, print_contours)
                Finds the contour(s) and if print_contours is set to True, then
                the image will be displayed in a window along with the contours
                drawn out. Returns the list of contours found
            -------------------------------WIP----------------------------------
            gen_g_code_outline(self)
                Takes known contours and generates g_code to frost the outside
                of the cookie. Robot needs to be calibrated and cookie needs to
                be scanned before running this method. Will print "Error: Robot
                needs to be calibrated and cookie needs to be scanned" and return
                0 if self.box_platform or self.contours is empty


            check_bounds(self)
                Finds if cookie contours is within bounds of printable area.
                Looks at self.box_platform and self.contours to determine wether
                the cookie is within the printable area when the platform calibrated.
                Returns True if the cookie is within bounds and False if cookie is
                outside of the bounds. WIP as its not necessary for functionality,
                but it would be nice as a double check

    """
    def __init__(self, file_name = ""):
        # self.file_name = file_name
        # self.threshold_value = 230
        # self.threshold_type = 1
        # self.max_binary_value = 255
        # self.image = cv2.imread(self.file_name)
        # self.image_copy = self.image.copy()
        self.l_avg = 0
        self.box_platform = []
        self.contours = []
        self.Xt_mm = []

    def calibrate(self, frame_test, im_show = True):
        # Convert image from BGR to HSV (easier to detect color ranges)
        hsv = cv.cvtColor(frame_test, cv.COLOR_BGR2HSV)

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
        # cv.drawContours(frame_test, contours, -1, (0,255,0), 3)
        # If there are contours, draw contours
        if contours != ():
            bounding_rect = cv.minAreaRect(contours[0])
            # print(bounding_rect)
            box = cv.boxPoints(bounding_rect)
            print(box)
            box = np.int0(box) # Convert box into integer values
            # print(box)
            cv.drawContours(frame_test, [box],0,(0,0,255),2)

            # Take the calibration square and scale-up to printable area
            rsq_l = np.int0(bounding_rect[1]) # Red Square length
            self.l_avg = int((rsq_l[0] + rsq_l[1])/2) # Average length of square
            l_platform = int(8.8 * self.l_avg)
            w_platform = int(7.3 * self.l_avg)
            # Draw this on the frame_test
            bounding_platform = (bounding_rect[0], (w_platform, l_platform), bounding_rect[2])
            box_platform = cv.boxPoints(bounding_platform)
            self.box_platform = np.int0(box_platform)

            cv.drawContours(frame_test, [self.box_platform],0,(0,255,0),2)



        # Display the resulting frame
        if im_show == True:
            cv.putText(frame_test, 'Correct? (y/n)', (10,450), cv.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv.LINE_AA)
            cv.imshow('Calibration', frame_test)


            # cv.imshow('mask',mask) # Mask display
            # cv.imshow('opening',opening) # Dialation display

    def find_cookie(self, camera_feed, display_name = "test"):
        # KNN Subtractor (other is MOG2: it was found KNN works best)
        backSub = cv.createBackgroundSubtractorKNN()

        capture = camera_feed
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
            # print(frameNumSinceTest)
            if frameNumSinceTest < 100:
                fgMask = backSub.apply(frame) # Apply masking to video feed using first frame
                cv.putText(frame,'Learning: Please Wait',(15,15), font, 0.5, (0,0,0))
                cv.rectangle(frame, (575,2), (625, 20), (255,255,255), -1)
                cv.putText(frame, str(frameNumSinceTest), (595,15), font, 0.5, (0,0,0))
                frameNumSinceTest += 1
            elif wait_for_respose == False:
                # print("Done Testing")
                cv.putText(frame,'Place Cookie on Platform',(15,15), font, 0.5, (0,0,0))
                # Instruction on bottom left hand corner
                cv.rectangle(frame, (10,435), (225,455), (255,255,255), -1)
                cv.putText(frame, 's=Scan, q=Quit', (15,450), font, 0.5, (0,0,0))

            # Record after the cookie is placed
            if key_press == ord('s'):
                # Back substitution
                fgMask = backSub.apply(frame)
                # Remove noise by eroding and dilating image
                kernel = np.ones((25,25),np.uint8)
                opening = cv.morphologyEx(fgMask, cv.MORPH_OPEN, kernel)
                # cv.imshow("test", opening)
                # Find and draw contours on binary image
                contours, hirarchy = cv.findContours(opening, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
                if contours != ():
                    cnt = contours[0]
                    print(cnt)
                else:
                    print("No Contours Found")
                wait_for_respose = True

            # If the user recorded the cookie, display the threshold for user to verify
            # if the cookie shape looks correct
            if wait_for_respose == True:
                if contours != ():
                    cv.drawContours(frame, [cnt], 0, (0,255,0), 3)

                cv.putText(frame,'Correct? (Y/N)',(15,15), font, 0.5, (0,0,0))
                # cv.rectangle(frame, (10,2), (225,20), (255,255,255), -1)
                cv.imshow(display_name, frame)

                if key_press == ord('y'):
                    print("Saving Contours")
                    if contours != ():
                        self.contours = cnt
                    else:
                        print("No Contours Found: Exiting Cookie Scanner & Homing")
                    """
                    INSERT NEW CODE HERE TO SAVE CONTOURS
                    """

                    break
                elif key_press == ord('n'):
                    wait_for_respose = False
                    frameNumSinceTest = 1 # Set the number of frames to 1 so model can relearn
            else:
                cv.imshow(display_name, frame)

            if key_press == ord('q'):
                print("'q' was pressed: quitting")
                break

    def gen_g_code_outline(self):
        if self.box_platform != () and self.contours != ():
            # Given self attributes, convert everything into mm and transform contours into g-code
            # Find top left corner of printable platform
            origin_translation = [self.box_platform[0]]
            # Reshape contours list from 3D to 2D
            contours_reshaped = np.reshape(self.contours, (len(self.contours), 2))
            # Make matrix of linear transformation & use to set origin (subtract transformation)
            lin_trans_matrix = np.tile(origin_translation, (len(contours_reshaped), 1)) # Makes matrix same dimensions as contours
            # Subtract the translation
            Xt = np.subtract(contours_reshaped, lin_trans_matrix)
            # Find scalar to convert from pixels to mm
            scalar = 15/self.l_avg # 15 mm / l_avg [=] mm/pixel
            # Apply scalar to matrix to convert to mm & store in self.Xt_mm
            self.Xt_mm = scalar * Xt
        elif self.box_platform == () and self.contours == ():
            print("Platform needs calibration and cookie needs to be scanned")
        elif self.contours == ():
            print("Cookie needs to be scanned before generating g-code")
        else:
            print("Platform needs to be calibrated before generating g-code")

"""
    def check_bounds(self):
        cnt = self.contours
        ret = False

        # Find the extreme points on the cookie shape
        # Code adapted from https://docs.opencv.org/4.x/d1/d32/tutorial_py_contour_properties.html
        extreme_points[0] = tuple(cnt[cnt[:,:,0].argmin()][0]) # Leftmost
        extreme_points[1] = tuple(cnt[cnt[:,:,0].argmax()][0]) # Rightmost
        extreme_points[2] = tuple(cnt[cnt[:,:,1].argmin()][0]) # Topmost
        extreme_points[3] = tuple(cnt[cnt[:,:,1].argmax()][0]) # Bottommost
        # Find extreme points of rectangle
        extreme_points_box[0] = tuple(self.box_platform[self.box_platform[:,:,0].argmin()][0]) # Leftmost
        extreme_points_box[1] = tuple(self.box_platform[self.box_platform[:,:,0].argmax()][0]) # Rightmost
        extreme_points_box[2] = tuple(self.box_platform[self.box_platform[:,:,1].argmin()][0]) # Topmost
        extreme_points_box[3] = tuple(self.box_platform[self.box_platform[:,:,1].argmax()][0]) # Bottommost
        # Put all relevant points into different list
        extreme_x_y[0] = extreme_points[0][0]
        extreme_x_y[1] = extreme_points[1][0]
        extreme_x_y[2] = extreme_points[2][1]
        extreme_x_y[3] = extreme_points[3][1]
        # Repeat for rectangle
        extreme_x_y_box[0]

        # Find if the mins and maxes are within bounding rectangle
        # x dimenstions
        for i in self.box_platform:
            if
        # Find if the cookie is within min and max bounds
        # x-coordinates
"""
