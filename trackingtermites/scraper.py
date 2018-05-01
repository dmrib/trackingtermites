import cv2
import glob
import json
import numpy as np
import os
import pandas as pd
import pims
import skimage
import sys
import tqdm

import termite as trmt


class Scraper():
    def __init__(self, settings_path):
        with open(settings_path) as settings_file:
            self.config = json.load(settings_file)
        if not os.path.exists(self.config['output_path']):
            os.makedirs(self.config['output_path'])
        self.nest = trmt.Experiment(self.config['source_folder'])
        self.video = self.load_video()

    def load_video(self):
        try:
            return pims.Video(self.config['video_path'])
        except FileNotFoundError:
            print('Video file not found.')
            sys.exit()

    def get_frame(self, frame_number):
        frame = self.video[frame_number]
        frame = cv2.resize(frame, (0,0), fx=self.config['resize_ratio'],
                           fy=self.config['resize_ratio'])
        return frame

    def mark_termites(self, frame, termite_pos, other_pos):
        cv2.circle(frame, termite_pos, 5, (255, 0, 0), -1)
        cv2.circle(frame, other_pos, 5, (255, 0, 0), -1)

    def scrape(self):
        for self.step in tqdm.tqdm(range(0,len(self.video),30)):
            for current in range(len(self.nest.termites)):
                for other in range(current+1, len(self.nest.termites)):
                        frame = self.get_frame(self.step)
                        try:
                            if self.nest.termites[current].trail.loc[self.step, f'encountering_{self.nest.termites[other].label}']:
                                termite_pos = (self.nest.termites[current].trail.loc[self.step, 'x'],
                                               self.nest.termites[current].trail.loc[self.step, 'y'])
                                other_pos = (self.nest.termites[other].trail.loc[self.step, 'x'],
                                             self.nest.termites[other].trail.loc[self.step, 'y'])
                                self.mark_termites(frame, termite_pos, other_pos)
                                half = ((termite_pos[0]+other_pos[0])//2,
                                        (termite_pos[1]+other_pos[1])//2)
                                event = frame[(half[1]-self.config['termite_size']):(half[1]+self.config['termite_size']),
                                              (half[0]-self.config['termite_size']):(half[0]+self.config['termite_size'])]
                                path = os.path.join(self.config['output_path'], f'{self.nest.termites[current].label}-{self.nest.termites[other].label}-{self.step}.jpg')
                                skimage.io.imsave(path, event)
                        except Exception:
                            print(f'No entry for {self.nest.termites[current].label} in frame {self.step}.')
                            pass

if __name__ == '__main__':
    scraper = Scraper('settings/scraper.json')
    scraper.scrape()
