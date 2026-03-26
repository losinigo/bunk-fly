import json
import re

with open('questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

issues = []

for library in data:
    for chapter in library['chapters']:
        for q in chapter['questions']:
            q_id = q['id']
            q_issues = []

            # Check for missing correct answer
            if not q.get('correct_answer'):
                q_issues.append('missing correct_answer')

            # Check for missing or empty answers
            if not q.get('answers'):
                q_issues.append('no answers')
            else:
                # Check for fewer than 3 answer options
                if len(q['answers']) < 3:
                    q_issues.append(f"only {len(q['answers'])} answer(s): {list(q['answers'].keys())}")

                # Check for messy answer values (contain multiple options like "2. C.3.")
                for k, v in q['answers'].items():
                    if re.search(r'[A-D]\.\s*\d', v) or len(v) < 2:
                        q_issues.append(f"messy answer {k}: {repr(v)}")

            # Check for missing explanations
            if not q.get('explanations'):
                q_issues.append('no explanations')
            else:
                if len(q['explanations']) < 3:
                    q_issues.append(f"only {len(q['explanations'])} explanation(s)")

            # Check for OCR artifacts in question text
            artifacts = ['Onthe', 'Atan ', 'Ifthe', 'Ifa ', 'anIFR', 'Inwarmer']
            for a in artifacts:
                if a in q.get('question', ''):
                    q_issues.append(f"OCR artifact in question: '{a}'")

            if q_issues:
                issues.append((q_id, q_issues))

import re
print(f"Found {len(issues)} questions with issues:\n")
for q_id, q_issues in issues:
    print(f"  [{q_id}]")
    for issue in q_issues:
        print(f"    - {issue}")

if not issues:
    print("All questions look clean!")
