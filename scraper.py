import time
import json
import re
import os
import pyautogui
import pytesseract
import win32api
import win32con
from pywinauto import Desktop

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

FIGURES_DIR = 'figures'
os.makedirs(FIGURES_DIR, exist_ok=True)

# x offsets from window left edge for A, B, C buttons and Next button
ANSWER_OFFSETS = {'A': 215, 'B': 260, 'C': 304}
NEXT_X_OFFSET = 794   # 1745 - 951 (window left)
BTN_Y_RATIO = 0.94    # buttons are at 94% of window height

def win32_click(x, y):
    win32api.SetCursorPos((x, y))
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(0.4)

def get_text(gleim):
    r = gleim.rectangle()
    region = (r.left + 185, r.top + 215, r.right - r.left - 185, int((r.bottom - r.top) * 0.70))
    return pytesseract.image_to_string(pyautogui.screenshot(region=region)).strip()

def get_screenshot(gleim):
    r = gleim.rectangle()
    region = (r.left + 185, r.top + 215, r.right - r.left - 185, int((r.bottom - r.top) * 0.70))
    return pyautogui.screenshot(region=region)

def parse_question(raw_text):
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    question_lines = []
    answers = {}
    current_key = None

    for line in lines:
        match = re.match(r'^([A-D])[\.\s]\s+(.*)', line)
        if match:
            current_key = match.group(1)
            answers[current_key] = match.group(2).strip()
        elif current_key:
            answers[current_key] += ' ' + line
        else:
            question_lines.append(line)

    question_text = re.sub(r'^\d+\.\s*', '', ' '.join(question_lines)).strip()

    bleed = re.search(r'\s([A-D])\s+(.+)$', question_text)
    if bleed and bleed.group(1) not in answers:
        answers[bleed.group(1)] = bleed.group(2).strip()
        question_text = question_text[:bleed.start()].strip()

    return question_text, answers

def parse_after_click(raw_text):
    m = re.search(r'Answer\s*\(([A-D])\)\s*is (correct|incorrect)[\.:]?\s*(.*?)(?=\n[A-D][\.\s]|\Z)', raw_text, re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(2).lower() == 'correct', m.group(3).strip()
    return None, None

def extract_figure_ref(text):
    match = re.search(r'Refer to figure (\w+)', text, re.IGNORECASE)
    return match.group(0) if match else None

def main():
    desktop = Desktop(backend='uia')
    gleim = desktop.window(class_name='TEmulationGleimForm')
    listbox = gleim.child_window(title='FSidebarPanel', control_type='Pane').child_window(control_type='List')

    children = listbox.children()
    question_items = [c for c in children if c.window_text() and c.window_text() != 'Vertical']
    total = len(question_items)
    print(f"Found {total} questions")

    question_items[0].click_input()
    time.sleep(0.4)

    results = []
    for i in range(total):
        q_id = question_items[i].window_text()
        print(f"Scraping {q_id} ({i+1}/{total})...", end=' ')

        raw_text = get_text(gleim)
        question, answers = parse_question(raw_text)
        figure_ref = extract_figure_ref(raw_text)
        screenshot_file = None

        if figure_ref:
            screenshot_file = f"{FIGURES_DIR}/{q_id}.png"
            get_screenshot(gleim).save(screenshot_file)

        # Click each answer and capture explanation
        correct_answer = None
        explanations = {}
        win_rect = gleim.rectangle()
        btn_y = win_rect.top + int((win_rect.bottom - win_rect.top) * BTN_Y_RATIO)

        for letter, x_offset in ANSWER_OFFSETS.items():
            win32_click(win_rect.left + x_offset, btn_y)
            is_correct, explanation = parse_after_click(get_text(gleim))
            if explanation:
                explanations[letter] = explanation
            if is_correct:
                correct_answer = letter

        print(f"correct={correct_answer} {'[HAS IMAGE]' if figure_ref else 'OK'}")

        results.append({
            "id": q_id,
            "question": question,
            "answers": answers,
            "correct_answer": correct_answer,
            "explanations": explanations,
            "figure_ref": figure_ref,
            "screenshot": screenshot_file
        })

        # Click Next using win32 to avoid pywinauto timeout issues
        if i < total - 1:
            win_rect = gleim.rectangle()
            next_x = win_rect.left + NEXT_X_OFFSET
            next_y = win_rect.top + int((win_rect.bottom - win_rect.top) * BTN_Y_RATIO)
            win32_click(next_x, next_y)

    with open('questions.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    figure_count = sum(1 for r in results if r['figure_ref'])
    print(f"\nDone! Saved {len(results)} questions ({figure_count} with figures) to questions.json")

if __name__ == '__main__':
    main()
