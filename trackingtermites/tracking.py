from collections import namedtuple
import cv2
import json
import random
import sys
import termite as trmt
import time


Record = namedtuple('Record', ['frame', 'time', 'x', 'y', 'xoffset', 'yoffset'])


class TermiteTracker:
    def __init__(self, settings_file_path):
        self._load_settings(settings_file_path)
        self.termites = []
        self.video = None
        self.frame = None
        self.playing = False

    def _load_settings(self, settings_file_path):
        with open(settings_file_path) as settings_file:
            self.settings = json.load(settings_file)

    def _load_video(self):
        self.video = cv2.VideoCapture(self.settings['video_path'])
        if not self.video.isOpened:
            print('Could not find the video file.')
            sys.exit()

        self._read_next_frame()

    def _read_next_frame(self):
        self.playing, self.frame = self.video.read()
        self.frame = cv2.resize(self.frame, (0,0), fx=0.5, fy=0.5)
        if not self.playing:
            print('Could not start video.')
            sys.exit()
        return True

    def _select_termites(self):
        for i in range(1, self.settings['n_termites']+1):
            random_color = (random.randint(0, 255), random.randint(0, 255),
                            random.randint(0, 255))
            termite = trmt.Termite(str(i), random_color)
            termite.tracker = cv2.Tracker_create('KCF')
            termite_pos = cv2.selectROI('Select the termite...', self.frame,
                                        False, False)
            termite.trail.append(Record(int(self.video.get(cv2.CAP_PROP_POS_FRAMES)),
                                 time.strftime("%H:%M:%S",
                                 time.gmtime(int(self.video.get(cv2.CAP_PROP_POS_MSEC)/1000))),
                                 termite_pos[0], termite_pos[1], termite_pos[2],
                                 termite_pos[3]))

            termite.tracker.init(self.frame, termite_pos)
            cv2.destroyWindow('Select the termite...')
            self.termites.append(termite)

    def _update_positions(self):
        for termite in self.termites:
            found, termite_pos = termite.tracker.update(self.frame)
            if not found:
                print('Termite lost.')
            else:
                termite.trail.append(Record(int(self.video.get(cv2.CAP_PROP_POS_FRAMES)),
                                     time.strftime("%H:%M:%S",
                                     time.gmtime(int(self.video.get(cv2.CAP_PROP_POS_MSEC)/1000))),
                                     termite_pos[0], termite_pos[1],
                                     termite_pos[2], termite_pos[3]))

    def _draw_boxes(self):
        for termite in self.termites:
            origin = (int(termite.trail[-1].x), int(termite.trail[-1].y))
            end = (int(termite.trail[-1].x + termite.trail[-1].xoffset),
                   int(termite.trail[-1].y + termite.trail[-1].yoffset))
            cv2.rectangle(self.frame, origin, end, termite.color)
            cv2.putText(self.frame, termite.label, (end[0]+5, end[1]+5), 2,
                        color=termite.color, fontScale=0.3)

    def _draw_frame_info(self):
        cv2.putText(self.frame, 'Frame #{}, of {} {}ms delay.'.format(
                    int(self.video.get(cv2.CAP_PROP_POS_FRAMES)),
                    int(self.video.get(cv2.CAP_PROP_FRAME_COUNT)),
                    self.settings['movie_speed']), (5,10), 1, color=(0, 0, 255),
                    fontScale=0.7)

    def _process_event(self, pressed_key):
        if pressed_key == 27:
            return False
        elif pressed_key == ord('p'):
            cv2.waitKey(0)
        elif pressed_key == ord('.'):
            self.settings['movie_speed'] = max(1, self.settings['movie_speed'] - 10)
        elif pressed_key == ord(','):
            self.settings['movie_speed'] += 10
        elif pressed_key == ord('r'):
            correct = int(input('Termite number: '))
            new_position = cv2.selectROI('Select the termite...', self.frame,
                                         False, False)
            cv2.destroyWindow('Select the termite...')
            self.termites[correct-1].tracker = cv2.Tracker_create('KCF')
            self.termites[correct-1].tracker.init(self.frame, new_position)
        elif pressed_key == ord('w'):
            for termite in self.termites:
                termite.trail = termite.trail[:max(1, len(termite.trail)-15)]
                termite.tracker = cv2.Tracker_create('KCF')
                termite.tracker.init(self.frame, (termite.trail[-1].x,
                                     termite.trail[-1].y,
                                     termite.trail[-1].xoffset,
                                     termite.trail[-1].yoffset))
            self.video.set(cv2.CAP_PROP_POS_FRAMES,
                           max(1, self.video.get(cv2.CAP_PROP_POS_FRAMES) - 30))

        return True

    def _write_output(self, output_path):
        for termite in self.termites:
            termite.to_csv(output_path)

    def track(self):
        self._load_video()
        self._select_termites()

        # Tracking loop
        while True:
            go_on = self._read_next_frame()
            if not go_on:
                break
            self._update_positions()
            self._draw_boxes()
            self._draw_frame_info()

            # Show current frame
            cv2.imshow('Tracking...', self.frame)

            # Check and processs pressed keys events
            pressed_key = cv2.waitKey(self.settings['movie_speed']) & 0xff
            go_on = self._process_event(pressed_key)
            if not go_on:
                break

        self._write_output(self.settings['output_path'])


if __name__ == '__main__':
    tracker = TermiteTracker('settings.json')
    tracker.track()
