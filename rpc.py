import numpy as np
import cv2

cap = cv2.VideoCapture(0)

#Loops infinitely, until broken by the break statement.
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # resize to make the operations run faster
    resized_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    # blur to make the colors more consistent, removing noise
    blurred_resized_frame = cv2.blur(resized_frame, (5, 5))

    # Convert to HSV color space - good for searching by color (hue), saturation
    # and value. This is like the "color picker" - select color, and how white
    # and how black
    hsv = cv2.cvtColor(blurred_resized_frame, cv2.COLOR_BGR2HSV)

    #These set the range of permissible colors
    lower_color_range = np.array([20,80,80])
    upper_color_range = np.array([30,180,180])

    # generates a mask (binary image)
    mask = cv2.inRange(hsv, lower_color_range, upper_color_range)

    # this elimates small blobs by making every blobs shave off its exterior
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.erode(mask, kernel, iterations = 3)

    # Combines the mask with the blurred resized original to show what sensed,
    # and show what it looks like
    color_res = cv2.bitwise_and(blurred_resized_frame, blurred_resized_frame, mask= mask)

    # finds information about blobs, needed to find the centroids
    im2, contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        # calculate moments for each contour
        M = cv2.moments(c)

        # calculate x,y coordinate of center
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            # prints the centroids of every blob
            print(cX, cY)

            # adds a circle and text to the image to show the centroid
            cv2.circle(color_res, (cX, cY), 5, (255, 255, 255), -1)
            cv2.putText(color_res, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        else: # this is needed if the centroid calculations ever fail
            cX, cY = 0, 0
        cv2.circle(color_res, (cX, cY), 5, (255, 255, 255), -1)
        cv2.putText(color_res, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


    # Display the resulting frame
    cv2.imshow('frame', color_res)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
