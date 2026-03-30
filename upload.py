import json
import os
import requests

SUPABASE_URL = "https://flynsttdbritbkzbwpwq.supabase.co"
SUPABASE_KEY = "sb_secret_JFGmZZv2TYnXXW4hxFfWlg_vKbKUzfU"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def insert(table, payload):
    res = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=payload)
    if not res.ok:
        print(f"  ERROR inserting into {table}: {res.text}")
    res.raise_for_status()
    return res.json()[0]

def upsert(table, payload, on_conflict):
    headers = {**HEADERS, "Prefer": f"resolution=merge-duplicates,return=representation"}
    res = requests.post(f"{SUPABASE_URL}/rest/v1/{table}?on_conflict={on_conflict}", headers=headers, json=payload)
    res.raise_for_status()
    return res.json()[0]

def upload_figure(filename, filepath):
    storage_url = f"{SUPABASE_URL}/storage/v1/object/figures/{filename}"
    with open(filepath, 'rb') as f:
        res = requests.post(storage_url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/png"
        }, data=f)
    if res.status_code not in (200, 201):
        print(f"  Warning uploading {filename}: {res.text}")
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/figures/{filename}"
    return public_url

with open('questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Upload figures
print("Uploading figures...")
figure_url_map = {}
for filename in os.listdir('figures'):
    if not filename.endswith('.png'):
        continue
    filepath = os.path.join('figures', filename)
    url = upload_figure(filename, filepath)
    figure_url_map[filename] = url
    print(f"  {filename} -> {url}")

print(f"Figures done: {len(figure_url_map)}\n")

# Upload data
for library in data:
    lib = upsert('libraries', {'name': library['library']}, 'name')
    lib_id = lib['id']
    print(f"Library: {library['library']} (id={lib_id})")

    for chapter in library['chapters']:
        ch = insert('chapters', {
            'library_id': lib_id,
            'chapter_number': chapter['chapter'],
            'section': chapter['section']
        })
        ch_id = ch['id']
        print(f"  Chapter {chapter['chapter']}: {chapter['section']} (id={ch_id})")

        for q in chapter['questions']:
            # Insert question
            q_row = insert('questions', {
                'chapter_id': ch_id,
                'question_id': q['id'],
                'question': q['question'],
                'correct_answer': q.get('correct_answer'),
            })
            q_db_id = q_row['id']

            # Insert question_figures
            for screenshot in q.get('screenshots', []):
                if screenshot:
                    filename = os.path.basename(screenshot)
                    image_url = figure_url_map.get(filename)
                    if image_url:
                        fig = upsert('figures', {
                            'figure_ref': q['figure_refs'][q['screenshots'].index(screenshot)],
                            'image_url': image_url
                        }, 'figure_ref')
                        insert('question_figures', {
                            'question_id': q_db_id,
                            'figure_id': fig['id']
                        })

            # Insert answers
            for letter, text in q.get('answers', {}).items():
                insert('answers', {'question_id': q_db_id, 'letter': letter, 'answer': text})

            # Insert explanations
            for letter, text in q.get('explanations', {}).items():
                insert('explanations', {'question_id': q_db_id, 'letter': letter, 'explanation': text})

            print(f"    [{q['id']}] done")

print("\nAll data uploaded to Supabase.")
