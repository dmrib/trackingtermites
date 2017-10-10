"""Termite movement simulation."""


import cv2
import glob
import numpy as np

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
        for step in range(len(self.termites[0].trail)):
            background = np.zeros((self.params['arena_size'][1], self.params['arena_size'][0], 3), np.uint8)
            for termite in self.termites:
                cv2.circle(background, termite.trail[step], self.params['termite_radius'], termite.color, -1)
            cv2.imshow('Arena', background)
            cv2.waitKey(1)

        cv2.destroyAllWindows()

if __name__ == '__main__':
    sim = Simulation('../config/simulation.conf')
    sim.run()
