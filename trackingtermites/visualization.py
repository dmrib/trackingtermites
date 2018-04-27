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
        self.video = self.load_video()

    def load_video(self):
        output_path = f'{os.path.join(self.config["output_path"], "Videos/")}'
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
    def show(self):
        self.step = 0
        while self.step < len(self.video):
            frame = self.get_frame(self.step)
            for termite in self.nest.termites:
                self.draw_termites(frame)
                self.draw_connections(frame)
            cv2.imshow(self.config['experiment_name'], frame)
            self.output.writeFrame(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            pressed_key = cv2.waitKey(self.config['movie_speed']) & 0xff
            if pressed_key == 27:
                self.output.close()
                sys.exit()
            self.step += 1
        cv2.destroyAllWindows()
        self.output.close()

    def draw_connections(self, frame):
        for termite in self.nest.termites:
            for other in self.nest.termites:
                if termite != other:
                    if termite.trail.loc[self.step, f'encountering_{other.label}']:
                        cv2.line(frame, (termite.trail.loc[self.step, 'x'], termite.trail.loc[self.step, 'y']),
                                (other.trail.loc[self.step, 'x'], other.trail.loc[self.step, 'y']),
                                (55,31,122), 3)


if __name__ == '__main__':
    vis = NetworkVisualization('settings/visualization.json')
    vis.show()
