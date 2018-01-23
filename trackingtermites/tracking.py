import cv2
import sys

def track(video_path):
    # Open video source
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print('Could not find the video file.')
        sys.exit()

    # Read first frame and resize
    playing, frame = video.read()
    frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
    if not playing:
        print('Could not start video.')
        sys.exit()

    # Select termites and start trackers
    tracker = cv2.Tracker_create('KCF')
    termite_pos = cv2.selectROI('Select the termite...', frame, False, False)
    tracker.init(frame, termite_pos)
    cv2.destroyWindow('Select the termite...')

    # Tracking loop
    while True:
        # Read next frame
        playing, frame = video.read()
        if not playing:
            break
        frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)

        # Update tracker
        found, termite_pos = tracker.update(frame)
        if not found:
            print('Termite lost.')

        # Draw termite on current frame
        cv2.rectangle(frame, (int(termite_pos[0]), int(termite_pos[1])), (int(termite_pos[0] + termite_pos[2]), int(termite_pos[1] + termite_pos[3])), (255, 0, 0))

        # Draw frame info
        cv2.putText(frame, f'Frame #{int(video.get(cv2.CAP_PROP_POS_FRAMES))}'
                           f' of {int(video.get(cv2.CAP_PROP_FRAME_COUNT))}',
                           (5,10), 1, color=(0, 0, 255), fontScale=0.7)

        # Show current frame
        cv2.imshow('Tracking...', frame)
        pressed_key = cv2.waitKey(1) & 0xff
        if pressed_key == 27:
            break
        if pressed_key == ord('p'):
            cv2.waitKey(0)

        # An unorthodox approach
        cv2.waitKey(0)


if __name__ == '__main__':
    track('D:/Og-footage/00100.MTS')
