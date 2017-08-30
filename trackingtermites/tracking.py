"""This module contains the termite tracking functionalities."""

import sys
import cv2

import data
import video
import termites as trmt


class GeneralTracker:
    """Tracking experiment abstraction."""
    def __init__(self, input_path):
        """Initializer.

        Args:
            input_path (str): path of input file.
        Returns:
            None.
        """
        self.termites = []
        self.params = data.load_input('../data/sample_input.txt')
        self.video_source = video.VideoPlayer(self.params['video_source'],
                            self.params['video_source_size'], self.params['filters'])

    def run(self):
        """Start experiment.

        Args:
            None.
        Returns:
            None.
        """
        self.locate_termites()
        self.track_all()

    def locate_termites(self):
        """Open GUI tool for selecting termite to be tracked.

        Args:
            None.
        Returns:
            None.
        """
        for t_number in range(self.params['n_termites']):
            roi = self.video_source.select_roi()
            starting_box = (roi[0], roi[1], self.params['box_size'], self.params['box_size'])

            termite = trmt.Termite(t_number+1, starting_box, starting_box[2])
            termite.tracker = cv2.Tracker_create(self.params['method'])
            termite.tracker.init(self.video_source.current_frame, starting_box)

            self.termites.append(termite)

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
            self.video_source.show_current_frame('Tracking')

            pressed_key = cv2.waitKey(1) & 0xff    # Continue if no key is being pressed
            if pressed_key == 27:
                data.write_output(self.params['output_path'], self.params, self.termites)
                break
            elif pressed_key == ord('r'):
                self.restart_trackers(full=True)
            elif pressed_key == ord('e'):
                self.restart_trackers()
            elif pressed_key == ord('p'):
                self.video_source.pause()

            self.video_source.next_frame()

        data.write_output(self.params['output_path'], self.params, self.termites)

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
                print(f'Lost termite no.{termite.identity}')
                self.video_source.pause()
            termite.detect_collisions(self.termites)
            termite.compute_distances(self.termites, self.params['scale'])
            termite.path.append([int(termite.position[0]), int(termite.position[1]), termite.colliding_with, termite.distances])

    def draw(self):
        """Draw bounding box in the tracked termites.

        Args:
            None.
        Returns:
            None.
        """
        for termite in self.termites:
            if self.params['show_labels']:
                self.video_source.draw_label(str(termite.identity), termite.color, (termite.end[0]+5, termite.end[1]+5))
            if termite.colliding_with and self.params['highlight_collisions']:
                    self.video_source.draw_b_box(termite.origin, termite.end, termite.color, strong=True)
            else:
                if self.params['show_bounding_box']:
                    self.video_source.draw_b_box(termite.origin, termite.end, termite.color)
            if self.params['show_d_lines']:
                for other_termite in self.termites:
                    if other_termite.identity != termite.identity:
                        self.video_source.draw_line(termite.origin, other_termite.end, termite.color)

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
        new_region = (recover_point[0], recover_point[1], self.params['box_size'], self.params['box_size'])
        termite.tracker = cv2.Tracker_create(self.params['method'])
        termite.tracker.init(self.video_source.current_frame, new_region)


if __name__ == '__main__':
    termite_tracker = GeneralTracker('../data/sample_input.txt')
    termite_tracker.run()
