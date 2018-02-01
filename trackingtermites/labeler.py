import pandas as pd
import json
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


if __name__ == '__main__':
    labeling = LabelingSession('data/Sample Experiment')
