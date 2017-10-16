"""Termite movement simulation."""


import cv2
import glob
import numpy as np
import sys

import termites as trmt
import utils
import video


class Simulation:
    '''Abstraction for termite movement simulation experiment.'''
    def __init__(self, config_path):
        self.termites = []
        self.params = utils.read_config_file(config_path)
        self.simulation_speed = self.params['simulation_speed']

    def run(self):
        '''Start simulation.

        Args:
            None.
        Returns:
            None.
        '''
        self.load_termites(self.params['source_files_path'])
        self.simulate()

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

    def simulate(self):
        '''Displays termite trail recorded points at a black arena.

        Args:
            None.
        Returns:
            None.
        '''
        video_source = video.VideoPlayer(self.params['original_source'], self.params['out_path'], self.params['arena_size'], [], True, 'MOG', 100)
        simulation_length = max(len(x.trail) for x in self.termites)
        current_step = 0
        while current_step < simulation_length:
            video_source.next_frame()
            background = np.zeros((self.params['arena_size'][1], self.params['arena_size'][0], 3), np.uint8)
            for termite in self.termites:
                cv2.circle(background, termite.trail[current_step], self.params['termite_radius'], termite.color, 1)
                cv2.putText(background, termite.number, (termite.trail[current_step][0]-4, termite.trail[current_step][1]-self.params['termite_radius']-5), 2, color=termite.color,
                            fontScale=0.4)
                for step in termite.trail[max(0, current_step-self.params['trail_size']):current_step]:
                    cv2.circle(background, step, 1, termite.color, -1)

            background = cv2.resize(background, self.params['arena_size'])
            cv2.imshow('Movement Simulation', np.hstack((video_source.current_frame, background)))
            pressed_key = cv2.waitKey(self.params['simulation_speed']) & 0xff
            if pressed_key == ord('p'):
                cv2.waitKey(0)
            current_step += 1

        cv2.destroyAllWindows()

if __name__ == '__main__':
    sim = Simulation('../config/simulation.conf')
    sim.run()
