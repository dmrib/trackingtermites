import pandas as pd
import random

random.seed(42)

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
        self.trail.to_csv(output_path, index=False, float_format='%.1f')

    def from_csv(self, source_path):
        '''Load termite data from csv file into pandas dataframe.

        Args:
            source_path (str): path to data source file.
        Returns:
            None.
        '''
        self.trail = pd.read_csv(source_path)
