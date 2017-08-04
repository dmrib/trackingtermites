"""This module contains the termite tracking functionalities."""

import sys
import random
import cv2

class Termite:
    def __init__(self, starting_point, box_size=20):
        self.position = starting_point
        self.box_size = box_size
        self.color = tuple([random.randint(0, 256), random.randint(0, 256), random.randint(0, 256)])
        self.tracker = None


class Experiment:
    def __init__(self, n_termites, method, video_source, box_size = 20, video_source_size=(640, 480)):
        self.termites = []
        self.n_termites = n_termites
        self.method = method
        self.box_size = box_size
        self.video_source = cv2.VideoCapture(video_source)
        self.video_source_size = video_source_size
        self.locate_termites()

    def locate_termites(self):
        if not self.video_source.isOpened():
            print('Could not open video.')
            sys.exit()

        ok, frame = self.video_source.read()
        frame = cv2.resize(frame, self.video_source_size)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if not ok:
            print('Could not read video file.')
            sys.exit()

        for _ in range(self.n_termites):
            starting_point = cv2.selectROI(frame, False)
            starting_box = (starting_point[0], starting_point[1], self.box_size, self.box_size)
            termite = Termite(starting_point, self.box_size)
            termite.tracker = cv2.Tracker_create(self.method)
            termite.tracker.init(gray, starting_box)
            self.termites.append(termite)

    def update_termites(self, frame):
        for termite in self.termites:
            ok, termite.position = termite.tracker.update(frame)

    def draw(self, frame):
        for termite in self.termites:
            origin = (int(termite.position[0]), int(termite.position[1]))
            end = (int(termite.position[0] + termite.position[2]),
                  int(termite.position[1] + termite.position[3]))
            cv2.rectangle(frame, origin, end, termite.color)

    def track_all(self):
        while True:
            ok, frame = self.video_source.read()
            if not ok:
                break
            else:
                frame = cv2.resize(frame, self.video_source_size)
                self.update_termites(frame)
                self.draw(frame)
                cv2.imshow("Tracking", frame)

            k = cv2.waitKey(1) & 0xff
            if k == 27:
                break


def track(method, video_source, template):
    """Track a single termite sample in video input.

    Args:
        method (str): tracking algorithm name.
        video_source (str): video path.
        template (str): termite template path.

    Returns:
        None.

    """
    trackerA = cv2.Tracker_create(method)
    trackerB = cv2.Tracker_create(method)
    video = cv2.VideoCapture(video_source)
    box_size = 20

    if not video.isOpened():
        print('Could not open video.')
        sys.exit()

    ok, frame = video.read()
    if not ok:
        print('Could not read video file.')
        sys.exit()

    frame = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    starting_pointA = cv2.selectROI(frame, False)
    termite_positionA = (starting_pointA[0], starting_pointA[1], box_size, box_size)

    starting_pointB = cv2.selectROI(frame, False)
    termite_positionB = (starting_pointB[0], starting_pointB[1], box_size, box_size)

    trackerA.init(gray, termite_positionA)
    trackerB.init(gray, termite_positionB)

    while True:
        ok, frame = video.read()
        if not ok:
            break

        frame = cv2.resize(frame, (640, 480))
        ok, termite_positionA = trackerA.update(frame)
        ok, termite_positionB = trackerB.update(frame)

        if ok:
            pA1 = (int(termite_positionA[0]), int(termite_positionA[1]))
            pA2 = (int(termite_positionA[0] + termite_positionA[2]),
                  int(termite_positionA[1] + termite_positionA[3]))



        if ok:
            pB1 = (int(termite_positionB[0]), int(termite_positionB[1]))
            pB2 = (int(termite_positionB[0] + termite_positionB[2]),
                  int(termite_positionB[1] + termite_positionB[3]))



        if (termite_positionA[0] < termite_positionB[0] + box_size and
            termite_positionA[0] + box_size > termite_positionB[0] and
            termite_positionA[1] < termite_positionB[1] + box_size and
            box_size + termite_positionA[1] > termite_positionB[1]):
            cv2.rectangle(frame, pB1, pB2, (255, 0, 0))
            cv2.rectangle(frame, pA1, pA2, (255, 0, 0))
        else:
            cv2.rectangle(frame, pA1, pA2, (0, 0, 255))
            cv2.rectangle(frame, pB1, pB2, (0, 255, 0))

        cv2.imshow("Tracking", frame)

        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break


if __name__ == '__main__':
    #ex = Experiment(4, 'KCF', '../data/00012.MTS')
    #ex.track_all()
    track('KCF', '../data/00012.MTS', '../data/sample2.jpg')
