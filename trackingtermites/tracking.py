"""This module contains the termite tracking functionalities."""

import sys
import cv2

import data
import termites as trmt


class Experiment:
    """Tracking experiment abstraction."""
    def __init__(self, input_path, output_path):
        """Initializer.

        Args:
            input_path (str): path of input file.
            output_path (str): path for output file.
        Returns:
            None.

        """
        self.termites = []
        self.data_handler = data.DataHandler(input_path, output_path)
        self.params = self.data_handler.load_input()
        self.video_source = cv2.VideoCapture(self.params['video_source'])

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
        if not self.video_source.isOpened():
            print('Could not open video.')
            sys.exit()

        ok, frame = self.video_source.read()
        if not ok:
            print('Could not read video file.')
            sys.exit()
        frame = cv2.resize(frame, self.params['video_source_size'])

        for t_number in range(self.params['n_termites']):
            starting_point = cv2.selectROI(frame, False)
            starting_box = (starting_point[0], starting_point[1], self.params['box_size'], self.params['box_size'])
            termite = trmt.Termite(t_number+1, starting_point, self.params['box_size'])
            termite.tracker = cv2.Tracker_create(self.params['method'])
            termite.tracker.init(frame, starting_box)
            self.termites.append(termite)

        cv2.destroyWindow('ROI selector')

    def track_all(self):
        """Start tracking loop.

        Args:
            None.
        Returns:
            None.
        """
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        video_output = cv2.VideoWriter('../data/out-video.avi', fourcc, 30.0, (640,480))
        ok, frame = self.video_source.read()
        while ok:
            frame = cv2.resize(frame, self.params['video_source_size'])
            self.update_termites(frame)
            self.draw(frame)
            if self.params['save_output']:
                video_output.write(frame)
            cv2.imshow("Tracking", frame)

            k = cv2.waitKey(1) & 0xff
            if k == 27:
                self.data_handler.write_output(self.params, self.termites)
                break
            elif k == ord('r'):
                self.restart_trackers(frame)
            elif k == ord('e'):
                self.restart_tracker(frame)
            elif k == ord('p'):
                cv2.waitKey()

            ok, frame = self.video_source.read()

        self.data_handler.write_output(self.params, self.termites)

    def update_termites(self, frame):
        """Update termites positions.

        Args:
            frame (numpy.ndarray): next video frame.

        Returns:
            None.
        """
        for termite in self.termites:
            ok, termite.position = termite.tracker.update(frame)
            termite.detect_collisions(self.termites)
            termite.compute_distances(self.termites, self.params['scale'])
            termite.path.append([int(termite.position[0]), int(termite.position[1]), termite.colliding_with, termite.distances])

    def draw(self, frame):
        """Draw bounding box in the tracked termites.

        Args:
            frame (numpy.ndarray): next video frame.
        Returns:
            None.
        """
        for termite in self.termites:
            origin = (int(termite.position[0]), int(termite.position[1]))
            end = (int(termite.position[0] + termite.position[2]),
                  int(termite.position[1] + termite.position[3]))
            if self.params['show_labels']:
                cv2.putText(frame, str(termite.identity), (end[0]+5,end[1]+5), cv2.FONT_HERSHEY_SIMPLEX, color=termite.color, fontScale=0.3)
            if termite.colliding_with and self.params['highlight_collisions']:
                    cv2.rectangle(frame, origin, end, termite.color, 5)
            else:
                if self.params['show_bounding_box']:
                    cv2.rectangle(frame, origin, end, termite.color)
            if self.params['show_d_lines']:
                for other_termite in self.termites:
                    end = (int(other_termite.position[0]), int(other_termite.position[1]))
                    cv2.line(frame, origin, end, color=termite.color, thickness=1)
        if self.params['show_frame_info']:
            cv2.putText(frame, f'#{int(self.video_source.get(cv2.CAP_PROP_POS_FRAMES))} of'
                               f' {int(self.video_source.get(cv2.CAP_PROP_FRAME_COUNT))},'
                               f' {int(self.video_source.get(cv2.CAP_PROP_FPS))}fps.',
                       (10,10), cv2.FONT_HERSHEY_SIMPLEX, color=(255, 0, 0), fontScale=0.3)

    def restart_trackers(self, frame):
        """Restart the tracker instance of every termite in experiment.

        Args:
            frame (np.ndarray): video frame.
        Returns:
            None.
        """
        for termite in self.termites:
            recover_point = cv2.selectROI(frame, False)
            new_region = (recover_point[0], recover_point[1], self.params['box_size'], self.params['box_size'])
            termite.tracker = cv2.Tracker_create(self.params['method'])
            termite.tracker.init(frame, new_region)
        cv2.destroyWindow('ROI selector')

    def restart_tracker(self, frame):
        """Restart the tracker for a single individual.

        Args:
            frame (np.ndarray): video frame.
        Returns:
            None.
        """
        termite_number = int(input('Tell me the termite number: ')) - 1
        recover_point = cv2.selectROI(frame, False)
        new_region = (recover_point[0], recover_point[1], self.params['box_size'], self.params['box_size'])
        self.termites[termite_number].tracker = cv2.Tracker_create(self.params['method'])
        self.termites[termite_number].tracker.init(frame, new_region)
        cv2.destroyWindow('ROI selector')


if __name__ == '__main__':
    ex = Experiment('../data/sample_input.txt', '../data/')
    ex.run()
