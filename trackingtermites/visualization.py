import cv2
import json
import os
import numpy as np
import pandas as pd
import sys
import termite as trmt


class TrackingVisualization():
    def __init__(self, settings_file_path):
            '''Initializer.

            Args:
                settings_file_path (str): path to tracking session settings file.
            Returns:
                None.
            '''
            self.termites = []
            self._load_settings(settings_file_path)
            self._load_termites()
            self._load_video()

    def _load_settings(self, settings_file_path):
        '''Load tracking session visualization settings.

        Args:
            settings_file_path (str): path to tracking session settings file.
        Returns:
            None.
        '''
        with open(settings_file_path) as settings_file:
            self.settings = json.load(settings_file)

    def _load_termites(self):
        '''Load termite tracking session output from source folder.

        Args:
            None.
        Returns:
            None.
        '''
        for termite_number in range(1, self.settings['n_termites'] + 1):
            label = 't' + str(termite_number)
            file_name = '{}-trail.csv'.format(label)
            file_path = os.path.join(self.settings['source_folder'], file_name)
            termite = trmt.Termite(label)
            termite.from_csv(file_path)
            self.termites.append(termite)

        self._adjust_predictions()

    def _load_video(self):
        '''Load video and video writer.

        Args:
            None.
        Returns:
            None.
        '''
        self.video = cv2.VideoCapture(self.settings['video_path'])
        self.shape = (int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH)*self.settings['resize_ratio']),
                      int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)*self.settings['resize_ratio']))
        self.out = cv2.VideoWriter('{}/{}.avi'.format(self.settings['source_folder'],
                              self.settings['experiment_name']),
                              cv2.VideoWriter_fourcc(*'MJPG'), 30.0, self.shape)

    def _adjust_predictions(self):
        '''Adjust termites x and y components to better postion predictions.

        Args:
            None.
        Returns:
            None.
        '''
        for termite in self.termites:
            termite.normalize()

    def _draw_frame_info(self):
        '''Draw frame info on current frame.

        Args:
            None.
        Returns:
            None.
        '''
        cv2.putText(self.frame, 'Frame #{} of {}, {}ms delay.'.format(
                    int(self.video.get(cv2.CAP_PROP_POS_FRAMES)),
                    len(self.termites[0].trail),
                    self.settings['movie_speed']), (5,10), 1, color=(0, 0, 255),
                    fontScale=0.7)

    def _draw_termites(self):
        '''Draw termites' positions on current frame.

        Args:
            None.
        Returns:
            None.
        '''
        for termite in self.termites:
            position = (int(termite.trail.loc[self.step,'x']),
                        int(termite.trail.loc[self.step,'y']))
            cv2.circle(self.frame, position, 3, termite.color, -1)
            cv2.circle(self.frame, position, 8, termite.color, 2)
            cv2.putText(self.frame, 'w'+termite.label[-1], (position[0]-7, position[1]-11), 2, color=termite.color,
                        fontScale=0.4)

    def _draw_trails(self):
        '''Draw termites' trails on current frame.

        Args:
            None.
        Returns:
            None.
        '''
        for termite in self.termites:
            f_trail = termite.trail.iloc[self.step:min(len(self.termites[0].trail), self.step+5)]
            for future in f_trail.itertuples():
                cv2.circle(self.frame, (int(future.x), int(future.y)), 2,
                           termite.color, -1)

            p_trail = termite.trail.iloc[max(0, self.step-5):self.step]
            for past in p_trail.itertuples():
                cv2.circle(self.frame, (int(past.x), int(past.y)), 2,
                           termite.color, -1)

    def show(self):
        '''Start tracking session visualization.

        Args:
            None.
        Returns:
            None.
        '''
        for self.step in range(1, len(self.termites[0].trail)):
            self.playing, self.frame = self.video.read()
            if not self.playing:
                sys.exit()
            self.frame = cv2.resize(self.frame, (0,0), fx=self.settings['resize_ratio'],
                                    fy=self.settings['resize_ratio'])
            self._draw_frame_info()
            self._draw_termites()
            self._draw_trails()

            cv2.imshow(self.settings['experiment_name'], self.frame)
            self.out.write(self.frame)

            pressed_key = cv2.waitKey(self.settings['movie_speed']) & 0xff
            if pressed_key == 27:
                sys.exit()


class NetworkVisualization(TrackingVisualization):
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
                    distance = np.sqrt((((termite_a.trail['x']-termite_b.trail['x'])**2) +
                               ((termite_a.trail['y']-termite_b.trail['y'])**2)))
                    termite_a.trail['distance_to_t{}'.format(b_number)] = distance
                    termite_a.trail['interaction_with_t{}'.format(b_number)] = 'no-interaction'

    def show(self):
        '''Start tracking session visualization.

        Args:
            None.
        Returns:
            None.
        '''
        self._compute_distances()
        for frame_number in range(1, len(self.termites[0].trail['frame'])):
            playing, self.frame = self.video.read()
            self._draw_frame_info()
            self.frame = cv2.resize(self.frame, (0,0), fx=self.settings['resize_ratio'],
                               fy=self.settings['resize_ratio'])

            for n_termite in range(len(self.termites)):
                predicted = (int(self.termites[n_termite].trail.loc[frame_number, 'x']), int(self.termites[n_termite].trail.loc[frame_number, 'y']))
                cv2.circle(self.frame, predicted, 3, self.termites[n_termite].color, -1)
                cv2.putText(self.frame, self.termites[n_termite].trail.loc[frame_number,'label'], (predicted[0]+5, predicted[1]+5), 2,
                            color=self.termites[n_termite].color, fontScale=0.3)
                for other in range(n_termite+1, len(self.termites)):
                    other_predicted = (int(self.termites[other].trail.loc[frame_number, 'x']), int(self.termites[other].trail.loc[frame_number, 'y']))
                    if self.termites[n_termite].trail.loc[frame_number, 'distance_to_{}'.format(self.termites[other].trail.loc[0, 'label'])] < 65:
                        cv2.line(self.frame, predicted, other_predicted, (0,0,255), 1)
                        half = ((predicted[0]+other_predicted[0])//2, (predicted[1]+other_predicted[1])//2)
                        cv2.circle(self.frame, half, 3, (255, 0, 0), -1)

            self.out.write(self.frame)
            cv2.imshow('Labeling...', self.frame)
            pressed_key = cv2.waitKey(1) & 0xff
            if pressed_key == 27:
                sys.exit()


if __name__ == '__main__':
    vis = NetworkVisualization('settings/visualization.json')
    vis.show()
