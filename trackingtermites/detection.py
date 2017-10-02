"""Termite detection using TensorFlow Object Detection API."""


import glob

import termites as trmt


class Dataset:
    """Termite image dataset abstraction."""
    def __init__(self, trails_folder):
        """Initializer.

        Args:
            trails_folder (str): path to folder containing termites source files.
        Returns:
            None.
        """
        self.trails_folder = trails_folder
        self.termites = []

    def create_dataset(self):
        """Create termite image dataset from trackers output files.

        Args:
            None.
        Returns:
            None.
        """
        termites_files = glob.glob('{}termite*'.format(self.trails_folder))
        self.load_termites(termites_files)

    def load_termites(self, termites_files):
        """Load termites trails from given files.

        Args:
            None.
        Returns:
            None.
        """
        for trail in termites_files:
            self.termites.append(trmt.TermiteRecord(trail))


if __name__ == '__main__':
    dat = Dataset('../data/development/')
    dat.create_dataset()
