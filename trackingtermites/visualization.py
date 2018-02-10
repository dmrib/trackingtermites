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
        for termite_number in range(1, self.settings['n_termites'] + 1):
            label = 't' + str(termite_number)
            file_name = '{}-trail.csv'.format(label)
            file_path = os.path.join(self.settings['source_folder'], file_name)
            termite = trmt.Termite(label)
            termite.from_csv(file_path)
            self.termites.append(termite)

    def show(self):
        for termite in self.termites:
            termite.trail['x'] = termite.trail['x'] + termite.trail['xoffset']/2
            termite.trail['y'] = termite.trail['y'] + termite.trail['yoffset']/2

        video = cv2.VideoCapture(self.settings['video_path'])
        shape = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)*self.settings['resize_ratio']),
                 int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)*self.settings['resize_ratio']))
        out = cv2.VideoWriter('{}/{}.avi'.format(self.settings['source_folder'],
                              self.settings['experiment_name']),
                              cv2.VideoWriter_fourcc(*'MJPG'), 30.0, shape)

        for step in range(1, len(self.termites[0].trail)):
            playing, frame = video.read()
            if not playing:
                sys.exit()
            frame = cv2.resize(frame, (0,0), fx=self.settings['resize_ratio'],
                                    fy=self.settings['resize_ratio'])

            for termite in self.termites:
                position = (int(termite.trail.loc[step,'x']),
                            int(termite.trail.loc[step,'y']))
                cv2.circle(frame, position, 3, termite.color, -1)
                cv2.circle(frame, position, 8, termite.color, 2)
                cv2.putText(frame, 'Frame #{} of {}, {}ms delay.'.format(
                            int(video.get(cv2.CAP_PROP_POS_FRAMES)),
                            len(self.termites[0].trail),
                            self.settings['movie_speed']), (5,10), 1, color=(0, 0, 255),
                            fontScale=0.7)

            cv2.imshow(self.settings['experiment_name'], frame)
            out.write(frame)

            pressed_key = cv2.waitKey(self.settings['movie_speed']) & 0xff
            if pressed_key == 27:
                sys.exit()


if __name__ == '__main__':
    vis = TrackingVisualization('settings/visualization.json')
    vis.show()
