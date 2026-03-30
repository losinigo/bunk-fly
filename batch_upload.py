import json
import os
import requests
import hashlib

# --- CONFIG ---
SUPABASE_URL = "https://flynsttdbritbkzbwpwq.supabase.co"
SUPABASE_KEY = "sb_secret_JFGmZZv2TYnXXW4hxFfWlg_vKbKUzfU"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- UTILITY FUNCTIONS ---
def upsert_batch(table, payload_list, on_conflict):
    if not payload_list:
        return []
    headers = {**HEADERS, "Prefer": f"resolution=merge-duplicates,return=representation"}
    res = requests.post(f"{SUPABASE_URL}/rest/v1/{table}?on_conflict={on_conflict}", headers=headers, json=payload_list)
    res.raise_for_status()
    return res.json()

def delete_where(table, condition):
    if not condition:
        return
    res = requests.delete(f"{SUPABASE_URL}/rest/v1/{table}?{condition}", headers=HEADERS)
    res.raise_for_status()

def hash_file(filepath):
    """Return SHA1 hash of a file to detect changes."""
    h = hashlib.sha1()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def upload_figure_if_new(filename, filepath, existing_figures):
    """Upload figure only if new or changed."""
    file_hash = hash_file(filepath)
    existing = existing_figures.get(filename)
    if existing and existing.get('hash') == file_hash:
        return existing['id'], existing['public_url']

    # Upload to Supabase storage
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

    # Upsert in Supabase figures table with hash
    fig = upsert_batch('figures', [{
        'figure_ref': os.path.splitext(filename)[0],
        'image_url': public_url,
        'hash': file_hash
    }], 'figure_ref')[0]

    return fig['id'], fig['image_url']

# --- LOAD JSON ---
with open('questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# --- FETCH EXISTING FIGURES ---
existing_figures = {}
for fig in requests.get(f"{SUPABASE_URL}/rest/v1/figures", headers=HEADERS).json():
    existing_figures[fig['figure_ref'] + '.png'] = {'id': fig['id'], 'public_url': fig['image_url'], 'hash': fig.get('hash')}

# --- UPLOAD FIGURES ---
print("Uploading figures...")
figure_url_map = {}
figure_id_map = {}
for filename in os.listdir('figures'):
    if not filename.endswith('.png'):
        continue
    filepath = os.path.join('figures', filename)
    fig_id, url = upload_figure_if_new(filename, filepath, existing_figures)
    figure_url_map[filename] = url
    figure_id_map[filename] = fig_id
    print(f"  {filename} -> {url}")

print(f"Figures done: {len(figure_url_map)}\n")

# --- SYNC DATA ---
for library in data:
    # Upsert library
    lib = upsert_batch('libraries', [{'name': library['library']}], 'name')[0]
    lib_id = lib['id']
    print(f"Library: {library['library']} (id={lib_id})")

    # Fetch existing chapters for this library
    existing_chapters = {ch['chapter_number']: ch['id'] for ch in requests.get(
        f"{SUPABASE_URL}/rest/v1/chapters?library_id=eq.{lib_id}", headers=HEADERS
    ).json()}
    json_chapters = {ch['chapter']: ch for ch in library['chapters']}

    # Delete removed chapters + their questions
    for chapter_number, ch_id in existing_chapters.items():
        if chapter_number not in json_chapters:
            delete_where('questions', f'chapter_id=eq.{ch_id}')
            delete_where('chapters', f'id=eq.{ch_id}')
            print(f"  Deleted Chapter {chapter_number} (id={ch_id})")

    # Batch upsert chapters
    chapter_payloads = [{
        'library_id': lib_id,
        'chapter_number': ch['chapter'],
        'section': ch['section']
    } for ch in json_chapters.values()]
    upserted_chapters = upsert_batch('chapters', chapter_payloads, 'library_id,chapter_number')
    chapter_map = {ch['chapter_number']: ch['id'] for ch in upserted_chapters}

    # Sync questions per chapter
    for chapter_number, chapter in json_chapters.items():
        ch_id = chapter_map[chapter_number]

        existing_questions = {q['question_id']: q['id'] for q in requests.get(
            f"{SUPABASE_URL}/rest/v1/questions?chapter_id=eq.{ch_id}", headers=HEADERS
        ).json()}
        json_questions = {q['id']: q for q in chapter['questions']}

        # Delete removed questions
        for qid, q_db_id in existing_questions.items():
            if qid not in json_questions:
                delete_where('answers', f'question_id=eq.{q_db_id}')
                delete_where('explanations', f'question_id=eq.{q_db_id}')
                delete_where('questions', f'id=eq.{q_db_id}')
                print(f"    Deleted question {qid} (id={q_db_id})")

        # Batch upsert questions
        question_payloads = []
        for q in json_questions.values():
            figure_id = None
            if q.get('figure_ref') and q.get('screenshot'):
                filename = os.path.basename(q['screenshot'])
                figure_id = figure_id_map.get(filename)
            question_payloads.append({
                'chapter_id': ch_id,
                'question_id': q['id'],
                'question': q['question'],
                'correct_answer': q.get('correct_answer'),
                'figure_id': figure_id
            })

        upserted_questions = upsert_batch('questions', question_payloads, 'question_id')
        question_id_map = {q['question_id']: q['id'] for q in upserted_questions}

        # Batch upsert answers & explanations
        answer_payloads = []
        explanation_payloads = []
        for q in json_questions.values():
            q_db_id = question_id_map[q['id']]
            for letter, text in q.get('answers', {}).items():
                answer_payloads.append({'question_id': q_db_id, 'letter': letter, 'answer': text})
            for letter, text in q.get('explanations', {}).items():
                explanation_payloads.append({'question_id': q_db_id, 'letter': letter, 'explanation': text})

        for i in range(0, len(answer_payloads), 50):
            upsert_batch('answers', answer_payloads[i:i+50], 'question_id,letter')
        for i in range(0, len(explanation_payloads), 50):
            upsert_batch('explanations', explanation_payloads[i:i+50], 'question_id,letter')

        print(f"  Chapter {chapter_number} synced")

print("\nAll data fully synced and optimized with Supabase!")