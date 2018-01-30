from collections import namedtuple


class Termite:
    def __init__(self, label, color):
        '''Initializer.

        Args:
            label (str): termite identification label.
            color (tuple): BGR termite color code.
        Returns:
            None.
        '''
        self.label = label
        self.color = color
        self.trail = []
        self.tracker = None

    def to_csv(self, output_path):
        '''Write termite data to csv file.

        Args:
            output_path (str): destination path to output file.
        Returns:
            None.
        '''
        with open('{}/{}-trail.csv'.format(output_path, self.label), mode='w') as trail_out:
            trail_out.write('label,frame,time,x,y,xoffset,yoffset\n')
            for record in self.trail:
                trail_out.write('{},{},{},{},{},{},{}\n'.format('t'+self.label,
                                record['frame'], record['time'], record['x'],
                                record['y'], record['xoffset'],
                                record['yoffset']))
