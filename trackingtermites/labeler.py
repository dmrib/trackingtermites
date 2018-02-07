import cv2
import json
import numpy as np
import os
import pandas as pd
import sys
import termite as trmt


class LabelingSession():
    def __init__(self, source_folder_path):
        '''Initializer.

        Args:
            source_folder_path (str): path to folder containing tracking data.
        Returns:
            None.
        '''
        self.termites = []

        self.source_folder_path = source_folder_path
        self._load_metadata()
        self._load_termites()

        self.output_path = os.path.join(self.source_folder_path, 'Labeled')

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
            os.makedirs(os.path.join(self.output_path, 'head-head'))
            os.makedirs(os.path.join(self.output_path, 'head-abdomen'))
            os.makedirs(os.path.join(self.output_path, 'no-interaction'))

        self.video = cv2.VideoCapture(self.metadata['video_path'])

    def _load_metadata(self):
        '''Load tracking metadata file.

        Args:
            None.
        Returns:
            None.
        '''
        with open(os.path.join(self.source_folder_path, 'meta.json')) as metadata:
            self.metadata = json.load(metadata)

    def _load_termites(self):
        '''Load termite data.

        Args:
            None.
        Returns:
            None.
        '''
        for termite_number in range(1, self.metadata['n_termites'] + 1):
            label = 't' + str(termite_number)
            file_name = '{}-trail.csv'.format(label)
            file_path = os.path.join(self.source_folder_path, file_name)
            termite = trmt.PandasTermite(label)
            termite.from_csv(file_path)
            self.termites.append(termite)

    def _compute_distances(self):
        '''Compute distances between termites on every experiment frame and
           updates dataframes.

        Args:
            None.
        Returns:
            None.
        '''
        for termite in self.termites:
            termite.trail['x'] = termite.trail['x'] + termite.trail['xoffset']/2
            termite.trail['y'] = termite.trail['y'] + termite.trail['yoffset']/2

        for a_number, termite_a in enumerate(self.termites, start=1):
            for b_number, termite_b in enumerate(self.termites, start=1):
                if a_number != b_number:
                    distance = np.sqrt((((termite_a.trail['x']-termite_b.trail['x'])**2) +
                               ((termite_a.trail['y']-termite_b.trail['y'])**2)))
                    termite_a.trail['distance_to_t{}'.format(b_number)] = distance
                    termite_a.trail['interaction_with_t{}'.format(b_number)] = 'no-interaction'

    def _save_termite_data(self):
        for termite in self.termites:
            destination_path = os.path.join(self.source_folder_path, 'Labeled')
            termite.to_csv(destination_path+'/{}.csv'.format(termite.trail.loc[0, "label"]))
        sys.exit()

    def start_session(self):
        '''Starts labeling session.

        Args:
            None.
        Returns:
            None.
        '''
        self._compute_distances()

        for frame_number in range(1, len(self.termites[0].trail['frame'])):
            playing, frame = self.video.read()
            frame = cv2.resize(frame, (0,0), fx=self.metadata['resize_ratio'],
                               fy=self.metadata['resize_ratio'])
            clear = frame.copy()

            for n_termite in range(len(self.termites)):
                predicted = (int(self.termites[n_termite].trail.loc[frame_number, 'x']), int(self.termites[n_termite].trail.loc[frame_number, 'y']))
                cv2.circle(frame, predicted, 3, self.termites[n_termite].color, -1)
                cv2.putText(frame, self.termites[n_termite].trail.loc[frame_number,'label'], (predicted[0]+5, predicted[1]+5), 2,
                            color=self.termites[n_termite].color, fontScale=0.3)

            for n_termite in range(len(self.termites)):
                predicted = (int(self.termites[n_termite].trail.loc[frame_number, 'x']), int(self.termites[n_termite].trail.loc[frame_number, 'y']))
                for other in range(n_termite+1, len(self.termites)):
                    other_predicted = (int(self.termites[other].trail.loc[frame_number, 'x']), int(self.termites[other].trail.loc[frame_number, 'y']))
                    if self.termites[n_termite].trail.loc[frame_number, 'distance_to_{}'.format(self.termites[other].trail.loc[0, 'label'])] < 70:
                        cv2.line(frame, predicted, other_predicted, (0,0,255), 1)
                        half = ((predicted[0]+other_predicted[0])//2, (predicted[1]+other_predicted[1])//2)
                        cv2.circle(frame, half, 3, (255, 0, 0), -1)

                        event = clear[(half[1]-25):(half[1]+25), (half[0]-25):(half[0]+25)]
                        edges = cv2.Canny(event,40,40)
                        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                        evaluation = np.hstack((event, edges))
                        evaluation = cv2.resize(evaluation, (0,0), fx=5,
                                                fy=5)

                        cv2.imshow('Labeling...', frame)
                        cv2.imshow('Encounter', evaluation)
                        encouter_label = cv2.waitKey(0) & 0xff
                        if encouter_label == 27:
                            cv2.destroyAllWindows()
                            self._save_termite_data()
                        elif encouter_label == ord('q'):
                            cv2.imwrite(os.path.join(self.output_path, 'head-head/{}-{}-head-head.jpg'.format(self.termites[n_termite].trail.loc[0, 'label'],
                                                                        frame_number)), event)
                            self.termites[n_termite].trail.loc[frame_number, 'interaction_with_{}'.format(self.termites[other].trail.loc[0, 'label'])] = 'head-head'
                            self.termites[other].trail.loc[frame_number, 'interaction_with_{}'.format(self.termites[n_termite].trail.loc[0, 'label'])] = 'head-head'

                        elif encouter_label == ord('w'):
                            cv2.imwrite(os.path.join(self.output_path, 'head-abdomen/{}-{}-head-abdomen.jpg'.format(self.termites[n_termite].trail.loc[0, 'label'],
                                                                        frame_number)), event)
                            self.termites[n_termite].trail.loc[frame_number, 'interaction_with_{}'.format(self.termites[other].trail.loc[0, 'label'])] = 'head-abdomen'
                            self.termites[other].trail.loc[frame_number, 'interaction_with_{}'.format(self.termites[n_termite].trail.loc[0, 'label'])] = 'head-abdomen'
                        elif encouter_label == ord('e'):
                            cv2.imwrite(os.path.join(self.output_path, 'no-interaction/{}-{}-no-interaction.jpg'.format(self.termites[n_termite].trail.loc[0, 'label'],
                                                                        frame_number)), event)

                        cv2.destroyWindow('Encounter')
        self._save_termite_data()


if __name__ == '__main__':
    labeling = LabelingSession('data/Sample Experiment')
    labeling.start_session()
