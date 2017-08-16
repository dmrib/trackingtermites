"""This module contains the data input and output functionalities."""

import datetime
import os


class DataHandler:
    """Input and output data handler class."""
    def __init__(self, input_path, output_path):
        """Initializer.

        Args:
            input_path (str): path of input file.
            output_path (str): path for output file.
        Returns:
            None.
        """
        self.input_path = input_path
        self.output_path = output_path

    def load_input(self):
        """Read input file and creates parameters dictionary.

        Args:
            None.
        Returns:
            parameters (dict): experiment parameters.
        """
        parameters = {}
        with open(self.input_path, mode='r', encoding='utf-8') as input_file:
            for line in input_file:
                if not line[0] == '\n' and not line[0] == '#' and not line[0] == ' ':
                    param, value = line.rstrip('\n').split(' ')
                    parameters[param] = value

        if 'n_termites' in parameters:
            parameters['n_termites'] = int(parameters['n_termites'])

        if 'box_size' in parameters:
            parameters['box_size'] = int(parameters['box_size'])

        if 'video_source_size' in parameters:
            y, x = parameters['video_source_size'].rstrip('\n').split(',')
            parameters['video_source_size'] = tuple([int(y), int(x)])

        return parameters

    def write_output(self, params, termites):
        """Write output data to file.

        Args:
            params (dict): experiment parameters.
            termites (list): experiment termites.
        Returns:
            None.
        """
        output_path = '../data/' + params['exp_name']
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        for termite in termites:
            termite_output = output_path + f'/termite-{termite.identity}.dat'
            with open(termite_output, mode='w', encoding='utf-8') as out_file:
                out_file.write(self.create_header(params))
                out_file.write(f'# Termite number: {termite.identity}\n')
                out_file.write(f'# Color: {termite.color}\n\n')
                out_file.write('###\n\n')
                out_file.write('frame, y, x, colliding\n')
                for frame, location in enumerate(termite.path):
                    out_file.write(f'{frame}, {location[0]}, {location[1]}, {location[2]}\n')

    def create_header(self, params):
        """Creates string summaring an experiment.

        Args:
            params (dict): experiment params.
        Returns:
            header (str): experiment header.
        """
        header = ''
        header += '# Date: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n'
        header += '# Movie name: ' + params['video_source'].split('/')[-1] + '\n'

        return header


if __name__ == '__main__':
    handler = DataHandler('../data/sample_input.txt', '')
    handler.load_input()
