import cv2
import matplotlib.pyplot as plt
import numpy as np


def tutorial_one():
    img = cv2.imread('images/termite-01.jpg', cv2.IMREAD_GRAYSCALE)
    cv2.imshow('img' ,img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def tutorial_two():
    cap = cv2.VideoCapture(-1)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640,480))
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
    img = cv2.imread('images/termite-01.jpg', cv2.IMREAD_COLOR)

    cv2.line(img, (0, 0), (30, 150), (0, 0, 0), 5)
    cv2.rectangle(img, (40,0), (60, 20), (0, 255, 0), 5)
    cv2.circle(img, (60, 60), 30, (0, 0, 255), -1)

    pts = np.array([[10,5], [40,21], [30,90]], np.int32)
    cv2.polylines(img, [pts], True, (255, 255, 0), 3)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'OpenCV', (0, 100), font, 1, (200, 120, 30), 2, cv2.LINE_AA)

    cv2.imshow('img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()

def tutorial_four():
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
    cap = cv2.VideoCapture(-1)

    while True:
        _, frame = cap.read()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array([0, 255, 255])
        upper = np.array([255, 255, 255])

        mask = cv2.inRange(hsv, lower, upper)
        res = cv2.bitwise_and(frame, frame, mask=mask)

        cv2.imshow('raw', frame)
        cv2.imshow('mask', mask)
        cv2.imshow('res', res)

        q = cv2.waitKey(5) & 0xFF
        if q == 27:
            break

def tutorial_six():
    cap = cv2.VideoCapture(-1)

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
    img = cv2.imread('images/patri.jpg', 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template = cv2.imread('images/termite-04.jpg', 0)

    w, h = template.shape[::-1]

    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.2
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        cv2.rectangle(img, pt, (pt[0]+w, pt[1]+h), (0,255,255), 1)

    cv2.imshow('detected', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def first_try():
    img = cv2.imread('images/otto-1.jpg', 1)
    img = cv2.resize(img, (0,0), fx=0.3, fy=0.3)
    template = cv2.imread('images/otto-template.png', 1)

    font = cv2.FONT_HERSHEY_SIMPLEX

    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.7325
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        cv2.putText(img, 'Cat', pt, font, 1, (200, 120, 30), 2, cv2.LINE_AA)

    cv2.imshow('detected', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    first_try()
