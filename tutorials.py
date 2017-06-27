"""Module containing tutorials code. This ain't going to development code."""

import cv2
import matplotlib.pyplot as plt
import numpy as np


def tutorial_one():
    """Read and display images."""
    img = cv2.imread('images/termite-01.jpg', cv2.IMREAD_GRAYSCALE)
    cv2.imshow('img', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def tutorial_two():
    """
    Read video capture and convert to greyscale.

    Both outputs are shown to user. The original version is saved as
    output.avi.
    """
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        out.write(frame)
        cv2.imshow('frame', frame)
        cv2.imshow('gray', gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


def tutorial_three():
    """Draw forms on a image and display result."""
    img = cv2.imread('images/termite-01.jpg', cv2.IMREAD_COLOR)

    cv2.line(img, (0, 0), (30, 150), (0, 0, 0), 5)
    cv2.rectangle(img, (40, 0), (60, 20), (0, 255, 0), 5)
    cv2.circle(img, (60, 60), 30, (0, 0, 255), -1)

    pts = np.array([[10, 5], [40, 21], [30, 90]], np.int32)
    cv2.polylines(img, [pts], True, (255, 255, 0), 3)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'OpenCV', (0, 100), font, 1, (200, 120, 30), 2,
                cv2.LINE_AA)

    cv2.imshow('img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


def tutorial_four():
    """Select, print and changes arbitrary regions of interest in image."""
    img = cv2.imread('images/termite-01.jpg', cv2.IMREAD_COLOR)

    px = img[55, 55]
    print(px)

    img[55, 55] = [255, 255, 255]
    print(img[55, 55])

    roi = img[10: 30][10: 60]
    print(roi)

    img[10: 30][10: 60] = (0, 0, 0)
    cv2.imshow('img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


def tutorial_five():
    """Perform red color filtering."""
    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red = np.array([30, 150, 50])
        upper_red = np.array([255, 255, 180])

        mask = cv2.inRange(hsv, lower_red, upper_red)
        res = cv2.bitwise_and(frame, frame, mask=mask)

        cv2.imshow('raw', frame)
        cv2.imshow('mask', mask)
        cv2.imshow('res', res)

        q = cv2.waitKey(5) & 0xFF
        if q == 27:
            break


def tutorial_six():
    """Apply edge detection filters."""
    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        canny = cv2.Canny(frame, 50, 50)

        cv2.imshow('original', frame)
        cv2.imshow('gray', gray)
        cv2.imshow('laplacian', laplacian)
        cv2.imshow('sobelx', sobelx)
        cv2.imshow('sobely', sobely)
        cv2.imshow('canny', canny)

        q = cv2.waitKey(5) & 0xFF
        if q == 27:
            break


def tutorial_seven():
    """Perform template matching."""
    img = cv2.imread('images/patri.jpg', 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template = cv2.imread('images/termite-04.jpg', 0)

    w, h = template.shape[::-1]

    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.5
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        cv2.rectangle(img, pt, (pt[0]+w, pt[1]+h), (0, 255, 255), 1)

    cv2.imshow('detected', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def first_try():
    """Indentify Otto via template matching."""
    img = cv2.imread('images/otto-1.jpg', 1)
    img = cv2.resize(img, (0, 0), fx=0.3, fy=0.3)
    template = cv2.imread('images/otto-template.png', 1)

    w, h, l = template.shape

    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.7325
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        cv2.rectangle(img, pt, (pt[0]+w, pt[1]+h), (0, 255, 255), 1)

    cv2.imshow('detected', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def tutorial_eight():
    """Feature detection on Otto."""
    img1 = cv2.imread('images/otto-template.png', 0)
    img2 = cv2.imread('images/otto-1.jpg', 0)

    orb = cv2.ORB_create()

    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    print(len(matches))

    img3 = cv2.drawMatches(img1, kp1, img2, kp2, matches[:5], None, flags=2)
    plt.imshow(img3)
    plt.show()


def tutorial_nine():
    """Haar cascade face, eyes, smile and cat face detection."""
    face_cascade = cv2.CascadeClassifier('haarcascades/'
                                         'haarcascade_frontalface_alt_tree'
                                         '.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_eye.xml')
    smile_cascade = cv2.CascadeClassifier('haarcascades/'
                                          'haarcascade_frontalcatface'
                                          '_extended.xml')

    cap = cv2.VideoCapture(0)

    while 1:
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]

            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh),
                              (0, 255, 0), 2)

            smiles = smile_cascade.detectMultiScale(roi_gray)
            for (sx, sy, sw, sh) in smiles:
                cv2.rectangle(roi_color, (sx, sy), (sx+sw, sy+sh),
                              (0, 0, 255), 2)

        cats = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in cats:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]

        cv2.imshow('img', img)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    tutorial_nine()
