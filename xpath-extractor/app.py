import os
import re
import socket
import ipaddress
import email
from urllib.parse import urlparse
from flask import Flask, request, jsonify, render_template
import requests
from lxml import html
from charset_normalizer import detect

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB limit

# --- SSRF & Security Protection ---
def is_safe_url(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        # Resolve to IP to prevent DNS pinning / private range access
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)
        return not ip_obj.is_private
    except Exception:
        return False

# --- MHTML Parser ---
def extract_html_from_mhtml(mhtml_bytes):
    try:
        msg = email.message_from_bytes(mhtml_bytes)
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ['text/html', 'application/xhtml+xml']:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or 'utf-8'
                try:
                    return payload.decode(charset, errors='replace')
                except Exception:
                    return payload.decode('latin-1', errors='replace')
    except Exception:
        pass
    # Fallback: regex search for raw html sections if mime parsing choked
    try:
        raw_text = mhtml_bytes.decode('utf-8', errors='ignore')
        html_match = re.search(r'<html.*?</html>', raw_text, re.DOTALL | re.IGNORECASE)
        if html_match:
            return html_match.group(0)
    except Exception:
        pass
    raise ValueError("Could not extract valid HTML from MHTML structure.")

# --- Robust XPath Generation Engine ---
def generate_xpaths_for_element(el, tree):
    candidates = []
    
    # 1. ID Selector (Highest Reliability)
    el_id = el.get('id')
    if el_id and not re.search(r'\d{4,}', el_id): # Ignore dynamic looking numeric IDs
        xpath = f"//*[@id='{el_id}']"
        if len(tree.xpath(xpath)) == 1:
            candidates.append({"xpath": xpath, "type": "ID Match", "score": 100})

    # 2. Unique Attributes (data-*, name, role, itemid)
    sticky_attrs = ['data-id', 'data-qa', 'data-cy', 'name', 'itemprop', 'role']
    for attr in sticky_attrs:
        val = el.get(attr)
        if val:
            xpath = f"//{el.tag}[@{attr}='{val}']"
            count = len(tree.xpath(xpath))
            if count == 1:
                candidates.append({"xpath": xpath, "type": f"Attribute [@{attr}]", "score": 90})
            elif 1 < count <= 3:
                # Add index if it limits the selection space gracefully
                for idx in range(1, count + 1):
                    idx_xpath = f"(//{el.tag}[@{attr}='{val}'])[{idx}]"
                    candidates.append({"xpath": idx_xpath, "type": f"Attribute [@{attr}] with Index", "score": 75})

    # 3. Class Name + Tag combinations
    classes = el.get('class')
    if classes:
        first_class = classes.split()[0]
        xpath = f"//{el.tag}[contains(concat(' ', normalize-space(@class), ' '), ' {first_class} ')]"
        count = len(tree.xpath(xpath))
        if count == 1:
            candidates.append({"xpath": xpath, "type": "Class Match", "score": 80})

    # 4. Text content matching (normalize-space)
    node_text = "".join(el.itertext()).strip()
    if node_text and len(node_text) < 50:
        clean_text = re.sub(r'\s+', ' ', node_text).replace("'", "\\'")
        xpath = f"//{el.tag}[normalize-space()='{clean_text}']"
        if len(tree.xpath(xpath)) == 1:
            candidates.append({"xpath": xpath, "type": "Exact Text Match", "score": 85})
        else:
            xpath_contains = f"//{el.tag}[contains(normalize-space(), '{clean_text[:25]}')]"
            if len(tree.xpath(xpath_contains)) == 1:
                candidates.append({"xpath": xpath_contains, "type": "Partial Text Match", "score": 70})

    # 5. Fallback Absolute Position Path
    parts = []
    current = el
    while current is not None and current.tag != 'html':
        parent = current.getparent()
        if parent is not None:
            siblings = parent.findall(current.tag)
            if len(siblings) > 1:
                idx = siblings.index(current) + 1
                parts.append(f"{current.tag}[{idx}]")
            else:
                parts.append(current.tag)
            current = parent
        else:
            parts.append(current.tag)
            break
    parts.append("html")
    absolute_path = "/" + "/".join(reversed(parts))
    candidates.append({"xpath": absolute_path, "type": "Structural Absolute Path", "score": 40})

    # Deduplicate paths safely keeping highest scores
    seen = set()
    deduped = []
    for cand in sorted(candidates, key=lambda x: x['score'], reverse=True):
        if cand['xpath'] not in seen:
            seen.add(cand['xpath'])
            deduped.append(cand)
    return deduped

# --- Core Query/Matching Logic ---
def execute_search(html_text, query, mode):
    # Setup safe error recovery parser
    parser = html.HTMLParser(recover=True, remove_comments=True)
    tree = html.fromstring(html_text.encode('utf-8', errors='replace'), parser=parser)
    
    results = []
    query_clean = query.strip().lower()

    # Strategy Functions
    def search_as_value():
        # Match elements where raw inner text or attribute contents contain value
        elements = tree.xpath("//*[text() or @*]")
        for el in elements:
            # Check Text content
            el_text = "".join(el.itertext()).strip()
            if query_clean in el_text.lower():
                snippet = el_text[:60] + "..." if len(el_text) > 60 else el_text
                paths = generate_xpaths_for_element(el, tree)
                if paths:
                    results.append({"matched_text": snippet, "mode_found": "Value Match", "paths": paths})
            
            # Check Attributes
            for attr, val in el.attrib.items():
                if query_clean in val.lower():
                    paths = generate_xpaths_for_element(el, tree)
                    if paths:
                        results.append({"matched_text": f"@{attr}='{val}'", "mode_found": "Attribute Value Match", "paths": paths})

    def search_as_key():
        # Find structural Labels/Headers, then find nearby sister data/values
        all_nodes = tree.xpath("//*[text()]")
        for el in all_nodes:
            el_text = "".join(el.itertext()).strip()
            if query_clean in el_text.lower() and len(el_text) < 40:
                # Key label found! Look for relational values nearby
                candidates = []
                
                # Check following sibling node
                sibling = el.getnext()
                if sibling is not None: candidates.append(sibling)
                
                # Check parent's following sibling (common in form layouts)
                parent = el.getparent()
                if parent is not None:
                    p_sibling = parent.getnext()
                    if p_sibling is not None:
                        candidates.append(p_sibling)
                        # Check inside structural table cell mappings
                        if p_sibling.tag == 'td' or p_sibling.xpath(".//td"):
                            candidates.extend(p_sibling.xpath(".//*[text()]")[:2])

                # Extract first valid structural target
                for target in candidates:
                    target_text = "".join(target.itertext()).strip()
                    if target_text:
                        paths = generate_xpaths_for_element(target, tree)
                        if paths:
                            results.append({
                                "matched_text": f"Value near key '{el_text}': {target_text[:50]}",
                                "mode_found": "Key-to-Value Association",
                                "paths": paths
                            })
                        break

    # Route execution depending on mode selection
    if mode == 'value':
        search_as_value()
    elif mode == 'key':
        search_as_key()
    else: # 'auto' Fallback Flow
        search_as_value()
        if not results:
            search_as_key()

    # Deduplicate results list
    unique_results = []
    seen_paths = set()
    for res in results:
        primary_path = res['paths'][0]['xpath']
        if primary_path not in seen_paths:
            seen_paths.add(primary_path)
            unique_results.append(res)
            
    return unique_results[:10] # Limit to top 10 matches for layout neatness

# --- API Endpoints ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    mode = request.form.get('mode', 'auto')
    query = request.form.get('query', '')
    
    if not query:
        return jsonify({"error": "Search keyword/value parameter is required"}), 400

    html_content = ""
    
    try:
        # Scenario A: Processing via Live URL Fetching
        if 'url' in request.form and request.form['url'].strip():
            url = request.form['url'].strip()
            if not is_safe_url(url):
                return jsonify({"error": "Access denied: Invalid or insecure Private IP range URL architecture."}), 400
            
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Scraper/1.0"}
            response = requests.get(url, headers=headers, timeout=15, verify=True)
            
            if response.status_code != 200:
                return jsonify({"error": f"Failed remote fetch. Server returned status code: {response.status_code}"}), 400
                
            # Content encoding detection strategy
            detected = detect(response.content)
            encoding = detected.get('encoding') or response.apparent_encoding or 'utf-8'
            html_content = response.content.decode(encoding, errors='replace')
            
        # Scenario B: Processing via Uploaded File Stream
        elif 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file payload selected for upload"}), 400
                
            file_bytes = file.read()
            filename = file.filename.lower()
            
            if filename.endswith('.mhtml') or filename.endswith('.mht'):
                html_content = extract_html_from_mhtml(file_bytes)
            else:
                # Raw document fallbacks
                try:
                    html_content = file_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    html_content = file_bytes.decode('latin-1', errors='replace')
        else:
            return jsonify({"error": "Missing input context: Please supply a live URL page or drop an HTML/MHTML asset file."}), 400

        # Execute Document Inspection Engine
        matches = execute_search(html_content, query, mode)
        return jsonify({"success": True, "results": matches})

    except requests.exceptions.Timeout:
        return jsonify({"error": "The connection timed out while trying to fetch the requested URL route (15s limit)."}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "DNS resolution failed or remote server completely rejected connections."}), 502
    except Exception as e:
        return jsonify({"error": f"Internal Processing Error Exception encountered: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)