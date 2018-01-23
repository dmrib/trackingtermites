from collections import namedtuple


class Termite:
    def __init__(self):
        self.trail = []
        self.tracker = None

    def to_file(self):
        with open('data/trail.csv', mode='w') as trail_out:
            for record in self.trail:
                trail_out.write(f'{record.frame},{record.time},{record.x},'
                                f'{record.y}\n')
