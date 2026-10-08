import json
import os
import re
import sys
import html
import time
from datetime import datetime
from time import mktime
from bs4 import BeautifulSoup
import feedparser

try:
    from curl_cffi import requests
except ImportError:
    print("ERROR: curl_cffi is required. pip install curl_cffi")
    sys.exit(1)

try:
    from google import genai
except ImportError:
    print("ERROR: Please install the new SDK: pip install google-genai")
    sys.exit(1)

# --- CONFIGURATION ---
RSS_URL = "https://rss.dw.com/xml/DKpodcast_lgn_de"
ABSOLUTE_CSS_URL = "https://roman-zajic.github.io/deutsch-portal/lessons/lesson.css"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERROR: Please set the GEMINI_API_KEY environment variable.")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

# Ensure lessons directory exists
os.makedirs("lessons", exist_ok=True)

# --- STEP 1: Read RSS Feed ---
print("=== STEP 1: Reading RSS Feed ===")
feed = feedparser.parse(RSS_URL)
entry = feed.entries[0]

title = entry.get("title", "")

published_tuple = entry.published_parsed
lesson_date = datetime.fromtimestamp(mktime(published_tuple)).strftime("%Y-%m-%d")
lesson_filename = f"{lesson_date}.html"
lesson_filepath = os.path.join("lessons", lesson_filename)

print(f"-> Target output file: {lesson_filepath}")

if os.path.exists(lesson_filepath):
    print(f"[!] Lesson {lesson_filename} already exists. Skipping generation.")
    # We don't exit here anymore! We proceed to Step 6 just to ensure the JSON manifest is always up to date.
    html_content = None
else:
    # Extract audio link
    audio_link = None
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get("href"):
                audio_link = enc.get("href")
                break
    if not audio_link:
        for link in entry.get("links", []):
            if link.get("rel") == "enclosure":
                audio_link = link.get("href")
                break

    raw_url = entry.link.split("?")[0]
    canonical_url = re.sub(r"(\d{2})-(\d{2})-(\d{4})", r"\1\2\3", raw_url)

    # --- STEP 2: Scrape Content ---
    print("\n=== STEP 2: Fetching Webpage ===")
    html_content = ""
    for url in [canonical_url, raw_url]:
        try:
            resp = requests.get(url, impersonate="chrome", timeout=15)
            if resp.status_code == 200 and len(resp.text) > 1000:
                html_content = resp.text
                break
        except Exception as e:
            print(f"-> Request error: {e}")

    span_html_content = ""
    span_plain_text = ""

    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        for span in soup.find_all("span"):
            if span.find("h2") and span.find("p"):
                span_html_content = span.decode_contents().strip()
                span_plain_text = span.get_text(separator="\n\n", strip=True)
                break

        if not span_html_content:
            container = soup.find("div", {"data-testid": "richtext-content-container"}) or soup.find("div",
                                                                                                     class_=lambda
                                                                                                         c: c and "suu7vya" in c)
            if container:
                target_span = container.find("span") or container
                span_html_content = target_span.decode_contents().strip()
                span_plain_text = target_span.get_text(separator="\n\n", strip=True)

        if not span_html_content and "__APOLLO_STATE__" in html_content:
            match = re.search(r"window\.__APOLLO_STATE__\s*=\s*(\{.*?\});", html_content)
            if match:
                try:
                    data = json.loads(match.group(1))
                    for key, val in data.items():
                        if isinstance(val, dict) and "text" in val and "<h2>" in val["text"]:
                            span_html_content = val["text"].strip()
                            span_plain_text = BeautifulSoup(span_html_content, "html.parser").get_text(separator="\n\n",
                                                                                                       strip=True)
                            break
                except Exception:
                    pass

    if not span_plain_text or len(span_plain_text) < 100:
        print("\n[!] ERROR: Could not extract article text. Halting.")
        sys.exit(1)

    # --- STEP 3: Gemini AI Vocabulary Extraction ---
    print("\n=== STEP 3: Gemini AI Vocabulary Extraction ===")
    prompt = f"""
    You are an expert German teacher. Read the following news text which contains multiple short articles.
    For EACH article, identify 10 to 15 difficult words that a B1/B2 level German student might not understand.
    Return ONLY a valid JSON array of objects. Do not use markdown blocks.

    Schema per object:
    {{
      "id": "123",
      "exact_word_in_text": "word in text",
      "word": "base word",
      "translation": "English",
      "partOfSpeech": "Noun",
      "article": "der",
      "level": "B1",
      "plural": "die Wörter",
      "notes": "note",
      "examples": ["Ex1", "Ex2"]
    }}

    Text to analyze:
    {span_plain_text}
    """

    vocab_data = []
    max_retries = 3

    for attempt in range(max_retries):
        try:
            print(f"-> Sending request to gemini-3.8-flash (Attempt {attempt + 1}/{max_retries})...")
            ai_response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt
            )

            json_string = ai_response.text.strip()
            if json_string.startswith("```json"):
                json_string = json_string[7:]
            if json_string.endswith("```"):
                json_string = json_string[:-3]

            vocab_data = json.loads(json_string)
            print(f"-> Successfully extracted {len(vocab_data)} vocabulary words!")
            break
        except Exception as e:
            print(f"-> Failed to parse AI JSON: {e}")
            if attempt < max_retries - 1:
                print("-> Waiting 10 seconds before retrying...")
                time.sleep(10)

    # --- STEP 4: Highlighting Words in HTML ---
    print("\n=== STEP 4: Highlighting Words in HTML ===")
    soup_content = BeautifulSoup(span_html_content, 'html.parser')

    for word_obj in vocab_data:
        exact_word = word_obj.get("exact_word_in_text", "")
        if not exact_word:
            continue
        json_str = html.escape(json.dumps(word_obj, ensure_ascii=False))
        pattern = re.compile(rf'(?<![a-zA-ZäöüÄÖÜß])({re.escape(exact_word)})(?![a-zA-ZäöüÄÖÜß])')

        for text_node in soup_content.find_all(string=True):
            if text_node.parent.name in ['script', 'style'] or 'vocab-word' in text_node.parent.get('class', []):
                continue
            if exact_word in text_node:
                new_text = pattern.sub(rf'<span class="vocab-word" data-json="{json_str}">\1</span>', text_node)
                if new_text != text_node:
                    new_soup = BeautifulSoup(new_text, 'html.parser')
                    text_node.replace_with(new_soup)

    highlighted_html_content = str(soup_content)

    # --- STEP 5: Generate HTML ---
    print("\n=== STEP 5: Generating Lesson HTML ===")
    html_output = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0, viewport-fit=cover" name="viewport"/>
<title>{title} | Audio</title>
<link href="{ABSOLUTE_CSS_URL}" rel="stylesheet"/>
<style>
    .vocab-word {{ color: #d97706; font-weight: 600; cursor: pointer; border-bottom: 1px dashed #d97706; transition: background-color 0.2s; }}
    .vocab-word:hover {{ background-color: #fef3c7; }}
    .modal-overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 9999; align-items: center; justify-content: center; backdrop-filter: blur(2px); }}
    .modal-content {{ background: white; padding: 24px; border-radius: 12px; max-width: 500px; width: 90%; box-shadow: 0 10px 25px rgba(0,0,0,0.15); position: relative; font-family: sans-serif; }}
    .modal-close {{ position: absolute; top: 16px; right: 16px; cursor: pointer; font-size: 24px; line-height: 1; color: #64748b; }}
    .modal-close:hover {{ color: #0f172a; }}
    .m-title {{ font-size: 1.5rem; color: #1e293b; margin: 0 0 8px 0; font-weight: 700; }}
    .m-meta {{ font-size: 0.9rem; color: #64748b; margin-bottom: 16px; }}
    .m-trans {{ font-size: 1.15rem; color: #0f172a; margin-bottom: 12px; font-weight: 500; }}
    .m-notes {{ font-size: 0.95rem; color: #475569; margin-bottom: 16px; font-style: italic; }}
    .m-examples {{ background: #f8fafc; padding: 16px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #e2e8f0; }}
    .m-examples ul {{ margin: 0; padding-left: 20px; color: #334155; }}
    .m-examples li {{ margin-bottom: 8px; }}
    .copy-btn {{ background: #f59e0b; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; width: 100%; transition: background 0.2s; }}
    .copy-btn:hover {{ background: #d97706; }}
</style>
</head>
<body>
<nav class="navbar">
<a aria-label="Deutsch Lernen home" class="brand-icon" href="../">
<svg fill="none" height="17" viewBox="0 0 31 22" width="24" xmlns="http://www.w3.org/2000/svg">
<rect fill="#95DFDB" height="6" rx="1.5" width="9" x="0" y="0"></rect><rect fill="#50C1C1" height="6" rx="1.5" width="9" x="11" y="0"></rect><rect fill="#008282" height="6" rx="1.5" width="9" x="22" y="0"></rect><rect fill="#95DFDB" height="6" rx="1.5" width="9" x="0" y="8"></rect><rect fill="#50C1C1" height="6" rx="1.5" width="9" x="11" y="8"></rect><rect fill="#008282" height="6" rx="1.5" width="9" x="22" y="8"></rect><rect fill="#95DFDB" height="6" rx="1.5" width="9" x="0" y="16"></rect><rect fill="#50C1C1" height="6" rx="1.5" width="9" x="11" y="16"></rect><rect fill="#E1A01E" height="6" rx="1.5" width="9" x="22" y="16"></rect>
</svg>
</a>
<div class="nav-pipe"></div>
<a class="nav-brand-text" href="index.html">Lessons</a>
<div class="nav-actions">
<a aria-label="Back to all modules" class="icon-btn" href="index.html" title="Back to all modules">
<svg class="line" viewBox="0 0 24 24"><path d="M3 12l9-9 9 9"></path><path d="M5 10v10h14V10"></path></svg>
</a>
</div>
</nav>

<div class="wrap">
<h1>{title}</h1>
<section>
<div class="audio-player-container" style="margin: 20px 0;">
<audio controls style="width: 100%;">
    <source src="{audio_link}" type="audio/mpeg"/>
</audio>
</div>
<div class="article-content" style="margin-top: 25px; line-height: 1.8;">
{highlighted_html_content}
</div>
<div class="source-link" style="margin-top: 25px; font-size: 0.9em;">
<a href="{canonical_url}" target="_blank" rel="noopener noreferrer">Quelle: Deutsche Welle (Originalbeitrag öffnen) &rarr;</a>
</div>
</section>
<footer><strong>Deutsch Lernen</strong> · <a href="index.html">alle Lektionen</a></footer>
</div>

<div class="modal-overlay" id="vocab-modal">
    <div class="modal-content">
        <div class="modal-close" id="modal-close">&times;</div>
        <h3 class="m-title" id="m-title">Word</h3>
        <div class="m-meta" id="m-meta">Noun • B1</div>
        <div class="m-trans" id="m-trans">Translation</div>
        <div class="m-notes" id="m-notes">Notes</div>
        <div class="m-examples"><ul id="m-examples-list"></ul></div>
        <button class="copy-btn" id="copy-json-btn">Copy JSON</button>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', () => {{
    const modal = document.getElementById('vocab-modal');
    const closeBtn = document.getElementById('modal-close');
    const copyBtn = document.getElementById('copy-json-btn');
    let currentJsonString = "";

    document.querySelectorAll('.vocab-word').forEach(wordEl => {{
        wordEl.addEventListener('click', (e) => {{
            const data = JSON.parse(e.target.getAttribute('data-json'));
            currentJsonString = JSON.stringify(data, null, 2);
            let title = data.word;
            if(data.article) title = data.article + " " + title;
            document.getElementById('m-title').textContent = title;
            let metaText = `${{data.partOfSpeech}} • ${{data.level}}`;
            if(data.plural) metaText += ` • Plural: ${{data.plural}}`;
            document.getElementById('m-meta').textContent = metaText;
            document.getElementById('m-trans').textContent = data.translation;
            document.getElementById('m-notes').textContent = data.notes || "";
            const exList = document.getElementById('m-examples-list');
            exList.innerHTML = '';
            if(data.examples && data.examples.length > 0) {{
                data.examples.forEach(ex => {{
                    const li = document.createElement('li');
                    li.textContent = ex;
                    exList.appendChild(li);
                }});
            }}
            modal.style.display = 'flex';
        }});
    }});
    closeBtn.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (e) => {{ if(e.target === modal) modal.style.display = 'none'; }});
    copyBtn.addEventListener('click', () => {{
        navigator.clipboard.writeText(currentJsonString).then(() => {{
            const oldText = copyBtn.textContent;
            copyBtn.textContent = "JSON Copied!";
            setTimeout(() => copyBtn.textContent = oldText, 2000);
        }});
    }});
}});
</script>
</body>
</html>
"""
    with open(lesson_filepath, "w", encoding="utf-8") as f:
        f.write(html_output)
    print(f"-> Saved: {lesson_filepath}")

# --- STEP 6: Build `lessons.json` manifest dynamically ---
print("\n=== STEP 6: Rebuilding lessons.json manifest ===")
manifest = []

# Scan the folder for all HTML files that look like a date
for filename in os.listdir("lessons"):
    if filename.endswith(".html") and filename != "index.html" and re.match(r"\d{4}-\d{2}-\d{2}", filename):
        file_path = os.path.join("lessons", filename)
        file_date = filename.replace(".html", "")

        # Open file simply to grab its <title>
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read(2000)  # Read only first 2000 chars for speed
            title_match = re.search(r"<title>(.*?)\s*\|\s*Audio</title>", content)
            file_title = title_match.group(1).strip() if title_match else f"Lektion vom {file_date}"

        manifest.append({
            "filename": filename,
            "title": file_title,
            "date": file_date
        })

# Sort the list so the newest dates appear first
manifest.sort(key=lambda x: x["date"], reverse=True)

# Save to lessons.json
manifest_path = os.path.join("lessons", "lessons.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"-> Successfully mapped {len(manifest)} lessons into lessons.json!")
print("\n=== ALL DONE! ===")