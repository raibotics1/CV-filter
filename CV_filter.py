# import libraries
import cv2
import numpy as np

camera = cv2.VideoCapture(0)  # output data from camera (parameter 0-webcam,1 for etc.-additional)
cv2.namedWindow('settings',cv2.WINDOW_AUTOSIZE) # creating a  settings window
if __name__ == '__main__':
    def nothing(*arg):
        pass

# create a Trackbar for settings and set a range of values
cv2.createTrackbar('h1', 'settings', 0, 255, nothing)
cv2.createTrackbar('s1', 'settings', 0, 255, nothing)
cv2.createTrackbar('v1', 'settings', 0, 255, nothing)
cv2.createTrackbar('h2', 'settings', 255, 255, nothing)
cv2.createTrackbar('s2', 'settings', 255, 255, nothing)
cv2.createTrackbar('v2', 'settings', 255, 255, nothing)
# set the initial and final parameters of HSV
cv2.setTrackbarPos('h1', 'settings', 0)
cv2.setTrackbarPos('h2', 'settings', 255)
cv2.setTrackbarPos('s1', 'settings', 0)
cv2.setTrackbarPos('s2', 'settings', 255)
cv2.setTrackbarPos('v1', 'settings', 0)
cv2.setTrackbarPos('v2', 'settings', 255)

while True:
    iSee = False  # flag: was the contour found?
    # normalized devation of colored object from the center of the frame in the range (-1:1)
    controlX = 0.0  #on the X-axis
    controlY = 0.0  # on the Y-axis
    success, frame = camera.read()  # reading the frame from the camera


    if success:  # if you read successfully
        height, width = frame.shape[0:2]  # Getting the frame  resolution
        # Reading the value of the trackbars
        h1 = cv2.getTrackbarPos('h1', 'settings')
        s1 = cv2.getTrackbarPos('s1', 'settings')
        v1 = cv2.getTrackbarPos('v1', 'settings')
        h2 = cv2.getTrackbarPos('h2', 'settings')
        s2 = cv2.getTrackbarPos('s2', 'settings')
        v2 = cv2.getTrackbarPos('v2', 'settings')
        # from the intial and final color of the filter
        h_min = np.array((h1, s1, v1), np.uint8)
        h_max = np.array((h2, s2, v2), np.uint8)
        # apply a filter to the frame in the HSV model
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # translate the frame from BGR to HSV
        binary = cv2.inRange(hsv, (h1, s1, v1), (h2, s2, v2)) # threshold frame processing

        roi = cv2.bitwise_and(frame, frame,mask=binary)  # using a mask, we select an object from the general frame

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_NONE)  # get the contours of the select areas

        if len(contours) != 0:  # if at least one contour is found
            maxc = max(contours, key=cv2.contourArea)  # maximum contour found
            moments = cv2.moments(maxc)  #  get a moment  this contour

            if moments["m00"] > 20:  # if the contour is larger than the area...
                cx = int(moments["m10"] / moments["m00"])  # find the coordinates of the center of the contour by x
                cy = int(moments["m01"] / moments["m00"])  # find the coordinates of the center of the contour by y

                iSee = True  # setting the flag that the contour is found
                controlX = 2 * (
                            cx - width / 2) / width  # find the deviation of the found object from the center
                # of the frame and normalize it
                controlY = -2 * (
                        cy - height / 2) / height
                cv2.drawContours(frame, maxc, -1, (0, 255, 0), 2)  # draw contour
                cv2.line(frame, (cx, 0), (cx, height), (0, 255, 0), 2)  # draw line for x
                cv2.line(frame, (0, cy), (width, cy), (0, 255, 0), 2)  # draw line for y

        cv2.putText(frame, 'iSee: {};'.format(iSee), (width - 600, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)  # text
        cv2.putText(frame, 'controlX: {:.2f}'.format(controlX), (width - 400, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)  # text
        cv2.putText(frame, 'controlY: {:.2f}'.format(controlY), (width - 200, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)  # text



        cv2.imshow('frame', frame)  # display all the frames on the screen
        cv2.imshow('binary', binary)
        cv2.imshow('roi', roi)

    if cv2.waitKey(1) == ord('q'):  #  exit, you need to press 'q' on the keyboard
        break

camera.release()
cv2.destroyAllWindows()
