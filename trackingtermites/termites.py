"""This module contains abstractions for dealing with termites."""

import random
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
        """Check if termite is encountering with others.

        Args:
            others (list): termites to be compared.
        Returns:
            None.
        """
        encountering_with = []
        for other in others:
            if other.identity != self.identity:
                if (self.position[1] < other.position[1] + self.box_size and
                    self.position[1] + self.box_size > other.position[1] and
                    self.position[0] < other.position[0] + self.box_size and
                    self.box_size + self.position[0] > other.position[0]):
                    encountering_with.append(other.identity)
        self.encountering_with = encountering_with

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
        output += ('frame, y, x, colliding, distances\n')
        for frame, location in enumerate(self.path):
            output += '{}, {}, {}, {}, {}\n'.format(frame, location[0], location[1], location[2], location[3])

        return output


class TermiteTrail:
    """Convenient representation of a termite path on video for TensorFlow record creation."""
    def __init__(self, source_path):
        """Initializer.

        Args:
            source_path (str): path of trail source file.
        Returns:
            None.
        """
        self.source_path = source_path
        self.meta = {}
        self.trail = []

    def load(self):
        """Read data from source file.

        Args:
            None.
        Returns:
            None.
        """
        meta = {}
        trail = []
        with open(self.source_path, mode='r', encoding='utf-8') as data_file:
            header = data_file.readlines()[:7]
            for line in header:
                line = line.lstrip('# ')
                data = line.split()
                if data[0] == 'Movie':
                    if data[1] == 'name:':
                        meta['movie_name'] = data[2].rstrip('\n')
                    else:
                        meta['movie_size'] = (int(data[2].rstrip(',')), int(data[3].rstrip('\n')))
                elif data[0] == 'Bounding':
                    meta['b_box_size'] = int(data[3])
        with open(self.source_path, mode='r', encoding='utf-8') as data_file:
            data = data_file.readlines()[11:]
            for line in data:
                line = line.split()
                trail.append((int(line[1].rstrip(',')), int(line[2].rstrip(','))))

        self.meta.update(meta)
        self.trail.extend(trail)
