"""Abstracts the video manipulation by OpenCV."""

import sys
import cv2


class VideoPlayer:
    """A FSM for video input control."""
    def __init__(self, video_path, video_shape, filters, write_capture_info):
        """Initializer.

        Args:
            video_path (str): path to video file.
            video_shape (tuple): default size for frame redimensioning.
            filters (list): list of filter's names to apply in video source.
            write_info (bool): should write frame info when displaying.
        Returns:
            None.
        """
        if video_path == '-1':
            video_path = int(video_path)
        self.source = cv2.VideoCapture(video_path)
        if not self.source.isOpened:
            print('Could not find video file.')
            sys.exit()

        self.current_frame = None
        self.playing = False
        self.video_shape = video_shape
        self.filters = filters
        self.write_capture_info = write_capture_info
        self.start()

    def start(self):
        """Read video capture first frame.

        Args:
            None.
        Return:
            None.
        """
        self.next_frame()
        if not self.playing:
            print('Could not read video frame.')
            sys.exit()

    def next_frame(self):
        """Read video's next frame.

        Args:
            None.
        Returns:
            None.
        """
        self.playing, self.current_frame = self.source.read()

        if self.playing:
            self.current_frame = cv2.resize(self.current_frame,
                                            self.video_shape)
            if self.filters:
                self.current_frame = self.apply_filters(self.current_frame)
            if self.write_capture_info:
                self.write_info()

    def apply_filters(self, frame):
        """Apply specified filters to frame.

        Args:
            frame (np.ndarray): frame to be modified.
        Returns:
            n_frame (np.ndarray): modified frame.
        """
        n_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if 'g-blur' in self.filters:
            n_frame = cv2.GaussianBlur(n_frame, (5,5), 0)
        if 'b-filtering' in self.filters:
            n_frame = cv2.bilateralFilter(n_frame, 9, 75, 75)
        if 'canny' in self.filters:
            n_frame = cv2.Canny(n_frame, 100, 200)
        if 't_adaptive' in self.filters:
            n_frame = cv2.adaptiveThreshold(n_frame, 255,
                                            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 115, 1)
        if 'otsu' in self.filters:
            _, n_frame = cv2.threshold(n_frame, 125, 255,
                                       cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        n_frame = cv2.cvtColor(n_frame, cv2.COLOR_GRAY2BGR)

        return n_frame

    def pause(self):
        """Pauses image sequence.

        Args:
            None.
        Returns:
            None.
        """
        cv2.waitKey()

    def show_current_frame(self, window_name):
        """Display current frame.

        Args:
            None.
        Returns:
            None.
        """
        cv2.imshow(window_name, self.current_frame)

    def write_info(self):
        """Write video status info on current frame.

        Args:
            None.
        Returns:
            None.
        """
        cv2.putText(self.current_frame,
                    '#{:.0f} of {:.0f}, {:.0f}fps.'.format(self.source.get(cv2.CAP_PROP_POS_FRAMES),
                    self.source.get(cv2.CAP_PROP_FRAME_COUNT), self.source.get(cv2.CAP_PROP_FPS)),
                    (10,10), 1, color=(0, 0, 0), fontScale=0.7)

    def draw_label(self, label, color, coordinate):
        """Draw label at coordinate on current frame.

        Args:
            label (str): label text.
            color (tuple): label color.
            coordinates (tuple): label coordinate.
        Returns:
            None.
        """
        cv2.putText(self.current_frame, label, coordinate, 2, color=color,
                    fontScale=0.3)

    def draw_line(self, origin, end, color):
        """Draw line from origin to end on current frame.

        Args:
            origin (tuple): line origin point.
            end (tuple): line end point.
            color (tuple): line color.
        """
        cv2.line(self.current_frame, origin, end, color=color, thickness=1)

    def draw_b_box(self, origin, end, color, strong=False):
        """Draw bounding box on current frame.

        Args:
            origin (tuple): bounding box origin point.
            end (tuple): bounding box end point.
            color (tuple): bounding box color.
            strong (bool): should use collision style box.
        Returns:
            None.
        """
        if strong:
            cv2.rectangle(self.current_frame, origin, end, color, 5)
        else:
            cv2.rectangle(self.current_frame, origin, end, color)

    def select_roi(self):
        """Prompt user for a region of interest.

        Args:
            None.
        Returns:
            ROI (tuple): selected ROI coordinates.
        """
        ROI = cv2.selectROI('Select region of interest...', self.current_frame,
                            False, False)
        cv2.destroyWindow('Select region of interest...')
        return ROI
