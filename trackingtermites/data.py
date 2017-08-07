"""This module contains the data input and output functionalities."""


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

    def write_output(self):
        """Write output data to file.

        Args:
            None.
        Returns:
            None.
        """
        pass


if __name__ == '__main__':
    handler = DataHandler('../data/sample_input.txt', '')
    handler.load_input()
