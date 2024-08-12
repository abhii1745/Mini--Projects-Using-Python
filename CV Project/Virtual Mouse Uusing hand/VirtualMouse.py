import mediapipe as mp
import cv2
import numpy as np
from math import sqrt
import win32api
import pyautogui


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


video = cv2.VideoCapture(0)


prev_cursor_pos = None
prev_index_finger_y = None
prev_middle_finger_y = None


SMOOTHING_FACTOR = 0.9


with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8) as hands:
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break

       
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = cv2.flip(image, 1)
        imageHeight, imageWidth, _ = image.shape

       
        results = hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2))

              
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

               
                index_finger_x = int(index_finger_tip.x * imageWidth)
                index_finger_y = int(index_finger_tip.y * imageHeight)
                middle_finger_x = int(middle_finger_tip.x * imageWidth)
                middle_finger_y = int(middle_finger_tip.y * imageHeight)
                thumb_x = int(thumb_tip.x * imageWidth)
                thumb_y = int(thumb_tip.y * imageHeight)

              
                print(f"Index finger: ({index_finger_x}, {index_finger_y}), Middle finger: ({middle_finger_x}, {middle_finger_y}), Thumb: ({thumb_x}, {thumb_y})")

              
                new_cursor_pos = (index_finger_x * 4, index_finger_y * 5)

                if prev_cursor_pos is None:
                    prev_cursor_pos = new_cursor_pos

    
                smooth_cursor_pos = (
                    int(prev_cursor_pos[0] * (1 - SMOOTHING_FACTOR) + new_cursor_pos[0] * SMOOTHING_FACTOR),
                    int(prev_cursor_pos[1] * (1 - SMOOTHING_FACTOR) + new_cursor_pos[1] * SMOOTHING_FACTOR)
                )

                # Move the cursor
                win32api.SetCursorPos(smooth_cursor_pos)

                # Update previous cursor position
                prev_cursor_pos = smooth_cursor_pos

              
                distance_thumb_index = sqrt((index_finger_x - thumb_x) ** 2 + (index_finger_y - thumb_y) ** 2)

   
                if distance_thumb_index < 30:
                    pyautogui.click()
                    print("Click performed")

               
                if abs(index_finger_x - middle_finger_x) < 20: 
                    if prev_index_finger_y is not None and prev_middle_finger_y is not None:
                        scroll_distance_index = index_finger_y - prev_index_finger_y
                        scroll_distance_middle = middle_finger_y - prev_middle_finger_y

                        if abs(scroll_distance_index) > 10 and abs(scroll_distance_middle) > 10:
                 
                            if (scroll_distance_index > 0 and scroll_distance_middle > 0) or \
                               (scroll_distance_index < 0 and scroll_distance_middle < 0):
                                pyautogui.scroll(-scroll_distance_index // 5) 
                                print("Scrolled", "down" if scroll_distance_index > 0 else "up")

             
                    prev_index_finger_y = index_finger_y
                    prev_middle_finger_y = middle_finger_y

       
        cv2.imshow('Hand Tracking', image)


        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

video.release()
cv2.destroyAllWindows()
