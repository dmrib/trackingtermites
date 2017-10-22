"""Utilitary shared functions."""

boolean_parameters = ['show_labels', 'highlight_collisions',
                      'show_bounding_box', 'show_frame_info',
                      'show_d_lines', 'show_trails', 'draw_petri']

tuple_parameters = ['video_source_size', 'arena_size']

integer_parameters = ['n_termites', 'box_size', 'scale', 'trail_size', 'termite_radius',
                      'r_step_size', 'simulation_speed']

list_parameters = ['filters']

def read_config_file(config_path):
    """Read input file and creates parameters dictionary.

    Args:
        config_path (str): path to configuration file.
    Returns:
        parameters (dict): loaded parameters.
    """
    parameters = {}
    with open(config_path, mode='r', encoding='utf-8') as input_file:
        for line in input_file:
            if not line[0] == '\n' and not line[0] == '#' and not line[0] == ' ':
                param, value = line.strip().split(' ')
                if param in tuple_parameters:
                    width, height = value.strip().split(',')
                    parameters[param] = tuple([int(width), int(height)])
                elif param in list_parameters:
                    values = []
                    for field in value.strip().split(','):
                        if field != 'None':
                            values.append(field)
                    parameters[param] = values
                elif param in integer_parameters:
                    parameters[param] = int(value)
                elif param in boolean_parameters:
                    if value.lower() == 'true':
                        parameters[param] = True
                    else:
                        parameters[param] = False
                else:
                    parameters[param] = value

    return parameters
