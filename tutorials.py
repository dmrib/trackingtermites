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

if __name__ == '__main__':
    tutorial_two()
