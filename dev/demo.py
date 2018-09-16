import cv2
import numpy as np
import pygame

from sklearn.cluster import KMeans

channels = 10
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(channels)



class Key:

    def __init__(self, note, sound):
        self.note = note #str
        self.sound = sound #Pygame Sound object
        self.isPlaying = False

    def stop(self):
        if self.isPlaying:
            self.isPlaying = False
            self.sound.stop()

    def play(self):
        if not self.isPlaying:
            self.isPlaying = True
            self.sound.play()

    def keyIsPlaying(self):
        return self.isPlaying

class Piano:

    def __init__(self):
        self.notes = self.initNotes() #List[str]
        self.keys = self.initKeys(self.notes) #Dict{str note: Key key}
        self.previousPressedNotes = []

    def initNotes(self):
        whites = "ABCDEFG"
        blacks = "ABDEG"
        octaves = range(3, 8)
        allNotes = []
        for i in octaves:
            for letter in whites:
                allNotes.append(letter + str(i))
            for letter in blacks:
                allNotes.append(letter + "b" + str(i))
        allNotes.append("C8") #the last note
        return allNotes

    def initKeys(self, notes):
        keys = {}
        for note in notes:
            soundPath = soundPath = "sounds/Piano.ff." + note + ".wav"
            rawSound = bytes(
                list(bytearray(
                    pygame.mixer.Sound(soundPath).get_raw()
                ))[ int((2**16)) : int((2**19)) ]
            )
            sound = pygame.mixer.Sound(rawSound)
            keys[note] = Key(note, sound)
        return keys

    def getNotes(self):
        return self.notes[:]

    def getKeys(self):
        return dict(self.keys)

    """
    string[] pressedNotes = List containing pressed notes

    Plays keys that are pressed. Stops keys that are not pressed.
    Call on every frame!
    """
    def playKeys(self, pressedNotes):
        if self.previousPressedNotes == pressedNotes:
            return
        for note in self.notes:
            if note in pressedNotes and not self.keys[note].keyIsPlaying():
                self.keys[note].play()
            elif note not in pressedNotes:
                self.keys[note].stop()
        self.previousPressedNotes = pressedNotes

    # def playKey(self, note):
    #     if not self.keys[note].keyIsPlaying():
    #         self.keys[note].play()
    #     return
    #
    # def stopKey(self, note):
    #     if self.keys[note].keyIsPlaying():
    #         self.keys[note].stop()


def getPoints():
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
    lower_color_range = np.array([30,80,120])
    upper_color_range = np.array([40,190,210])

    # generates a mask (binary image)
    mask = cv2.inRange(hsv, lower_color_range, upper_color_range)

    # this elimates small blobs by making every blobs shave off its exterior
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.erode(mask, kernel, iterations = 2)

    # Combines the mask with the blurred resized original to show what sensed,
    # and show what it looks like
    color_res = cv2.bitwise_and(blurred_resized_frame, blurred_resized_frame, mask= mask)

    # finds information about blobs, needed to find the centroids
    im2, contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    centroidList = []
    for c in contours:
        # calculate moments for each contour
        M = cv2.moments(c)

        # calculate x,y coordinate of center
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            # prints the centroids of every blob
            print(cX, cY)
            #
            # # adds a circle and text to the image to show the centroid
            # cv2.circle(color_res, (cX, cY), 5, (255, 255, 255), -1)
            # cv2.putText(color_res, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            centroidList.append([cX, cY])
        else: # this is needed if the centroid calculations ever fail
            cX, cY = 0, 0

    # Display the resulting frame
    cv2.imshow('frame', color_res)

    return centroidList



def isNearPixel(tolerance, originalPixel, testPixel):
    """ Returns true if a given pixel is withing the tolerance of the original pixel"""
    x = testPixel[0] < originalPixel[0] + tolerance and testPixel[0] > originalPixel[0] - tolerance
    y = testPixel[1] < originalPixel[1] + tolerance and testPixel[1] > originalPixel[1] - tolerance

    return (x and y)


def calibrate(note_list, number_of_notes):
    """ Applies k means clustering to a period where each note's location is set."""
    frameNumberCalibrate = 100

    pixelLocationList = number_of_notes * [[0, 0]]

    for i in range(numberOfNotes):
        print("Press note #" + str(i) + " - " + note_list[i])

        data_points = []

        for j in range(frameNumberCalibrate):
            data_points = data_points + getPoints()

        if len(data_points) == 0:
            data_points.append([0, 0])



        np_data_points = np.array(data_points)
        kmeans = KMeans(n_clusters=1)
        kmeans.fit(np_data_points)

        centroids = kmeans.cluster_centers_
        labels = kmeans.labels_
        pixelLocationList[i] = [int(centroids[0][0]), int(centroids[0][1])]
        print("calibrate: " + str(pixelLocationList[i]))
    return pixelLocationList

def noisy_pixels_to_notes(tolerance, pixels, pixelLocationList, note_list):
    """ Converts the pixels into a list of strings of the notes."""
    result_note_list = []
    for count, point in enumerate(pixels):
        for i in range(len(pixelLocationList)):
            if isNearPixel(tolerance, pixelLocationList[i], point):
                print(note_list[count] + " hhhhhhhhhjjjjjjjssdflkjslakdfjas;ldfkjas;ldkfjsldfja;ldsfkj")
                result_note_list.append(note_list[i])
    return result_note_list





if __name__ == "__main__":


    cap = cv2.VideoCapture(0)

    numberOfNotes = 25 # the total number of keys on the piano
    pixelLocationList = [] # stores the locations of the blobs after calibration
    tolerance = 15 # how many pixels off in each dimension the blob centroid can be

    note_list = ["C4", "Db4", "D4", "Eb4", "E4", "F4", "Gb4",
                 "G4", "Ab4", "A4", "Bb4", "B4",
                 "C5", "Db5", "D5", "Eb5", "E5", "F5", "Gb5",
                 "G5", "Ab5", "A5", "Bb5", "B5",
                 "C6"]

    pixelLocationList = calibrate(note_list, numberOfNotes)

    piano = Piano()

    #Example mapping of k presses to notes
    keyToNote = {121: "C3", 117:"E3", 105:"G3", 111:"C4"}
    #image = np.full((30,30), np.inf)
    while(1):
        #Example CV window open
        #cv2.imshow('image', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        pressedNotes = noisy_pixels_to_notes(tolerance, getPoints(), pixelLocationList, note_list)
        #Populate pressed Notes here
        piano.playKeys(pressedNotes)

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
