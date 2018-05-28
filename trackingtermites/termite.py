#!/usr/bin/env python

import glob
import numpy as np
import os
import pandas as pd
import random
import tqdm

import termite as trmt

random.seed(42)

def delta(column):
    return (column.shift(1) - column) ** 2


class Termite:
    def __init__(self, caste, number):
        self.caste = caste
        self.number = number
        self.color = (random.randint(1,256), random.randint(1,256),
                      random.randint(1,256))
        self.trail = []
        self.tracker = None

    def __repr__(self):
        return f'{self.label}'

    @property
    def label(self):
        return f'{self.caste}{self.number}'

    def to_dataframe(self):
        self.trail = pd.DataFrame(self.trail)
        self.trail = self.trail.set_index('frame')

    def to_csv(self, output_path):
        self.trail.to_csv(f'{output_path}/{self.label}-trail.csv',
                          float_format='%.1f', na_rep='NaN')

    def from_csv(self, source_path):
        self.trail = pd.read_csv(source_path, index_col=0)

    def normalize(self):
        self.trail['x'] = self.trail['x'] + self.trail['xoffset']//2
        self.trail['y'] = self.trail['y'] + self.trail['yoffset']//2


class Experiment():
    def __init__(self, source_folder):
        self.termites = []
        self.load_termites(source_folder)

    def load_termites(self, source_folder):
        data_files = glob.glob(f'{source_folder}*.csv')
        for data_file in data_files:
            label = os.path.basename(data_file).split('-')[0]
            termite = trmt.Termite(caste=label[0], number=int(label[1:]))
            termite.from_csv(data_file)
            self.termites.append(termite)

    def normalize(self):
        for termite in self.termites:
            termite.normalize()
            termite.trail = termite.trail.drop(columns=['xoffset', 'yoffset'])

    def compute_displacements(self):
        for termite in self.termites:
            deltas = termite.trail[['x', 'y']].apply(delta)
            displacement = np.sqrt(deltas['x'] + deltas['y'])
            termite.trail['displacement'] = displacement

    def compute_mean_velocities(self, movie_fps):
        for termite in self.termites:
            termite.trail['mean_velocity'] = termite.trail.groupby('time')['displacement'].transform(sum)/movie_fps

    def compute_nestmates_distances(self):
        for termite in self.termites:
            for other in self.termites:
                if termite != other:
                    distance = np.sqrt((((termite.trail['x']-other.trail['x'])**2) +
                                        ((termite.trail['y']-other.trail['y'])**2)))
                    termite.trail[f'distance_to_{other.label}'] = distance

    def compute_encounters(self, threshold):
        for termite in self.termites:
            for other in self.termites:
                if termite != other:
                    encounters = termite.trail[f'distance_to_{other.label}'] < threshold
                    termite.trail[f'encountering_{other.label}'] = encounters

    def save(self, output_path):
        output_path = os.path.join(output_path, 'Expanded')
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for termite in self.termites:
            termite.to_csv(output_path)


if __name__ == '__main__':
    base_folder = '/media/dmrib/tdata/Syntermes/'
    for experiment in tqdm.tqdm(os.listdir(base_folder), desc='Processing nests'):
        for i in range(1,4):
            file_path = f'{os.path.join(base_folder, experiment)}/{experiment}-{i}/'
            nest = Experiment(file_path)
            nest.normalize()
            nest.compute_displacements()
            nest.compute_mean_velocities(movie_fps=25)
            nest.compute_nestmates_distances()
            nest.compute_encounters(100)
            nest.save(file_path)
