import pandas as pd
import random


class Termite:
    def __init__(self, label):
        '''Initializer.

        Args:
            label (str): termite identification label.
            color (tuple): BGR termite color code.
        Returns:
            None.
        '''
        self.label = label
        self.color = (random.randint(1,256), random.randint(1,256),
                      random.randint(1,256))
        self.trail = []
        self.tracker = None

    def to_csv(self, output_path):
        '''Write termite tracker output data to csv file.

        Args:
            output_path (str): destination path to output file.
        Returns:
            None.
        '''
        with open('{}/{}-trail.csv'.format(output_path, self.label), mode='w') as trail_out:
            trail_out.write('label,frame,time,x,y,xoffset,yoffset\n')
            for record in self.trail:
                trail_out.write('{},{},{},{},{},{},{}\n'.format(self.label,
                                record['frame'], record['time'], record['x'],
                                record['y'], record['xoffset'],
                                record['yoffset']))

    def from_csv(self, source_path):
        '''Load termite data from csv file into pandas dataframe.

        Args:
            source_path (str): path to data source file.
        Returns:
            None.
        '''
        self.trail = pd.read_csv(source_path)
