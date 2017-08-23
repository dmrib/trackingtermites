"""This module contains abstractions for dealing with termites."""

import random
import math
import math


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
        self.distances = []
        self.path = [tuple([int(self.position[0]), int(self.position[1]), self.colliding_with, self.distances])]

    def detect_collisions(self, others):
        """Check if termite is colliding with others.

        Args:
            others (list): termites to be compared.
        Returns:
            None.
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

    def compute_distances(self, others, scale):
        """Compute the distace between the termite and the other samples.

        Args:
            others (list): termites to be compared.
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
