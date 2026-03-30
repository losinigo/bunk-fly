import json
import re

with open('questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Common OCR artifacts to fix in question text
OCR_FIXES = {
    'Onthe ': 'On the ',
    'Atan ': 'At an ',
    'Inwarmer': 'In warmer',
    'anIFR': 'an IFR',
    'Ifthe': 'If the ',
    'Ifa ': 'If a ',
    'Ifboth': 'If both',
    '\n': ' ',
}

def clean_text(text):
    if not text:
        return text
    for bad, good in OCR_FIXES.items():
        text = text.replace(bad, good)
    text = re.sub(r' +', ' ', text).strip()
    return text

def clean_question_prefix(text):
    """Remove OCR junk before '(Refer to figure' in question text."""
    match = re.search(r'\(Refer to figure', text)
    if match and match.start() > 0:
        text = text[match.start():]
    return text

def clean_answer_contamination(text):
    """Remove explanation text that leaked into answer options."""
    # Pattern: answer text followed by "Answer (X) is incorrect/correct because..."
    cleaned = re.split(r'\s*Answer \([A-C]\) is (?:in)?correct\b', text)[0]
    return cleaned.strip()

q_fixed = 0
a_fixed = 0
for library in data:
    for chapter in library['chapters']:
        for q in chapter['questions']:
            # Clean question text
            original = q['question']
            q['question'] = clean_text(q['question'])
            q['question'] = clean_question_prefix(q['question'])
            if q['question'] != original:
                q_fixed += 1
                print(f"[Q] {q['id']}: {repr(original[:80])} -> {repr(q['question'][:80])}")

            # Clean answer texts
            for k, v in q['answers'].items():
                original = v
                q['answers'][k] = clean_text(v)
                q['answers'][k] = clean_answer_contamination(q['answers'][k])
                if q['answers'][k] != original:
                    a_fixed += 1
                    print(f"[A] {q['id']} {k}: {repr(original[:80])} -> {repr(q['answers'][k][:80])}")

            # Clean explanations
            for k, v in q['explanations'].items():
                q['explanations'][k] = clean_text(v)

print(f"\nFixed {q_fixed} questions, {a_fixed} answers.")

with open('questions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Saved to questions.json")
