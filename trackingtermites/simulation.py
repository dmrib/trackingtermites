"""Termite movement simulation."""


import cv2
import glob
import numpy as np
import sys

import termites as trmt
import utils


class Simulation:
    '''Abstraction for termite movement simulation experiment.'''
    def __init__(self, config_path):
        self.termites = []
        self.params = utils.read_config_file(config_path)
        self.current_speed = 1

    def run(self):
        '''Start simulation.

        Args:
            None.
        Returns:
            None.
        '''
        self.load_termites(self.params['source_files_path'])
        self.simulate(self.params['original_source'])

    def load_termites(self, files_path):
        '''Load termite tracking experiment data.

        Args:
            files_path (str): path to input files.
        Returns:
            None.
        '''
        source_files = glob.glob(files_path + '*termite*')
        for source in source_files:
            self.termites.append(trmt.TermiteRecord(source))

    def simulate(self, original_source):
        '''Displays termite trail recorded points at a black arena.

        Args:
            original_source (str): original video path.
        Returns:
            None.
        '''
        original_video = cv2.VideoCapture(original_source)
        if not original_video.isOpened():
            print("Couldn't open the original video.")
            sys.exit()

        frame_number = 0
        playing, frame = original_video.read()
        while playing:
            frame = cv2.resize(frame, self.params['arena_size'])
            background = np.zeros((self.params['arena_size'][1], self.params['arena_size'][0], 3), np.uint8)
            for termite in self.termites:
                cv2.circle(background, termite.trail[frame_number], self.params['termite_radius'], termite.color, 3)
                cv2.putText(background, termite.number, termite.trail[frame_number], 2, color=termite.color,
                            fontScale=0.3)
                for step in termite.trail[max(0, frame_number-self.params['trail_size']):frame_number]:
                    cv2.circle(background, step, 1, termite.color, -1)

            background = cv2.resize(background, self.params['arena_size'])
            cv2.imshow('Movement Simulation', np.hstack((frame, background)))
            pressed_key = cv2.waitKey(1) & 0xff
            if pressed_key == ord('p'):
                cv2.waitKey(0)
            frame_number += 1
            playing, frame = original_video.read()

        cv2.destroyAllWindows()

if __name__ == '__main__':
    sim = Simulation('../config/simulation.conf')
    sim.run()
