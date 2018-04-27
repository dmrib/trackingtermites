import cv2
import json
import os
import numpy as np
import pandas as pd
import pims
from skvideo.io import FFmpegWriter
import sys

import termite as trmt


class TrackingVisualization():
    def __init__(self, settings_file_path):
        with open(settings_file_path) as settings_file:
            self.config = json.load(settings_file)

        self.coordinates = []
        self.nest = trmt.Experiment(self.config['source_folder'])
        self.nest.normalize()
        self.video = self.load_video()

    def load_video(self):
        output_path = f'{os.path.join(self.config["source_folder"], "Videos/")}'
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        if self.config['save_output']:
            self.output = FFmpegWriter(f'{output_path}tracking.mp4',
                                       outputdict={'-vcodec': 'libx264'})
        try:
            return pims.Video(self.config['video_path'])
        except FileNotFoundError:
            print('Video file not found.')
            sys.exit()

    def get_frame(self, frame_number):
        frame = self.video[frame_number]
        frame = cv2.resize(frame, (0,0), fx=self.config['resize_ratio'],
                           fy=self.config['resize_ratio'])
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.putText(frame, f'Frame #{self.step} of {len(self.video)}',
                    (5,10), 1, color=(0, 0, 255), fontScale=0.7)
        return frame

    def draw_termites(self, frame):
        for termite in self.nest.termites:
            position = (termite.trail.loc[self.step,'x'],
                        termite.trail.loc[self.step,'y'])
            cv2.circle(frame, position, 3, termite.color, -1)
            cv2.circle(frame, position, 8, termite.color, 2)
            cv2.putText(frame, termite.label, (position[0]-7, position[1]-11), 2,
                        color=termite.color, fontScale=0.4)

    def show(self):
        self.step = 0
        while self.step < len(self.video):
            frame = self.get_frame(self.step)
            for termite in self.nest.termites:
                self.draw_termites(frame)
            cv2.imshow(self.config['experiment_name'], frame)
            if self.config['save_output']:
                self.output.writeFrame(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            pressed_key = cv2.waitKey(self.config['movie_speed']) & 0xff
            if pressed_key == 27:
                self.output.close()
                sys.exit()
            self.step += 1
        cv2.destroyAllWindows()
        self.output.close()


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
            self.frame = cv2.resize(self.frame, (0,0), fx=self.settings['resize_ratio'],
                               fy=self.settings['resize_ratio'])
            self._draw_frame_info()

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
                self.output.release()
                sys.exit()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    vis = TrackingVisualization('settings/visualization.json')
    vis.show()
