import cv2
import datetime
import json
import os
import pandas as pd
import pims
import random
import sys
import time

import termite as trmt


class GeneralTracker:
    def __init__(self, config_path):
        with open(config_path) as config_file:
            self.config = json.load(config_file)
        self.video = self.load_video()
        self.current_frame = self.config['starting_frame'] + 1
        self.n_samples = self.config['n_termites']
        self.termites = []

        self.create_termites()

    def load_video(self):
        try:
            return pims.Video(self.config['video_path'])
        except FileNotFoundError:
            print('Video file not found.')
            sys.exit()

    def create_termites(self):
        frame = self.get_frame(self.config['starting_frame'])
        for t_number in range(1, self.n_samples + 1):
            if self.config['query_caste']:
                caste = input('Termite caste: ')
            else:
                caste = self.config['default_caste_label']
            termite = trmt.Termite(caste, t_number)
            initial_position = self.select_termite(frame)
            termite.tracker = cv2.Tracker_create(self.config['tracking_method'])
            termite.tracker.init(frame, initial_position)
            termite.trail.append({'frame': self.config['starting_frame'],
                                 'time': f'{time.strftime("%H:%M:%S", time.gmtime(self.current_frame/self.config["movie_fps"]))}',
                                 'label': termite.label,
                                 'caste': termite.caste,
                                 'x': initial_position[0],
                                 'y': initial_position[1],
                                 'xoffset': initial_position[2],
                                 'yoffset': initial_position[3]})
            self.termites.append(termite)

    def select_termite(self, frame):
        position = cv2.selectROI('Select the termite...', frame, False, False)
        position = tuple([int(x) for x in position])
        origin = (int(position[0]), int(position[1]))
        end = (int(position[0] + position[2]),
               int(position[1] + position[3]))
        cv2.rectangle(frame, origin, end, (0, 256, 0), 2)
        cv2.destroyAllWindows()
        return position

    def update_termites(self, frame):
        for termite in self.termites:
            found, position = termite.tracker.update(frame)
            position = [int(x) for x in position]
            if not found:
                print('Termite lost.')
            else:
                termite.trail.append({'frame': self.current_frame,
                                     'time': f'{time.strftime("%H:%M:%S", time.gmtime(self.current_frame/self.config["movie_fps"]))}',
                                     'label': termite.label,
                                     'caste': termite.caste,
                                     'x': position[0],
                                     'y': position[1],
                                     'xoffset': position[2],
                                     'yoffset': position[3]})

    def restart_tracker(self, frame):
        to_restart = int(input('Termite number: ')) - 1
        position = self.select_termite(frame)
        self.termites[to_restart].tracker = cv2.Tracker_create(self.config['tracking_method'])
        self.termites[to_restart].tracker.init(frame, position)
        self.termites[to_restart].trail[-1] = {'frame': self.current_frame,
                                               'time': f'{time.strftime("%H:%M:%S", time.gmtime(self.current_frame/self.config["movie_fps"]))}',
                                               'label': self.termites[to_restart].label,
                                               'caste': self.termites[to_restart].caste,
                                               'x': position[0],
                                               'y': position[1],
                                               'xoffset': position[2],
                                               'yoffset': position[3]}

    def rewind(self, n_steps):
        self.current_frame = max(self.config['starting_frame'], self.current_frame - n_steps - 1)
        frame = self.get_frame(self.current_frame)
        for termite in self.termites:
            termite.trail = termite.trail[:max(1, len(termite.trail) - n_steps - 1)]
            termite.tracker = cv2.Tracker_create(self.config['tracking_method'])
            termite.tracker.init(frame, (termite.trail[-1]['x'],
                                        termite.trail[-1]['y'],
                                        termite.trail[-1]['xoffset'],
                                        termite.trail[-1]['yoffset']))

    def draw_boxes(self, frame):
        for termite in self.termites:
            origin = (termite.trail[-1]['x'], termite.trail[-1]['y'])
            end = (termite.trail[-1]['x'] + termite.trail[-1]['xoffset'],
                   termite.trail[-1]['y'] + termite.trail[-1]['yoffset'])
            predicted = (termite.trail[-1]['x'] + termite.trail[-1]['xoffset']//2,
                         termite.trail[-1]['y'] + termite.trail[-1]['yoffset']//2)
            cv2.rectangle(frame, origin, end, termite.color, 2)
            cv2.circle(frame, predicted, 3, termite.color, -1)
            cv2.putText(frame, termite.label, (end[0]+5, end[1]+5), 2,
                        color=termite.color, fontScale=0.3)

    def print_summary(self):
        for termite in self.termites:
            print(f'{termite.label}, {len(termite.trail)} steps collected.')

    def write_output(self):
        output_path = os.path.join(self.config['output_path'],
                                   self.config['experiment_name'])
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        with open(os.path.join(output_path, 'meta.json'), mode='w') as metafile:
            json.dump(self.create_meta(), metafile, indent=4)
        for termite in self.termites:
            termite.to_csv(output_path)

    def create_meta(self):
        meta = {k: self.config[k] for k in ('experiment_name',
                     'conducted_by', 'tracking_method', 'n_termites',
                     'resize_ratio', 'video_path', 'movie_fps',
                     'starting_frame')}
        meta['movie_name'] = os.path.basename(self.config['video_path'])
        meta['date'] = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        return meta

    def get_frame(self, frame_number):
        frame = self.video[frame_number]
        frame = cv2.resize(frame, (0,0), fx=self.config['resize_ratio'],
                           fy=self.config['resize_ratio'])
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.putText(frame, f'Frame #{self.current_frame} of {len(self.video)} - {self.config["speed"]}ms delay.',
                    (5,10), 1, color=(0, 0, 255), fontScale=0.7)
        return frame

    def track(self):
        while self.current_frame < len(self.video):
            frame = self.get_frame(self.current_frame)
            self.update_termites(frame)
            self.draw_boxes(frame)

            cv2.imshow('Tracking...', frame)
            command = cv2.waitKey(self.config['speed'])
            if command == 27:
                cv2.destroyAllWindows()
                sys.exit()
            elif command == ord('w'):
                cv2.waitKey(0)
            elif command == ord('q'):
                self.restart_tracker(frame)
            elif command == ord('1'):
                self.rewind(self.config['rewind_steps'] // 2)
            elif command == ord('2'):
                self.rewind(self.config['rewind_steps'])
            elif command == ord('3'):
                self.rewind(self.config['rewind_steps'] * 2)
            elif command == ord('4'):
                self.rewind(self.config['rewind_steps'] * 5)
            elif command == ord('5'):
                self.rewind(self.config['rewind_steps'] * 10)
            elif command == ord('.'):
                self.config['speed'] = max(1, self.config['speed'] - 50)
            elif command == ord(','):
                self.config['speed'] += 50

            self.current_frame += 1
        self.write_output()
        self.print_summary()

tracker = GeneralTracker('settings/tracking.json')
tracker.track()
