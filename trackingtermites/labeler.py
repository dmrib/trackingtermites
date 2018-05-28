#!/usr/bin/env python

import cv2
import glob
import json
import numpy as np
import os
import sys

import termite as trmt


class ImageLabeler:
    def __init__(self, config_path):
        with open(config_path) as config_file:
            self.config = json.load(config_file)
        for event in self.config['events'].values():
            output_path = os.path.join(self.config['images_folder'], event)
            if not os.path.exists(output_path):
                os.makedirs(output_path)

    def label(self):
        images_paths = glob.glob(f'{self.config["images_folder"]}/*.jpg')
        for image_path in images_paths:
            image = cv2.imread(image_path)
            evaluation = self.create_evaluation_image(image)
            cv2.imshow('Labeling...', evaluation)
            pressed_key = cv2.waitKey(0)
            if pressed_key == 27:
                sys.exit()
            elif chr(pressed_key) in self.config['events']:
                image_name = os.path.basename(image_path)
                destination_folder = os.path.join(os.path.join(self.config['images_folder'],
                                                  self.config['events'][chr(pressed_key)]))
                cv2.imwrite(os.path.join(destination_folder, image_name), image)

    def create_evaluation_image(self, image):
        edges = cv2.Canny(image, 75, 75)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        evaluation = np.hstack((image, edges))
        evaluation = cv2.resize(evaluation, (0,0), fx=3, fy=3)
        return evaluation


if __name__ == '__main__':
    labeler = ImageLabeler('settings/labeler.json')
    labeler.label()
