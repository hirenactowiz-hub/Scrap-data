import email
import json
import re
from parsel import Selector


def load_mhtml_as_html(path):
    """
    MHTML files are MIME multipart messages, and the HTML part is usually
    Content-Transfer-Encoding: quoted-printable. Reading the file as plain
    text (like the original script did) leaves the quoted-printable escape
    sequences (=3D, =2F, soft line breaks, etc.) in the text.

    This parses the MHTML properly with the `email` module so each part is
    correctly decoded to real bytes/text.
    """
    with open(path, "rb") as f:
        msg = email.message_from_binary_file(f)

    html_parts = []
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            payload = part.get_payload(decode=True)  # decodes quoted-printable/base64
            charset = part.get_content_charset() or "utf-8"
            html_parts.append(payload.decode(charset, errors="ignore"))

    return "\n".join(html_parts)


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_js_object(raw_line):
    """
    Each matched line looks like:
        window.__initialState__ = {...json...}
    Strip the `window.X = ` prefix and parse the remainder as JSON.
    Returns (var_name, parsed_json_or_None).
    """
    match = re.match(r"\s*window\.(\w+)\s*=\s*(\{.*\})\s*(?:</script>)?\s*$", raw_line)
    if not match:
        return None, None

    var_name, json_blob = match.group(1), match.group(2)
    try:
        return var_name, json.loads(json_blob)
    except json.JSONDecodeError as e:
        # Some pages append trailing markup after the JSON object; try trimming
        try:
            # Find the last closing brace that makes it valid JSON
            for end in range(len(json_blob), 0, -1):
                if json_blob[end - 1] == "}":
                    try:
                        return var_name, json.loads(json_blob[:end])
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        print(f"[warn] Could not parse JSON for {var_name}: {e}")
        return var_name, None


def main():
    html = load_mhtml_as_html(r"C:\Users\hiren.chauhan\Desktop\HirenGit\newegg\newegg.mhtml")
    selector = Selector(text=html)

    script_data = selector.xpath(
        '//*[contains(text(),"GiftCardStyleList")]/text()'
    ).getall()

    results = {}
    for raw in script_data:
        cleaned = clean_text(raw)
        var_name, parsed = extract_js_object(cleaned)
        if var_name:
            results[var_name] = parsed if parsed is not None else cleaned
        elif cleaned:
            # Fallback: keep raw cleaned text if we couldn't parse it
            results.setdefault("_unparsed", []).append(cleaned)

    with open(r"C:\Users\hiren.chauhan\Desktop\HirenGit\newegg\cleaned_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("Cleaned & parsed data saved to output.json")


if __name__ == "__main__":
    main()