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
            edges = cv2.Canny(frame, 75, 75)
            edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            evaluation = np.hstack((frame, edges))
            evaluation = cv2.resize(evaluation, (0,0), fx=5,
                                                fy=5)
            cv2.imshow('Labeling', evaluation)
            pressed_key = cv2.waitKey(0) & 0xff
            if chr(pressed_key) in self.settings['events']:
                path = os.path.join(self.settings['output_path'],
                                    self.settings['events'][chr(pressed_key)] +
                                    '/' + str(image_id) + '.jpg')
                cv2.imwrite(path, frame)

            if pressed_key == 27:
                sys.exit()


class OnlineLabeler():
    def __init__(self, settings_file):
        self._load_settings(settings_file)
        self._load_termites()
        self.focal = self.settings['focal'] - 1
        self.video = cv2.VideoCapture(self.settings['video_path'])

    def _load_settings(self, settings_file):
        '''Load labeling session settings file.

        Args:
            settings_file (str): path to tracking session settings file.
        Retuns:
            None.
        '''
        with open(settings_file) as settings:
            self.settings = json.load(settings)

    def _load_termites(self):
        '''Load termite data from source folder.

        Args:
            None.
        Returns:
            None.
        '''
        self.nest = trmt.Nest(self.settings['n_termites'], self.settings['source_folder'])
        self.nest.normalize()
        self.nest.compute_distances()
        self.nest.compute_encounters(65)

    def label(self):
        '''Start labeling session.

        Args:
            None.
        Returns:
            None.
        '''
        frames_number = len(self.nest.termites[0].trail['label'])
        for f_number in range(1, frames_number):
            playing, frame = self.video.read()
            if not playing:
                sys.exit()
            frame = cv2.resize(frame, (0,0), fy=0.5, fx=0.5)
            t_pos = (int(self.nest.termites[self.focal].trail.loc[f_number, 'x']), int(self.nest.termites[self.focal].trail.loc[f_number, 'y']))
            cv2.circle(frame, t_pos, 3, self.nest.termites[self.focal].color, -1)
            cv2.putText(frame, 'Focal', (t_pos[0]-7, t_pos[1]-11), 2,
                        color=self.nest.termites[self.focal].color,
                        fontScale=0.4)
            for other in range(len(self.nest.termites)):
                if other != self.focal:
                    other_pos = (int(self.nest.termites[other].trail.loc[f_number, 'x']), int(self.nest.termites[other].trail.loc[f_number, 'y']))
                    if self.nest.termites[self.focal].trail.loc[f_number, 'distance_to_{}'.format(self.nest.termites[other].trail.loc[0, 'label'])] < 65:
                        half = ((t_pos[0]+other_pos[0])//2, (t_pos[1]+other_pos[1])//2)
                        event = frame[(half[1]-30):(half[1]+30),
                                      (half[0]-30):(half[0]+30)]
                        event = cv2.resize(event, (0,0), fy=2, fx=2)
                        edges = cv2.Canny(event, 75, 75)
                        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                        full = np.hstack((edges, event))
                        frame[0:full.shape[0], 0:full.shape[1]] = full
                        cv2.imshow('Encounters', frame)
                        pressed_key = cv2.waitKey(0) & 0xff
                        if pressed_key == 27:
                            sys.exit()
                        elif chr(pressed_key) in self.settings['events'].keys():
                            self.nest.termites[self.focal].trail.loc[f_number, 'interaction_with_{}'.format(self.nest.termites[other].trail.loc[0, 'label'])] = self.settings['events'][chr(pressed_key)]
        self.nest.save(self.settings['source_folder'])


if __name__ == '__main__':
    labeler = OnlineLabeler('settings/labeler.json')
    labeler.label()
