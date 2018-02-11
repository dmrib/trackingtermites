import cv2
import json
import os
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

    def show(self):
        '''Start tracking session visualization.

        Args:
            None.
        Returns:
            None.
        '''
        for step in range(1, len(self.termites[0].trail)):
            self.playing, self.frame = self.video.read()
            if not self.playing:
                sys.exit()
            self.frame = cv2.resize(self.frame, (0,0), fx=self.settings['resize_ratio'],
                                    fy=self.settings['resize_ratio'])
            self._draw_frame_info()

            for termite in self.termites:
                position = (int(termite.trail.loc[step,'x']),
                            int(termite.trail.loc[step,'y']))
                cv2.circle(self.frame, position, 3, termite.color, -1)
                cv2.circle(self.frame, position, 8, termite.color, 2)
                cv2.putText(self.frame, 'w'+termite.label[-1], (position[0]-7, position[1]-11), 2, color=termite.color,
                            fontScale=0.4)

                f_trail = termite.trail.iloc[step:min(len(self.termites[0].trail), step+5)]
                for future in f_trail.itertuples():
                    cv2.circle(self.frame, (int(future.x), int(future.y)), 2,
                               termite.color, -1)

                p_trail = termite.trail.iloc[max(0, step-5):step]
                for past in p_trail.itertuples():
                    cv2.circle(self.frame, (int(past.x), int(past.y)), 2,
                               termite.color, -1)

            cv2.imshow(self.settings['experiment_name'], self.frame)
            self.out.write(self.frame)

            pressed_key = cv2.waitKey(self.settings['movie_speed']) & 0xff
            if pressed_key == 27:
                sys.exit()


if __name__ == '__main__':
    vis = TrackingVisualization('settings/visualization.json')
    vis.show()
