import cv2
import json
import numpy as np
import os
import pandas as pd
import sys
import termite as trmt
import glob


class OfflineLabeler():
    def __init__(self, settings_file):
        '''Initializer.

        Args:
            settings_path (str): path to settings file.
        Returns:
            None.
        '''
        self.paths = []
        self._load_settings(settings_file)
        self.collect_paths()

    def _load_settings(self, settings_file):
        '''Load labeling session settings file.

        Args:
            settings_file (str): path to tracking session settings file.
        Retuns:
            None.
        '''
        with open(settings_file) as settings:
            self.settings = json.load(settings)

    def _create_collections(self):
        '''Create labeled images folders.

        Args:
            None.
        Returns:
            None.
        '''
        for event in self.settings['events'].values():
            folder_name = os.path.join(self.settings['output_path'], event)
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

    def collect_paths(self):
        '''Get all images paths in the images folder.

        Args:
            None.
        Returns:
            None.
        '''
        self.paths = [x for x in glob.glob(self.settings['images_folder']+'*.jpg')]

    def augment_dataset(self):
        '''Artificially augment dataset.

        Args:
            None.
        Returns:
            None.
        '''
        print('Augmenting dataset...')
        for folder in self.settings['events'].values():
            labeled = glob.glob(os.path.join(self.settings['images_folder'],
                                folder + '/*.jpg'))
            for image in labeled:
                frame = cv2.imread(image)
                artificial = cv2.flip(frame, 0)
                cv2.imwrite(image[:-4]+'-a1'+image[-4:], artificial)
                artificial = cv2.flip(frame, 1)
                cv2.imwrite(image[:-4]+'-a2'+image[-4:], artificial)
                artificial = cv2.flip(artificial, 0)
                cv2.imwrite(image[:-4]+'-a3'+image[-4:], artificial)

    def label(self):
        '''Start hand labeling loop.

        Args:
            None.
        Returns:
            None.
        '''
        self._create_collections()
        number_of_images = len(self.paths)
        for image_id, path in enumerate(self.paths):
            print('Image {} of {}'.format(image_id+1, number_of_images))
            frame = cv2.imread(path)
            cv2.imshow('Labeling', frame)
            pressed_key = cv2.waitKey(0) & 0xff
            if chr(pressed_key) in self.settings['events']:
                path = os.path.join(self.settings['output_path'],
                                    self.settings['events'][chr(pressed_key)] +
                                    '/' + str(image_id) + '.jpg')
                cv2.imwrite(path, frame)

            if pressed_key == 27:
                sys.exit()


if __name__ == '__main__':
    labeler = OfflineLabeler('settings/labeler.json')
    labeler.label()
