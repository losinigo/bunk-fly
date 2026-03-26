import time
import json
import win32api
import win32con
from pywinauto import Desktop

ANSWER_OFFSETS = {'A': 215, 'B': 260, 'C': 304}
BTN_Y_RATIO = 0.94
NEXT_X_OFFSET = 794

def win32_click(x, y):
    win32api.SetCursorPos((x, y))
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(0.6)

with open('questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

desktop = Desktop(backend='uia')
gleim = desktop.window(class_name='TEmulationGleimForm')
listbox = gleim.child_window(title='FSidebarPanel', control_type='Pane').child_window(control_type='List')

children = listbox.children()
question_items = [c for c in children if c.window_text() and c.window_text() != 'Vertical']

# Navigate to first question
question_items[0].click_input()
time.sleep(0.6)

issues = []

for i, q in enumerate(questions):
    q_id = q['id']
    correct = q.get('correct_answer')

    win_rect = gleim.rectangle()
    btn_y = win_rect.top + int((win_rect.bottom - win_rect.top) * BTN_Y_RATIO)

    if not correct:
        print(f"[SKIP] {q_id} ({i+1}/{len(questions)}) - no correct answer recorded")
        issues.append(q_id)
    elif correct not in ANSWER_OFFSETS:
        print(f"[SKIP] {q_id} ({i+1}/{len(questions)}) - answer '{correct}' not in A/B/C")
        issues.append(q_id)
    else:
        x = win_rect.left + ANSWER_OFFSETS[correct]
        win32_click(x, btn_y)
        print(f"[OK]   {q_id} ({i+1}/{len(questions)}) - clicked {correct}")

    # Click Next
    if i < len(questions) - 1:
        win_rect = gleim.rectangle()
        next_x = win_rect.left + NEXT_X_OFFSET
        next_y = win_rect.top + int((win_rect.bottom - win_rect.top) * BTN_Y_RATIO)
        win32_click(next_x, next_y)

print(f"\nDone. {len(issues)} questions need review: {issues}")
