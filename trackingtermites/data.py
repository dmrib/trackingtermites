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

        if 'show_labels' in parameters:
            if parameters['show_labels'].lower() == 'true':
                parameters['show_labels'] = True
            else:
                parameters['show_labels'] = False

        if 'highlight_collisions' in parameters:
            if parameters['highlight_collisions'].lower() == 'true':
                parameters['highlight_collisions'] = True
            else:
                parameters['highlight_collisions'] = False

        if 'show_bounding_box' in parameters:
            if parameters['show_bounding_box'].lower() == 'true':
                parameters['show_bounding_box'] = True
            else:
                parameters['show_bounding_box'] = False

        if 'save_output' in parameters:
            if parameters['save_output'].lower() == 'true':
                parameters['save_output'] = True
            else:
                parameters['save_output'] = False

        if 'show_frame_info' in parameters:
            if parameters['show_frame_info'].lower() == 'true':
                parameters['show_frame_info'] = True
            else:
                parameters['show_frame_info'] = False


        return parameters

    def write_output(self, params, termites):
        """Write output data to file.

        Args:
            params (dict): experiment parameters.
            termites (list): experiment termites.
        Returns:
            None.
        """
        header = self.create_header(params)

        output_path = '../data/' + params['exp_name']
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        for termite in termites:
            termite_output = output_path + f'/termite-{termite.identity}.dat'
            with open(termite_output, mode='w', encoding='utf-8') as out_file:
                out_file.write(header)
                out_file.write(f'# Termite number: {termite.identity}\n')
                out_file.write(f'# Color: {termite.color}\n\n')
                out_file.write('###\n\n')
                out_file.write('frame, y, x, colliding\n')
                for frame, location in enumerate(termite.path):
                    out_file.write(f'{frame}, {location[0]}, {location[1]}, {location[2]}\n')

        summary_output = output_path + '/experiment_summary.dat'
        with open(summary_output, mode='w', encoding='utf-8') as summ_file:
            summ_file.write('# Experiment summary\n')
            summ_file.write(header)
            summ_file.write('\n\n###\n\n')
            for step in range(len(termites[0].path)):
                for termite in termites:
                    if not termite.path[step][2]:
                        summ_file.write(f'{step}, {termite.path[step][0]}, {termite.path[step][1]}, {termite.identity}, 0\n')
                    else:
                        for collision in termite.path[step][2]:
                            summ_file.write(f'{step}, {termite.path[step][0]}, {termite.path[step][1]}, {termite.identity}, {collision}\n')

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
        header += '# Movie size: ' + str(params['video_source_size'][0]) + ', ' + str(params['video_source_size'][1]) + '\n'

        return header


if __name__ == '__main__':
    handler = DataHandler('../data/sample_input.txt', '')
    handler.load_input()
