"""Abstracts the video manipulation by OpenCV."""


import cv2

class VideoPlayer:
    """An image sequence abstraction."""
    def __init__(self, source_path):
        """Initializer.

        Args:
            source_path (str): path to video source.
        Returns:
            None.
        """
        self.source = cv2.VideoCapture(source_path)
        if not self.source.isOpened:
            print('Could not open video.')
            sys.exit()
