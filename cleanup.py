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
    # Collapse multiple spaces
    text = re.sub(r' +', ' ', text).strip()
    return text

fixed = 0
for library in data:
    for chapter in library['chapters']:
        for q in chapter['questions']:
            # Clean question text
            original = q['question']
            q['question'] = clean_text(q['question'])
            if q['question'] != original:
                fixed += 1
                print(f"[Q] {q['id']}: {repr(original[:60])} -> {repr(q['question'][:60])}")

            # Clean answer texts
            for k, v in q['answers'].items():
                original = v
                q['answers'][k] = clean_text(v)
                if q['answers'][k] != original:
                    print(f"[A] {q['id']} {k}: {repr(original[:60])} -> {repr(q['answers'][k][:60])}")

            # Clean explanations
            for k, v in q['explanations'].items():
                q['explanations'][k] = clean_text(v)

print(f"\nFixed {fixed} questions.")

with open('questions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Saved to questions.json")
