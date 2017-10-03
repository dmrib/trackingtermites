"""Termite detection using TensorFlow Object Detection API."""


import glob

import termites as trmt


class TermiteImageDataset:
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

    def to_csv(self, destination):
        """Write dataset in csv representation.

        Args:
            destination (str): files destination path.
        Returns:
            None.
        """
        with open(destination, mode='w') as csv_file:
            csv_file.write('filename, width, height, class, xmin, ymin, xmax, ymax\n')
            for termite in self.termites:
                for path_number, path in enumerate(termite.trail):
                    csv_file.write('{}-{}.png, {}, {}, {}, {}, {}, {}, {}\n'.format(
                        termite.movie_name[:-4],
                        path_number+1,
                        termite.movie_shape[0],
                        termite.movie_shape[1],
                        termite.movie_name[:3],
                        path[0],
                        path[1],
                        path[0] + termite.bounding_box_size,
                        path[1] + termite.bounding_box_size,
                    ))


if __name__ == '__main__':
    dat = TermiteImageDataset('../data/development/')
    dat.create_dataset()
    dat.to_csv('../data/dataset.csv')
