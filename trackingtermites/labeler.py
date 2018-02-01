import pandas as pd
import json
import numpy as np
import os


class LabelingSession():
    def __init__(self, source_folder_path):
        '''Initializer.

        Args:
            source_folder_path (str): path to folder containing tracking data.
        Returns:
            None.
        '''
        self.termites = []
        self._load_metadata(source_folder_path)
        self._load_termites(source_folder_path)

    def _load_metadata(self, source_folder_path):
        '''Load tracking metadata file.

        Args:
            source_folder_path (str): path to folder containing tracking data.
        Returns:
            None.
        '''
        with open(os.path.join(source_folder_path, 'meta.json')) as metadata:
            self.metadata = json.load(metadata)

    def _load_termites(self, source_folder_path):
        '''Load termite data.

        Args:
            source_folder_path (str): path to folder containing tracking data.
        Returns:
            None.
        '''
        for termite_number in range(1, self.metadata['n_termites'] + 1):
            file_name = '{}-trail.csv'.format(termite_number)
            file_path = os.path.join(source_folder_path, file_name)
            self.termites.append(pd.read_csv(file_path))

    def _compute_distances(self):
        '''Compute distances between termites on every experiment frame and
           updates dataframes.

        Args:
            None.
        Returns:
            None.
        '''
        for a_number, termite_a in enumerate(self.termites, start=1):
            for b_number, termite_b in enumerate(self.termites, start=1):
                if a_number != b_number:
                    distance = np.sqrt((((termite_a['x']-termite_b['x'])**2) +
                               ((termite_a['y']-termite_b['y'])**2)))
                    termite_a['distance_to_{}'.format(b_number)] = distance

    def start(self):
        '''Starts labeling session.

        Args:
            None.
        Returns:
            None.
        '''
        self._compute_distances()


if __name__ == '__main__':
    labeling = LabelingSession('data/Sample Experiment')
    labeling.start()
