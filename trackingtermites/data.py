"""This module contains the data input and output functionalities."""


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

    if 'filters' in parameters:
        filters = []
        for filtr in parameters['filters'].rstrip('\n').split(','):
            filters.append(filtr)
        parameters['filters'] = filters

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
