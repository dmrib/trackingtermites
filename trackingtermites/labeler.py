import cv2
import json
import os


class LabelingSession():
    def __init__(self, source_folder_path):
        self._load_metadata(source_folder_path)
        self._load_termites(source_folder_path)
        self.termites = []

    def _load_metadata(self, source_folder_path):
        with open(os.path.join(source_folder_path, 'meta.json')) as metadata:
            self.metadata = json.load(metadata)


if __name__ == '__main__':
    labeling = LabelingSession('data/Sample Experiment')
    labeling.start()
