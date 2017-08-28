"""This module contains the data input and output functionalities."""

import datetime
import os


def load_input(input_path):
    """Read input file and creates parameters dictionary.

    Args:
        input_path (str): path of input file.
    Returns:
        parameters (dict): experiment parameters.
    """
    parameters = {}
    with open(input_path, mode='r', encoding='utf-8') as input_file:
        for line in input_file:
            if not line[0] == '\n' and not line[0] == '#' and not line[0] == ' ':
                param, value = line.rstrip('\n').split(' ')
                parameters[param] = value

    if 'video_source_size' in parameters:
        y, x = parameters['video_source_size'].rstrip('\n').split(',')
        parameters['video_source_size'] = tuple([int(y), int(x)])

    integer_parameters = ['n_termites', 'box_size', 'scale']
    for parameter in integer_parameters:
        parameters[parameter] = int(parameters[parameter])


    boolean_parameters = ['show_labels', 'highlight_collisions',
                          'show_bounding_box', 'show_frame_info',
                          'show_d_lines']
    for parameter in boolean_parameters:
        if parameters[parameter].lower() == 'true':
            parameters[parameter] = True
        else:
            parameters[parameter] = False

    return parameters

def write_output(output_path, params, termites):
    """Write output data to file.

    Args:
        output_path (str): path for output file.
        params (dict): experiment parameters.
        termites (list): experiment termites.
    Returns:
        None.
    """
    header = create_header(params)

    output_path = output_path + params['exp_name']
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for termite in termites:
        termite_output = output_path + f'/termite-{termite.identity}.dat'
        with open(termite_output, mode='w', encoding='utf-8') as out_file:
            out_file.write(header)
            out_file.write(f'# Termite number: {termite.identity}\n')
            out_file.write(f'# Color: {termite.color}\n\n')
            out_file.write('###\n\n')
            out_file.write('frame, y, x, colliding, distances\n')
            for frame, location in enumerate(termite.path):
                out_file.write(f'{frame}, {location[0]}, {location[1]}, {location[2]}, {location[3]}\n')

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

def create_header(params):
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
