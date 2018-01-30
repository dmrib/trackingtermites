import cv2
import datetime
import json
import os
import random
import sys
import termite as trmt
import time


class TermiteTracker:
    def __init__(self, settings_file_path):
        '''Initializer.

        Args:
            settings_file_path (str): path to tracking session settings file.
        Returns:
            None.
        '''
        self._load_settings(settings_file_path)
        self.termites = []
        self.video = None
        self.frame = None
        self.playing = False

    def _load_settings(self, settings_file_path):
        '''Load tracking session settings.

        Args:
            settings_file_path (str): path to tracking session settings file.
        Returns:
            None.
        '''
        with open(settings_file_path) as settings_file:
            self.settings = json.load(settings_file)

    def _load_video(self):
        '''Load experiment video.

        Args:
            None.
        Returns:
            None.
        '''
        self.video = cv2.VideoCapture(self.settings['video_path'])
        if not self.video.isOpened:
            print('Could not find the video file.')
            sys.exit()

        self.playing, self.frame = self.video.read()
        if not self.playing:
            print('Could not start video.')
            sys.exit()
        self.frame = cv2.resize(self.frame, (0,0), fx=self.settings['resize_ratio'],
                                fy=self.settings['resize_ratio'])

    def _read_next_frame(self):
        '''Read next frame from current video.

        Args:
            None.
        Returns:
            None.
        '''
        self.playing, self.frame = self.video.read()
        if not self.playing:
            return self.playing
        self.frame = cv2.resize(self.frame, (0,0), fx=self.settings['resize_ratio'],
                                fy=self.settings['resize_ratio'])
        return self.playing

    def _select_termites(self):
        '''Open UI tool for selecting termites on current frame, create termite
           representation and append to termites list.

        Args:
            None.
        Return:
            None.
        '''
        for i in range(1, self.settings['n_termites']+1):
            random_color = (random.randint(0, 255), random.randint(0, 255),
                            random.randint(0, 255))
            termite = trmt.Termite(str(i), random_color)
            termite.tracker = cv2.Tracker_create(self.settings['tracking_method'])
            termite_pos = cv2.selectROI('Select the termite...', self.frame,
                                        False, False)
            termite.trail.append({'frame': int(self.video.get(cv2.CAP_PROP_POS_FRAMES)),
                                 'time': time.strftime("%H:%M:%S",
                                 time.gmtime(int(self.video.get(cv2.CAP_PROP_POS_MSEC)/1000))),
                                 'x': termite_pos[0],
                                 'y': termite_pos[1],
                                 'xoffset': termite_pos[2],
                                 'yoffset': termite_pos[3]})

            termite.tracker.init(self.frame, termite_pos)
            cv2.destroyWindow('Select the termite...')
            self.termites.append(termite)

    def _update_positions(self):
        '''Compute termite position on frame using the tracker output and
           append to the termite's trail.

        Args:
            None.
        Returns:
            None.
        '''
        for termite in self.termites:
            found, termite_pos = termite.tracker.update(self.frame)
            if not found:
                print('Termite lost.')
            else:
                termite.trail.append({'frame': int(self.video.get(cv2.CAP_PROP_POS_FRAMES)),
                                     'time': time.strftime("%H:%M:%S",
                                     time.gmtime(int(self.video.get(cv2.CAP_PROP_POS_MSEC)/1000))),
                                     'x': termite_pos[0],
                                     'y': termite_pos[1],
                                     'xoffset': termite_pos[2],
                                     'yoffset': termite_pos[3]})

    def _draw_boxes(self):
        '''Draw box on current frame representing a termite current predicted
           region.

        Args:
            None.
        Returns:
            None.
        '''
        for termite in self.termites:
            origin = (int(termite.trail[-1]['x']), int(termite.trail[-1]['y']))
            end = (int(termite.trail[-1]['x'] + termite.trail[-1]['xoffset']),
                   int(termite.trail[-1]['y'] + termite.trail[-1]['yoffset']))
            cv2.rectangle(self.frame, origin, end, termite.color, 2)
            cv2.putText(self.frame, termite.label, (end[0]+5, end[1]+5), 2,
                        color=termite.color, fontScale=0.4)

    def _draw_frame_info(self):
        '''Write frame meta info on the current frame.

        Args:
            None.
        Returns:
            None.
        '''
        cv2.putText(self.frame, 'Frame #{}, of {} {}ms delay.'.format(
                    int(self.video.get(cv2.CAP_PROP_POS_FRAMES)),
                    int(self.video.get(cv2.CAP_PROP_FRAME_COUNT)),
                    self.settings['movie_speed']), (5,10), 1, color=(0, 0, 255),
                    fontScale=0.7)

    def _process_event(self, pressed_key):
        '''Process a key press triggered event on tracking loop.

        Args:
            None.
        Returns:
            None.
        '''
        if pressed_key == 27:
            return False
        elif pressed_key == ord('p'):
            cv2.waitKey(0)
        elif pressed_key == ord('.'):
            self.settings['movie_speed'] = max(1, self.settings['movie_speed'] - 10)
        elif pressed_key == ord(','):
            self.settings['movie_speed'] += 10
        elif pressed_key == ord('r'):
            self._correct_termite()
        elif pressed_key == ord('w'):
            self._rewind()
        return True

    def _correct_termite(self):
        '''Correct termite position and restart tracker.

        Args:
            None.
        Returns:
            None.
        '''
        to_correct = int(input('Termite number: '))
        new_position = cv2.selectROI('Select the termite...', self.frame,
                                     False, False)
        cv2.destroyWindow('Select the termite...')
        self.termites[to_correct-1].tracker = cv2.Tracker_create(
                                              self.settings['tracking_method'])
        self.termites[to_correct-1].tracker.init(self.frame, new_position)

    def _rewind(self):
        '''Rewind tracking experiment.

        Args:
            None.
        Returns:
            None.
        '''
        for termite in self.termites:
            termite.trail = termite.trail[:max(1, len(termite.trail) -
                            self.settings['rewind_steps'])]
            termite.tracker = cv2.Tracker_create('KCF')
            termite.tracker.init(self.frame, (termite.trail[-1]['x'],
                                 termite.trail[-1]['y'],
                                 termite.trail[-1]['xoffset'],
                                 termite.trail[-1]['yoffset']))
        self.video.set(cv2.CAP_PROP_POS_FRAMES,
                       max(1, self.video.get(cv2.CAP_PROP_POS_FRAMES) -
                              self.settings['rewind_steps']))

    def _write_output(self, output_path):
        '''Write termites' tracking output to csv file.

        Args:
            output_path (str): destination path to the csv file.
        Return:
            None.
        '''
        self._create_meta()

        output_path = os.path.join(self.settings['output_path'] +
                                   self.settings['experiment_name'])
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        with open(output_path+'/meta.json', mode='w') as output_file:
            json.dump(self.meta, output_file, indent=4)
        for termite in self.termites:
            termite.to_csv(output_path)

    def _create_meta(self):
        '''Create experiment description file.

        Args:
            None.
        Returns:
            None.
        '''
        self.meta = {k: self.settings[k] for k in ('experiment_name',
                     'conducted_by', 'tracking_method', 'n_termites',
                     'resize_ratio')}
        self.meta['movie_name'] = os.path.basename(self.settings['video_path'])
        self.meta['date'] = '{}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.meta['movie_fps'] = self.video.get(cv2.CAP_PROP_FPS)

    def track(self):
        '''Tracking loop.

        Args:
            None.
        Returns:
            None.
        '''
        self._load_video()
        self._select_termites()

        # Tracking loop
        while True:
            if not self._read_next_frame():
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
