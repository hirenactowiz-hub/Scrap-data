import json
import os
import re

# Folder this script lives in (e.g. C:\Users\hiren.chauhan\Desktop\HirenGit\monarch_legacy_of_monsters)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_1 = os.path.join(BASE_DIR, "monarch_1.json")   # episode-detail dump (Season 1, complete)
INPUT_2 = os.path.join(BASE_DIR, "monarch_2.json")   # show-page dump (series info + partial episode window)
INPUT_3 = os.path.join(BASE_DIR, "monarch_3.json")   # episode-detail dump (Season 2, complete)
OUTPUT = os.path.join(BASE_DIR, "monarch_legacy_of_monsters_output.json")

# EXISTING UTILITY FUNCTIONS

def safe_get(obj, keys, default=None):
    for key in keys:
        if isinstance(obj, dict):
            obj = obj.get(key, default)
        elif isinstance(obj, list) and isinstance(key, int):  # <-- Fixed this line
            try:
                obj = obj[key]
            except IndexError:
                return default
        else:
            return default
        if obj is default and key != keys[-1]:
            return default
    return obj

def format_image_url(template, width=None, height=None, fmt="jpg"):
    if not template:
        return None
    w = width or 3840
    h = height or 2160
    return (
        template.replace("{w}", str(w))
        .replace("{h}", str(h))
        .replace("{f}", fmt)
    )


def parse_tag_number(tag):
    if not tag:
        return None
    m = re.search(r"\d+", str(tag))
    return int(m.group(0)) if m else None


def seconds_to_minutes_label(seconds):
    if seconds is None:
        return None
    if seconds > 10000:
        seconds = seconds / 1000.0
    return f"{int(round(seconds / 60))} min"


def epoch_ms_to_date(epoch_ms):
    if epoch_ms is None:
        return None
    from datetime import datetime, timezone
    return datetime.fromtimestamp(epoch_ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")


def parse_language_string(raw):
    if not raw:
        return []
    compounds = ["Chinese, Simplified", "Chinese, Traditional", "Cantonese, Traditional"]
    placeholder_map = {}
    protected = raw
    for i, c in enumerate(compounds):
        token = f"\x00{i}\x00"
        placeholder_map[token] = c
        protected = protected.replace(c, token)

    parts = re.split(r",\s*(?![^(]*\))", protected)
    cleaned = []
    for part in parts:
        name = part.strip()
        for token, original in placeholder_map.items():
            name = name.replace(token, original)
        name = re.sub(r"\s*\((?:AD|CC|SDH)[^)]*\)\s*$", "", name).strip()
        if name and name not in cleaned:
            cleaned.append(name)
    return cleaned

# NEW MODULAR DATA EXTRACTION FUNCTIONS

def load_source_files():
    """Loads and returns the three input JSON structures."""
    with open(INPUT_1, "r", encoding="utf-8") as f:
        file1 = json.load(f)
    with open(INPUT_2, "r", encoding="utf-8") as f:
        file2 = json.load(f)
    with open(INPUT_3, "r", encoding="utf-8") as f:
        file3 = json.load(f)
    return file1, file2, file3


def parse_series_hero_info(shelves, show_intent):
    """Extracts base series identification, URLs, titles, and synopses."""
    hero = shelves[0]["items"][0]
    series_id = safe_get(hero, ["buttons", 0, "action", "actionMetrics", "data", 0, "fields", "canonicalId"])
    title = hero.get("title")
    synopsis = hero.get("description")
    series_url = show_intent.get("canonicalURL")
    return series_id, title, synopsis, series_url


def parse_genres(shelves):
    """Extracts listed genres from the About shelf."""
    about_shelf = next((s for s in shelves if s.get("$type") == "About"), None)
    return safe_get(about_shelf, ["items", 0, "genres"], []) if about_shelf else []


def parse_info_shelf_metadata(shelves, file1):
    """Parses core technical metadata like rating, languages, and release year."""
    info_shelf = next((s for s in shelves if s.get("$type") == "Info"), None)
    release_year = None
    content_rating = None
    content_advisory = []
    subtitles = []

    if info_shelf:
        groups = {g.get("title"): g for g in info_shelf.get("items", [])}
        
        # Parse Information Section
        info_group = groups.get("Information", {}).get("items", [])
        for entry in info_group:
            if entry.get("id") == "information-releaseDate":
                m = re.search(r"\d{4}", entry.get("info", ""))
                if m:
                    release_year = int(m.group(0))
            elif entry.get("id") == "information-rating":
                content_rating = entry.get("info")
            elif entry.get("id") == "information-contentRatingAdvisories":
                content_advisory = [a.strip() for a in entry.get("info", "").split(",") if a.strip()]

        # Parse Subtitles
        lang_group = groups.get("Languages", {}).get("items", [])
        for entry in lang_group:
            if entry.get("id") == "languages-subtitles":
                subtitles = parse_language_string(entry.get("info", ""))

    # Parse Audio Languages
    playables = file1.get("data", {}).get("playables", {})
    audio_set = []
    if playables:
        first_playable = next(iter(playables.values()))
        audio_set = [t.get("displayName") for t in first_playable.get("audioTrackLocales", []) if t.get("displayName")]
    
    first_ep = safe_get(file1, ["data", "episodes", 0], {})
    original_langs = first_ep.get("originalSpokenLanguages", [])
    original_lang = original_langs[0].get("displayName") if original_langs else None
    audio_languages = ([original_lang] if original_lang else []) + [l for l in audio_set if l != original_lang]

    return release_year, content_rating, content_advisory, subtitles, audio_languages


def parse_cast_and_crew(shelves_by_header_title):
    """Extracts talent lists categorized by their cast or crew role."""
    cast_shelf = shelves_by_header_title.get("Cast & Crew")
    producers = []
    cast = []
    if cast_shelf:
        for item in cast_shelf.get("items", []):
            name = item.get("title")
            role = item.get("subtitle", "")
            if not name:
                continue
            if role == "Executive Producer":
                producers.append(name)
            else:
                cast.append(name)
    return producers, cast


def parse_trailers_and_bonus(shelves_by_header_title):
    """Extracts supplementary video links and marketing materials."""
    trailers_and_bonus = []
    for shelf_name in ("Trailers", "Bonus Content"):
        shelf = shelves_by_header_title.get(shelf_name)
        if not shelf:
            continue
        for item in shelf.get("items", []):
            artwork = item.get("artwork", {})
            trailers_and_bonus.append({
                "title": safe_get(item, ["contextAction", "title"]) or item.get("title"),
                "video_stream_url": safe_get(item, ["contextAction", "url"]),
                "thumbnail_url": format_image_url(artwork.get("template"), artwork.get("width"), artwork.get("height")),
                "content_rating": None,
                "duration": item.get("metadata"),
            })
    return trailers_and_bonus


def extract_episodes(file_data):
    """Generic parser for cleaning and extraction of individual episode objects."""
    episodes = []
    file_episodes = file_data.get("data", {}).get("episodes", [])
    for ep in file_episodes:
        images = ep.get("images", {}).get("contentImage", {})
        episodes.append({
            "episode_number": ep.get("episodeNumber"),
            "episode_title": ep.get("title"),
            "episode_url": ep.get("url"),
            "thumbnail_url": format_image_url(images.get("url"), images.get("width"), images.get("height")),
            "synopsis": ep.get("description"),
            "content_rating": safe_get(ep, ["rating", "displayName"]),
            "duration": seconds_to_minutes_label(ep.get("duration")),
            "release_date": epoch_ms_to_date(ep.get("releaseDate")),
        })
    episodes.sort(key=lambda e: e["episode_number"])
    return episodes

# MAIN EXECUTION FLOW

def main():
    # 1. Load IO Data
    file1, file2, file3 = load_source_files()

    # 2. Extract layout buckets (shelves)
    show_intent = file2["data"][1]["data"]
    shelves = show_intent["shelves"]
    shelves_by_header_title = {
        safe_get(s, ["header", "title"]): s for s in shelves if safe_get(s, ["header", "title"])
    }

    # 3. Process components using modular sub-functions
    series_id, title, synopsis, series_url = parse_series_hero_info(shelves, show_intent)
    genres = parse_genres(shelves)
    release_year, content_rating, content_advisory, subtitles, audio_languages = parse_info_shelf_metadata(shelves, file1)
    producers, cast = parse_cast_and_crew(shelves_by_header_title)
    trailers_and_bonus = parse_trailers_and_bonus(shelves_by_header_title)

    # 4. Process Season Episodes (reusing the same function)
    season1_episodes = extract_episodes(file1)
    season2_episodes = extract_episodes(file3)

    # 5. Build Season Meta wrappers
    episodes_shelf = shelves_by_header_title.get("Episodes")
    seasons_meta = {s["seasonNumber"]: s for s in safe_get(episodes_shelf, ["header", "seasons"], [])} if episodes_shelf else {}

    seasons_output = []
    if season1_episodes:
        seasons_output.append({
            "season_label": seasons_meta.get(1, {}).get("title", "Season 1"),
            "total_episodes_count": len(season1_episodes),
            "episodes": season1_episodes,
        })
    if season2_episodes:
        seasons_output.append({
            "season_label": seasons_meta.get(2, {}).get("title", "Season 2"),
            "total_episodes_count": len(season2_episodes),
            "episodes": season2_episodes,
        })

    total_seasons_count = f"{len(seasons_output)} Season" + ("" if len(seasons_output) == 1 else "s")

    # 6. Build Payload Matrix
    result = {
        "series_id": series_id,
        "series_url": series_url,
        "title": title,
        "is_new_series": False,
        "ranking": None,
        "synopsis": synopsis,
        "genres": genres,
        "imdb_rating": None,
        "release_year": release_year,
        "total_seasons_count": total_seasons_count,
        "content_advisory": content_advisory,
        "audio_languages": audio_languages,
        "subtitles": subtitles,
        "creators_and_cast": {
            "directors": [], 
            "producers": producers,
            "cast": cast,
            "studio": None,  
        },
        "trailers_and_bonus": trailers_and_bonus,
        "seasons": seasons_output,
    }

    # 7. Write Results
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # 8. Print Reports
    print(f"Wrote {OUTPUT}")
    print(f"Season 1: {len(season1_episodes)} episodes | Season 2: {len(season2_episodes)} episodes")
    print(f"Trailers/Bonus: {len(trailers_and_bonus)} | Cast: {len(cast)} | Producers: {len(producers)}")
    print(f"Audio languages: {audio_languages}")


if __name__ == "__main__":
    main()