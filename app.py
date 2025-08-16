import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)

# Finger tip IDs (thumb to pinky)
tip_ids = [4, 8, 12, 16, 20]

# Cooldown variables
last_action_time = 0
cooldown = 1.5  # seconds

# Check which fingers are up
def fingers_up(hand_landmarks1):
    fingers2 = []

    # Thumb: compare x position (depends on hand orientation)
    if hand_landmarks1.landmark[tip_ids[0]].x < hand_landmarks1.landmark[tip_ids[0] - 1].x:
        fingers2.append(1)
    else:
        fingers2.append(0)

    # Other fingers: compare y position (tip above pip)
    for i in range(1, 5):
        if hand_landmarks1.landmark[tip_ids[i]].y < hand_landmarks1.landmark[tip_ids[i] - 2].y:
            fingers2.append(1)
        else:
            fingers2.append(0)

    return fingers2

# Gesture mapping
def get_gesture(fingers1):
    if fingers1 == [1, 1, 1, 1, 1]:
        return "Open Palm (Play)"
    elif fingers1 == [0, 0, 0, 0, 0]:
        return "Fist (Pause)"
    elif fingers1 == [0, 1, 1, 0, 0]:
        return "Volume Up"
    elif fingers1 == [0, 0, 0, 1, 1]:
        return "Volume Down"
    elif fingers1 == [0, 0, 0, 0, 1]:
        return "Next Video"
    elif fingers1 == [1, 1, 1, 1, 0]:
        return "Previous Video"
    else:
        return None

# Simulate keyboard actions
def execute_command(gesture1):
    global last_action_time
    if time.time() - last_action_time < cooldown:
        return

    print(f"Executing: {gesture1}")
    if gesture1 in ["Open Palm (Play)", "Fist (Pause)"]:
        pyautogui.press('space')
    elif gesture1 == "Volume Up":
        pyautogui.press('volumeup')
    elif gesture1 == "Volume Down":
        pyautogui.press('volumedown')
    elif gesture1 == "Next Video":
        pyautogui.hotkey('shift', 'n')
    elif gesture1 == "Previous Video":
        pyautogui.hotkey('shift', 'p')

    last_action_time = time.time()

# Main loop
while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            fingers = fingers_up(hand_landmarks)
            gesture = get_gesture(fingers)

            if gesture:
                cv2.putText(img, gesture, (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                            1.2, (0, 255, 0), 3)
                execute_command(gesture)

    cv2.imshow("YouTube Gesture Controller", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
