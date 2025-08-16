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
cooldown = 1.0  # seconds

# Play/Stop state
is_playing = False

# Check which fingers are up
def fingers_up(hand_landmarks1):
    fingers2 = []

    # Thumb
    if hand_landmarks1.landmark[tip_ids[0]].x < hand_landmarks1.landmark[tip_ids[0] - 1].x:
        fingers2.append(1)
    else:
        fingers2.append(0)

    # Other fingers
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
        return "Fist (Stop)"
    elif fingers1 == [0, 1, 1, 0, 0]:
        return "Two Fingers (Mute/Unmute)"
    elif fingers1 == [0, 1, 0, 0, 0]:
        return "Index Only (Volume Up)"
    elif fingers1 == [0, 0, 0, 0, 1]:
        return "Pinky Only (Volume Down)"
    elif fingers1 == [1, 0, 0, 0, 1]:
        return "Thumb + Pinky (Next Video)"
    elif fingers1 == [1, 1, 1, 1, 0]:
        return "Four Fingers (Previous Video)"
    else:
        return None

# Simulate keyboard actions
def execute_command(gesture1):
    global last_action_time, is_playing
    if time.time() - last_action_time < cooldown:
        return

    print(f"Executing: {gesture1}")
    if gesture1 == "Open Palm (Play)":
        if not is_playing:  # Play only if currently stopped
            pyautogui.press('k')  # YouTube play
            is_playing = True
    elif gesture1 == "Fist (Stop)":
        if is_playing:  # Stop only if currently playing
            pyautogui.press('k')  # YouTube pause
            is_playing = False
    elif gesture1 == "Two Fingers (Mute/Unmute)":
        pyautogui.press('volumemute')
    elif gesture1 == "Index Only (Volume Up)":
        pyautogui.press('volumeup')
    elif gesture1 == "Pinky Only (Volume Down)":
        pyautogui.press('volumedown')
    elif gesture1 == "Thumb + Pinky (Next Video)":
        pyautogui.hotkey('shift', 'n')
    elif gesture1 == "Four Fingers (Previous Video)":
        pyautogui.hotkey('shift', 'p')

    last_action_time = time.time()

# Draw navigation panel
def draw_panel(img):
    panel_x, panel_y = 10, 100
    panel_w, panel_h = 360, 240
    cv2.rectangle(img, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), (40, 40, 40), -1)
    cv2.putText(img, "Gesture Controls:", (panel_x + 10, panel_y + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    controls = [
        "Open Palm      -> Play",
        "Fist           -> Stop",
        "Two Fingers    -> Mute/Unmute",
        "Index Only     -> Volume Up",
        "Pinky Only     -> Volume Down",
        "Thumb + Pinky  -> Next Video",
        "Four Fingers   -> Prev Video"
    ]

    for i, text in enumerate(controls):
        cv2.putText(img, text, (panel_x + 10, panel_y + 60 + i * 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

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

    # Draw navigation panel
    draw_panel(img)

    cv2.imshow("GesturePilot", img)

    # Exit if window closed or 'q' pressed
    if cv2.getWindowProperty("GesturePilot", cv2.WND_PROP_VISIBLE) < 1:
        break
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

