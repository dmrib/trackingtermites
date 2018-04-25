import glob
import numpy as np
import os
import pandas as pd
import random

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
        return f'{self.label}, {len(self.trail)} steps collected.'

    @property
    def label(self):
        return f'{self.caste}{self.number}'

    def to_dataframe(self):
        self.trail = pd.DataFrame(self.trail)
        self.trail = self.trail.set_index('frame')

    def to_csv(self, output_path):
        self.to_dataframe()
        self.trail.to_csv(f'{output_path}/{self.label}-trail.csv',
                          float_format='%.1f', na_rep='NaN')

    def from_csv(self, source_path):
        self.trail = pd.read_csv(source_path)

    def normalize(self):
        self.trail['x'] = self.trail['x'] + self.trail['xoffset']//2
        self.trail['y'] = self.trail['y'] + self.trail['yoffset']//2


class Nest():
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

    def compute_distances(self):
        '''Compute distances between each termite.

        Args:
            None.
        Returns:
            None.
        '''
        for a_number, termite_a in enumerate(self.termites, start=1):
            print('Computing distances of termite {} of {}.'.format(a_number, len(self.termites)))
            for b_number, termite_b in enumerate(self.termites, start=1):
                if a_number != b_number:
                    distance = np.sqrt((((termite_a.trail['x']-termite_b.trail['x'])**2) +
                               ((termite_a.trail['y']-termite_b.trail['y'])**2)))
                    termite_a.trail['distance_to_t{}'.format(b_number)] = distance
                    termite_a.trail['interaction_with_t{}'.format(b_number)] = 'no-interaction'

    def compute_encounters(self, thresold):
        '''Check and point encounters between termites.

        Args:
            thresold (float): distance in pixel units for reporting encounters.
        Returns:
            None.
        '''
        number_of_frames = len(self.termites[0].trail['frame'])
        for frame_number in range(1, number_of_frames):
            print('Computing encounters on frame {} of {}.'.format(frame_number, number_of_frames-1))
            for n_termite in range(len(self.termites)):
                predicted = (int(self.termites[n_termite].trail.loc[frame_number, 'x']), int(self.termites[n_termite].trail.loc[frame_number, 'y']))
                for other in range(n_termite+1, len(self.termites)):
                    other_predicted = (int(self.termites[other].trail.loc[frame_number, 'x']), int(self.termites[other].trail.loc[frame_number, 'y']))
                    if self.termites[n_termite].trail.loc[frame_number, 'distance_to_{}'.format(self.termites[other].trail.loc[0, 'label'])] < thresold:
                        self.termites[n_termite].trail.loc[frame_number, 'interaction_with_{}'.format(self.termites[other].trail.loc[0, 'label'])] = 'encountering'
                        self.termites[other].trail.loc[frame_number, 'interaction_with_{}'.format(self.termites[n_termite].trail.loc[0, 'label'])] = 'encountering'

    def save(self, output_path):
        output_path = os.path.join(output_path, 'Expanded')
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for termite in self.termites:
            termite.to_csv(output_path)


if __name__ == '__main__':
    base_folder = '/media/dmrib/tdata/Syntermes/'
    for experiment in os.listdir(base_folder):
        for i in range(1,4):
            file_path = f'{os.path.join(base_folder, experiment)}/{experiment}-{i}/'
            nest = Nest(file_path)
            nest.normalize()
            nest.compute_displacements()
            nest.compute_mean_velocities(movie_fps=25)
            nest.save(file_path)
