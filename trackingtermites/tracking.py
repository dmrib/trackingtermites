"""This module contains the termite tracking functionalities."""

import sys
import random
import cv2

import data


class Termite:
    """Termite under study abstraction."""
    def __init__(self, identity, starting_point, box_size=20):
        """Initializer.

        Args:
            identity (int): termite identity on video
            starting_point (tuple): y and x values for termite starting point.
            box_size (int): bounding box size.
        Returns:
            None.
        """
        self.identity = identity
        self.position = starting_point
        self.box_size = box_size
        self.color = tuple([random.randint(0, 256), random.randint(0, 256), random.randint(0, 256)])
        self.tracker = None
        self.colliding_with = []
        self.path = [tuple([self.position[0], self.position[1], self.colliding_with])]

    def detect_collisions(self, others):
        """Check if termite is colliding with others.

        Args:
            others (list): termites to be compared.
        Returns:
            colliding (bool): True if the termite is colliding.
        """
        colliding_with = []
        for other in others:
            if other.identity != self.identity:
                if (self.position[1] < other.position[1] + self.box_size and
                    self.position[1] + self.box_size > other.position[1] and
                    self.position[0] < other.position[0] + self.box_size and
                    self.box_size + self.position[0] > other.position[0]):
                    colliding_with.append(other.identity)
        self.colliding_with = colliding_with


class Experiment:
    """Tracking experiment abstraction."""
    def __init__(self, input_path, output_path):
        """Initializer.

        Args:
            input_path (str): path of input file.
            output_path (str): path for output file.
        Returns:
            None.

        """
        self.termites = []
        self.data_handler = data.DataHandler(input_path, output_path)
        self.params = self.data_handler.load_input()
        self.video_source = cv2.VideoCapture(self.params['video_source'])
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
        frame = cv2.resize(frame, self.params['video_source_size'])

        for t_number in range(self.params['n_termites']):
            starting_point = cv2.selectROI(frame, False)
            starting_box = (starting_point[0], starting_point[1], self.params['box_size'], self.params['box_size'])
            termite = Termite(t_number+1, starting_point, self.params['box_size'])
            termite.tracker = cv2.Tracker_create(self.params['method'])
            termite.tracker.init(frame, starting_box)
            self.termites.append(termite)

    def update_termites(self, frame):
        """Update termites positions.

        Args:
            frame (numpy.ndarray): next video frame.

        Returns:
            None.
        """
        for termite in self.termites:
            ok, termite.position = termite.tracker.update(frame)
            termite.detect_collisions(self.termites)
            termite.path.append([int(termite.position[0]), int(termite.position[1]), termite.colliding_with])

    def draw(self, frame):
        """Draw bounding box in the tracked termites.

        Args:
            frame (numpy.ndarray): next video frame.

        Returns:
            None.
        """
        for termite in self.termites:
            origin = (int(termite.position[0]), int(termite.position[1]))
            end = (int(termite.position[0] + termite.position[2]),
                  int(termite.position[1] + termite.position[3]))
            if termite.colliding_with:
                cv2.rectangle(frame, origin, end, termite.color, 5)
            else:
                cv2.rectangle(frame, origin, end, termite.color)

    def track_all(self):
        """Start tracking loop.

        Args:
            None.
        Returns:
            None.
        """
        ok = True
        while ok:
            ok, frame = self.video_source.read()
            if not ok:
                break
            else:
                frame = cv2.resize(frame, self.params['video_source_size'])
                self.update_termites(frame)
                self.draw(frame)
                cv2.imshow("Tracking", frame)

            k = cv2.waitKey(1) & 0xff
            if k == 27:
                self.data_handler.write_output(self.params, self.termites)
                break

        self.data_handler.write_output(self.params, self.termites)


if __name__ == '__main__':
    ex = Experiment('../data/sample_input.txt', '')
    ex.track_all()
