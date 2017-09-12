"""This module contains abstractions for dealing with termites."""

import random
import math


class Termite:
    """Termite in an experiment."""
    def __init__(self, identity, starting_point, box_size):
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
        self.color = tuple([random.randint(0, 256), random.randint(0, 256),
                           random.randint(0, 256)])
        self.tracker = None
        self.path = []

    @property
    def origin(self):
        """Termite bounding box origin point."""
        return (int(self.position[0]), int(self.position[1]))

    @property
    def end(self):
        """Termite bounding box end point."""
        return (int(self.position[0] + self.position[2]),
                int(self.position[1] + self.position[3]))

    def detect_encounters(self, others):
        """Update termite encounters.

        Args:
            others (list): termites to be compared.
        Returns:
            None.
        """
        encountering_with = []
        for other in others:
            if other.identity != self.identity:
                if (self.position[0] < other.position[0] + self.box_size and
                    self.position[0] + self.box_size > other.position[0] and
                    self.position[1] < other.position[1] + self.box_size and
                    self.box_size + self.position[1] > other.position[1]):
                    encountering_with.append(other.identity)
        self.encountering_with = encountering_with

    def compute_distances(self, others, scale):
        """Compute the distace between the termite and the other samples.

        Args:
            others (list): termites to be compared.
            scale (float): distance of 1cm in pixels.
        Returns:
            None.
        """
        distances = []
        for other in others:
            origin = math.pow(int((self.position[0] - other.position[0])),2)
            destination = math.pow(int((self.position[1] - other.position[1])),2)
            distance = round(math.sqrt(origin + destination) / scale, 2)
            distances.append(distance)
        self.distances = distances

    def generate_output(self):
        """Create output string for a termite.

        Args:
            None.
        Returns:
            output (str): output string.
        """
        output = ''
        output += '# Termite number: {}\n'.format(self.identity)
        output += '# Color: {}\n\n'.format(self.color)
        output += ('###\n\n')
        output += ('frame, x, y, colliding, distances\n')
        for frame, location in enumerate(self.path):
            output += 'f{}, {}, {}, {}, {}\n'.format(frame, location[0], location[1], location[2], location[3])

        return output
