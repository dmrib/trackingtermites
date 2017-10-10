"""Termite movement simulation."""


import cv2

import utils


class Simulation:
    '''Abstraction for termite movement simulation experiment.'''
    def __init__(self, config_path):
        self.termites = []
        self.params = utils.read_config_file(config_path)
        self.current_speed = 1


if __name__ == '__main__':
    sim = Simulation('../config/simulation.conf')
