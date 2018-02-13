import cv2
import json
import numpy as np
import os
import pandas as pd
import sys
import termite as trmt


class Scraper():
    def __init__(self, settings_path):
        '''Initializer.

        Args:
            settings_path (str): path to settings file.
        Returns:
            None.
        '''
        self.termites = []

        self._load_settings(settings_path)
        self._load_metadata()
        self._load_termites()


        self.video = cv2.VideoCapture(self.metadata['video_path'])


    def _load_metadata(self):
        '''Load tracking metadata file.

        Args:
            None.
        Returns:
            None.
        '''
        with open(os.path.join(self.settings['source_folder'], 'meta.json')) as metadata:
            self.metadata = json.load(metadata)

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
        '''Load termite data.

        Args:
            None.
        Returns:
            None.
        '''
        for termite_number in range(1, self.metadata['n_termites'] + 1):
            label = 't' + str(termite_number)
            file_name = '{}-trail.csv'.format(label)
            file_path = os.path.join(self.settings['source_folder'], file_name)
            termite = trmt.Termite(label)
            termite.from_csv(file_path)
            self.termites.append(termite)

    def _compute_distances(self):
        '''Compute distances between termites on every experiment frame and
           updates dataframes.

        Args:
            None.
        Returns:
            None.
        '''
        for termite in self.termites:
            termite.trail['x'] = termite.trail['x'] + termite.trail['xoffset']/2
            termite.trail['y'] = termite.trail['y'] + termite.trail['yoffset']/2

        for a_number, termite_a in enumerate(self.termites, start=1):
            for b_number, termite_b in enumerate(self.termites, start=1):
                if a_number != b_number:
                    distance = np.sqrt((((termite_a.trail['x']-termite_b.trail['x'])**2) +
                               ((termite_a.trail['y']-termite_b.trail['y'])**2)))
                    termite_a.trail['distance_to_t{}'.format(b_number)] = distance
                    termite_a.trail['interaction_with_t{}'.format(b_number)] = 'no-interaction'

    def scrape(self):
        '''Starts labeling session.

        Args:
            None.
        Returns:
            None.
        '''
        self._compute_distances()
        entries_number = len(self.termites[0].trail['frame'].values)

        for frame_number in range(1, entries_number):
            playing, frame = self.video.read()
            if not playing:
                print('The end.')
                sys.exit()
            frame = cv2.resize(frame, (0,0), fx=self.metadata['resize_ratio'],
                               fy=self.metadata['resize_ratio'])
            print('Scraping on frame {} of {}'.format(frame_number, entries_number-1))


            for n_termite in range(len(self.termites)):
                predicted = (int(self.termites[n_termite].trail.loc[frame_number, 'x']), int(self.termites[n_termite].trail.loc[frame_number, 'y']))
                for other in range(n_termite+1, len(self.termites)):
                    other_predicted = (int(self.termites[other].trail.loc[frame_number, 'x']), int(self.termites[other].trail.loc[frame_number, 'y']))
                    if self.termites[n_termite].trail.loc[frame_number, 'distance_to_{}'.format(self.termites[other].trail.loc[0, 'label'])] < self.settings['distance_threshold']:
                        half = ((predicted[0]+other_predicted[0])//2, (predicted[1]+other_predicted[1])//2)
                        event = frame[(half[1]-self.settings['collection_edge']):(half[1]+self.settings['collection_edge']),
                                      (half[0]-self.settings['collection_edge']):(half[0]+self.settings['collection_edge'])]
                        cv2.imwrite(self.settings['output_path']+'{}-t{}-t{}.jpg'.format(frame_number, n_termite, other), event)


if __name__ == '__main__':
    scraper = Scraper('settings/scraper.json')
    scraper.scrape()
