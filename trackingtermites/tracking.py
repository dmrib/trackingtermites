"""This module contains the termite tracking functionalities."""

import sys
import random
import cv2

class Termite:
    """Termite under study abstraction."""
    def __init__(self, starting_point, box_size=20):
        """Initializer.

        Args:
            starting_point (tuple): y and x values for termite starting point.
            box_size (int): bounding box size.
        Returns:
            None.
        """
        self.position = starting_point
        self.box_size = box_size
        self.color = tuple([random.randint(0, 256), random.randint(0, 256), random.randint(0, 256)])
        self.tracker = None


class Experiment:
    """Tracking experiment abstraction."""
    def __init__(self, n_termites, method, video_source, box_size = 20, video_source_size=(640, 480)):
        """Initializer.

        Args:
            input_path (str): path of input file.
            output_path (str): path for output file.
        Returns:
            None.

        """
        self.termites = []
        self.n_termites = n_termites
        self.method = method
        self.box_size = box_size
        self.video_source = cv2.VideoCapture(video_source)
        self.video_source_size = video_source_size
        self.locate_termites()

    def locate_termites(self):
        """Open GUI tool for selecting termite to be tracked.

        Args:
            None.
        Returns:
            None.
        """
        if not self.video_source.isOpened():
            print('Could not open video.')
            sys.exit()

        ok, frame = self.video_source.read()
        if not ok:
            print('Could not read video file.')
            sys.exit()
        frame = cv2.resize(frame, self.video_source_size)

        for _ in range(self.n_termites):
            starting_point = cv2.selectROI(frame, False)
            starting_box = (starting_point[0], starting_point[1], self.box_size, self.box_size)
            termite = Termite(starting_point, self.box_size)
            termite.tracker = cv2.Tracker_create(self.method)
            termite.tracker.init(frame, starting_box)
            self.termites.append(termite)

    def update_termites(self, frame):
        """Update termite position to the one in the passed frame.

        Args:
            frame (numpy.ndarray): video frame.

        Returns:
            None.
        """
        for termite in self.termites:
            ok, termite.position = termite.tracker.update(frame)

    def draw(self, frame):
        """Draw bounding box in the tracked termites.

        Args:
            frame (numpy.ndarray): video frame.

        Returns:
            None.
        """
        for termite in self.termites:
            origin = (int(termite.position[0]), int(termite.position[1]))
            end = (int(termite.position[0] + termite.position[2]),
                  int(termite.position[1] + termite.position[3]))
            cv2.rectangle(frame, origin, end, termite.color)

    def track_all(self):
        """Start tracking loop.

        Args:
            None.
        Returns:
            None.
        """
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


if __name__ == '__main__':
    ex = Experiment(3, 'KCF', '../data/movie01-n4.MTS')
    ex.track_all()
