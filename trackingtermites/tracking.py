#!/usr/bin/env python

"""This module contains the termite tracking functionalities."""

import cv2
import datetime, time
import os
import sys

import termites as trmt
import video


class GeneralTracker:
    """Termite tracker using OpenCV API."""
    def __init__(self, config_path):
        """Initializer.

        Args:
            config_path (str): path of tracker config file.
        Returns:
            None.
        """
        self.termites = []
        self.params = self.read_input(config_path)
        self.video_source = video.VideoPlayer(self.params['video_source'],
                                              self.params['output_path'],
                                              self.params['video_source_size'],
                                              self.params['filters'], True,
                                              self.params['subtractor'])

    def run(self):
        """Start trackers.

        Args:
            None.
        Returns:
            None.
        """
        self.locate_termites()
        self.track_all()

    def locate_termites(self):
        """Open GUI tool for termites area selection.

        Args:
            None.
        Returns:
            None.
        """
        for t_number in range(self.params['n_termites']):
            roi = self.video_source.select_roi()
            starting_box = (roi[0], roi[1], self.params['box_size'],
                            self.params['box_size'])

            termite = trmt.Termite(t_number+1, starting_box, starting_box[2])
            termite.tracker = cv2.Tracker_create(self.params['method'])
            termite.tracker.init(self.video_source.current_frame, starting_box)

            self.termites.append(termite)
        self.update_termites()

    def track_all(self):
        """Start tracking loop.

        Args:
            None.
        Returns:
            None.
        """
        self.video_source.next_frame()
        while self.video_source.playing:
            self.update_termites()
            self.draw()
            self.video_source.write_to_out_video()
            self.video_source.show_current_frame('Tracking')

            pressed_key = cv2.waitKey(1) & 0xff    # Continue if no key is
            if pressed_key == 27:                  # being pressed.
                break
            elif pressed_key == ord('r'):
                self.restart_trackers(full=True)
            elif pressed_key == ord('e'):
                self.restart_trackers()
            elif pressed_key == ord('p'):
                self.video_source.pause()

            self.video_source.next_frame()

        self.write_output()

    def update_termites(self):
        """Update termites positions.

        Args:
            None.
        Returns:
            None.
        """
        for termite in self.termites:
            found, termite.position = termite.tracker.update(self.video_source.current_frame)
            if not found:
                print('Lost termite no.{}'.format(termite.identity))
                self.video_source.pause()
            termite.detect_encounters(self.termites)
            termite.compute_distances(self.termites, self.params['scale'])
            termite.path.append([int(termite.position[0]), int(termite.position[1]),
                                termite.encountering_with, termite.distances,
                                self.video_source.source.get(cv2.CAP_PROP_POS_MSEC)])

    def draw(self):
        """Draw bounding box in the tracked termites.

        Args:
            None.
        Returns:
            None.
        """
        for termite in self.termites:
            if self.params['show_labels']:
                self.video_source.draw_label(str(termite.identity), termite.color,
                                             (termite.end[0]+5, termite.end[1]+5))
            if termite.encountering_with and self.params['highlight_collisions']:
                    self.video_source.draw_b_box(termite.origin, termite.end,
                                                 termite.color, strong=True)
            else:
                if self.params['show_bounding_box']:
                    self.video_source.draw_b_box(termite.origin, termite.end,
                                                 termite.color)
            if self.params['show_d_lines']:
                for other_termite in self.termites:
                    if other_termite.identity != termite.identity:
                        self.video_source.draw_line(termite.origin,
                                                    other_termite.end,
                                                    termite.color)

            if self.params['show_trails'] and self.params['trail_size'] != 0:
                for step in termite.path[-self.params['trail_size']:]:
                    self.video_source.draw_step((step[0], step[1]),
                                                termite.color)


    def restart_trackers(self, full=False):
        """Restart the tracker instance of termites in the experiment.

        Args:
            full (bool): should restart every tracker instance.
        Returns:
            None.
        """
        if full:
            for termite in self.termites:
                self.restart_tracker(termite)
        else:
            termite_number = int(input('Tell me the termite number: ')) - 1
            self.restart_tracker(self.termites[termite_number])

    def restart_tracker(self, termite):
        """Restart a tracker instance.

        Args:
            termite (trmt.Termite): Termite instance to have tracker restarted.
        Returns:
            None.
        """
        recover_point = self.video_source.select_roi()
        new_region = (recover_point[0], recover_point[1], self.params['box_size'],
                      self.params['box_size'])
        termite.tracker = cv2.Tracker_create(self.params['method'])
        termite.tracker.init(self.video_source.current_frame, new_region)

    def read_input(self, config_path):
        """Read input file and creates parameters dictionary.

        Args:
            config_path (str): path to configuration file.
        Returns:
            parameters (dict): trackers parameters.
        """
        parameters = {}
        with open(config_path, mode='r', encoding='utf-8') as input_file:
            for line in input_file:
                if not line[0] == '\n' and not line[0] == '#' and not line[0] == ' ':
                    param, value = line.strip().split(' ')
                    parameters[param] = value

        if 'video_source_size' in parameters:
            width, height = parameters['video_source_size'].strip().split(',')
            parameters['video_source_size'] = tuple([int(width), int(height)])

        if 'filters' in parameters:
            filters = []
            for filtr in parameters['filters'].strip().split(','):
                if filtr != 'None':
                    filters.append(filtr)
            parameters['filters'] = filters

        integer_parameters = ['n_termites', 'box_size', 'scale', 'trail_size']
        for parameter in integer_parameters:
            parameters[parameter] = int(parameters[parameter])


        boolean_parameters = ['show_labels', 'highlight_collisions',
                              'show_bounding_box', 'show_frame_info',
                              'show_d_lines', 'show_trails']
        for parameter in boolean_parameters:
            if parameters[parameter].lower() == 'true':
                parameters[parameter] = True
            else:
                parameters[parameter] = False

        return parameters

    def write_output(self):
        """Write trackers output data to file.

        Args:
            None.
        Returns:
            None.
        """
        header = self.create_header()

        output_path = self.params['output_path'] + self.params['exp_name']
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        summary_output = output_path + '/encounters_summary.dat'
        with open(summary_output, mode='w', encoding='utf-8') as summ_file:
            summ_file.write(self.create_encounters_summary())

        velocity_output = output_path + '/velocity_summary.dat'
        with open(velocity_output, mode='w', encoding='utf-8') as vel_output:
            vel_output.write(self.create_velocity_summary())

        for termite in self.termites:
            termite_output = output_path + '/termite-{}.dat'.format(termite.identity)
            with open(termite_output, mode='w', encoding='utf-8') as out_file:
                out_file.write(header)
                out_file.write(termite.generate_output())

    def create_header(self):
        """Creates header string of an experiment.

        Args:
            None.
        Returns:
            header (str): experiment header.
        """
        header = ''
        header += '# Date: {}\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        header += '# Movie name: {}\n'.format(self.params['video_source'].split('/')[-1])
        header += '# Movie shape: {}, {}\n'.format(self.params['video_source_size'][0], self.params['video_source_size'][1])
        header += '# Filters: {}\n'.format(self.params['filters'])
        header += '# Bounding box size: {}\n'.format(self.params['box_size'])

        return header

    def create_encounters_summary(self):
        """Creates summary description of an experiment encounters.

        Args:
            None.
        Returns:
            summary (str): experiment encounters summary.
        """
        header = self.create_header()
        summary = ''
        summary += '# Encounters summary\n'
        summary += header
        summary += '\n\n###\n\n'
        summary += 'frame, x, y, termite, encountering_with\n'
        for step in range(len(self.termites[0].path)):
            for termite in self.termites:
                if not termite.path[step][2]:
                    summary += '{}, {}, {}, {}, 0\n'.format(step+1,
                                                            termite.path[step][0],
                                                            termite.path[step][1],
                                                            termite.identity)
                else:
                    for encounter in termite.path[step][2]:
                        summary += '{}, {}, {}, {}, {}\n'.format(step+1,
                                                                 termite.path[step][0],
                                                                 termite.path[step][1],
                                                                 termite.identity,
                                                                 encounter)

        return summary

    def create_velocity_summary(self):
        """Creates summary of termite position in experiment by time.

        Args:
            None.
        Returns:
            summary (str): experiment positions by time summary.
        """
        header = self.create_header()
        summary = ''
        summary += '# Velocity summary\n'
        summary += header
        summary += '\n\n###\n\n'
        summary += 'termite, frame, time, x, y\n'
        for step in range(len(self.termites[0].path)):
            for termite in self.termites:
                summary += '{}, {}, {}, {}, {}\n'.format(termite.identity, step+1,
                                                     time.strftime("%H:%M:%S", time.gmtime(int(termite.path[step][4])/1000)),
                                                     termite.path[step][0],
                                                     termite.path[step][1])

        return summary

if __name__ == '__main__':
    termite_tracker = GeneralTracker('../config/tracking.conf')
    termite_tracker.run()
