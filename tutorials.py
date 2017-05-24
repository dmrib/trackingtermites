import cv2
import matplotlib.pyplot as plt
import numpy as np


def tutorial_one():
    img = cv2.imread('images/termite-01.jpg', cv2.IMREAD_GRAYSCALE)
    cv2.imshow('img' ,img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    tutorial_one()
