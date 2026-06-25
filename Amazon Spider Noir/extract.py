import os
import json

# --- 1. File Infrastructure Handler ---
def file_handler(filename, mode="r", data=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, filename)

    if mode == "r":
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    elif mode == "w":
        name, _ = os.path.splitext(filename)
        output_path = os.path.join(current_dir, f"{name}_output.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Output written to: {output_path}")
        return output_path


# --- 2. Micro-Extraction Functions ---
def extract_genres(header_detail: dict) -> list:
    try:
        genres_raw = header_detail.get("genres") or []
        return [g.get("text") for g in genres_raw if isinstance(g, dict) and g.get("text")]
    except Exception as e:
        print(f"Error parsing genres: {e}")
        return []


def extract_imdb_rating(imdb_data: dict) -> str:
    try:
        score = imdb_data.get("score")
        max_score = imdb_data.get("maxScore")
        return f"{score}/{max_score}" if score and max_score else None
    except Exception as e:
        print(f"Error parsing IMDB rating: {e}")
        return None

def extract_creators_and_cast(header_detail: dict) -> dict:
    try:
        contributors = header_detail.get("contributors") or {}
        studios_raw = header_detail.get("studios")
        
        # Safely extract the first element if it's a list, or keep it if it's already a string
        studio_string = studios_raw[0] if isinstance(studios_raw, list) and studios_raw else studios_raw
        
        return {
            "directors": [d.get("name") for d in contributors.get("directors", []) if isinstance(d, dict)],
            "producers": [p.get("name") for p in contributors.get("producers", []) if isinstance(p, dict)],
            "cast": [c.get("name") for c in contributors.get("cast", []) if isinstance(c, dict)],
            "studio": studio_string if isinstance(studio_string, str) else None
        }
    except Exception as e:
        print(f"Error parsing creators and cast: {e}")
        return {"directors": [], "producers": [], "cast": [], "studio": None}

import re

def extract_trailers_and_bonus(btf_state: dict, series_id: str) -> list:
    try:
        trailers = []
        containers = btf_state.get("containers", {}).get(series_id, [])
        
        if isinstance(containers, list) and containers:
            entities = containers[0].get("entities", []) if isinstance(containers[0], dict) else []
            
            for ent in entities:
                if isinstance(ent, dict):
                    # --- Thumbnail URL Extraction ---
                    images_data = ent.get("images")
                    raw_cover = images_data.get("cover") if isinstance(images_data, dict) else None
                    cover_img = raw_cover.get("url") if isinstance(raw_cover, dict) else raw_cover
                    
                    # --- Content Rating Extraction ---
                    badge = ent.get("maturityRatingBadge")
                    content_rating = badge.get("displayText") if isinstance(badge, dict) else ent.get("content_rating")

                    # --- Video Stream URL Extraction (From ent.link.url) ---
                    link_data = ent.get("link")
                    raw_url = link_data.get("url") if isinstance(link_data, dict) else ""
                    
                    video_url = None
                    if raw_url:
                        # Extract the alphanumeric detail ID (e.g., 0QSWZT2NXRQWO9I2EXHFU3JYF7) from the link path
                        # This matches any segment between slashes containing letters and numbers of typical ID length
                        match = re.search(r'/detail/([^/?#]+)', raw_url)
                        
                        if match:
                            extracted_id = match.group(1)
                        else:
                            # Fallback: if it's just a raw ID string without /detail/ in the raw path
                            extracted_id = raw_url.split('/')[-1].split('?')[0]
                        
                        # Format precisely as requested
                        video_url = f"https://www.primevideo.com/region/eu/detail/{extracted_id}"
                    
                    # Fallback to series_id format if everything else fails
                    if not video_url:
                        video_url = f"https://www.primevideo.com/region/eu/detail/{series_id}"

                    trailers.append({
                        "title": ent.get("displayTitle"),
                        "video_stream_url": video_url,
                        "thumbnail_url": cover_img,
                        "content_rating": content_rating,
                        "duration": ent.get("runtime")
                    })
        return trailers
    except Exception as e:
        print(f"Error parsing trailers and bonus: {e}")
        return []

def extract_seasons_and_episodes(btf_state: dict, header_detail: dict, atf_strings: dict, series_id: str) -> list:
    try:
        btf_details = btf_state.get("detail", {}).get("detail", {})
        btf_self = btf_state.get("self", {})
        rating_text = header_detail.get("ratingBadge", {}).get("displayText")
        
        episodes_list = [
            {
                "episode_number": item_data.get("episodeNumber"),
                "episode_title": item_data.get("title"),
                "episode_url": f"https://www.primevideo.com{btf_self.get(item_id, {}).get('link')}" if btf_self.get(item_id, {}).get("link") else None, 
                "thumbnail_url": item_data.get("images", {}).get("packshot") if isinstance(item_data.get("images"), dict) else None,
                "synopsis": item_data.get("synopsis"),
                "content_rating": rating_text,
                "duration": item_data.get("runtime"),
                "release_date": item_data.get("releaseDate")
            }
            for item_id, item_data in btf_details.items()
            if isinstance(item_data, dict) and item_id != series_id
        ]
        
        episodes_list.sort(key=lambda x: x["episode_number"] or 0)

        return [{
            "season_label": atf_strings.get("DV_WEB_ONE_SEASON"),
            "total_episodes_count": btf_state.get("episodeList", {}).get("totalCardSize"),
            "episodes": episodes_list
        }]
    except Exception as e:
        print(f"Error parsing seasons and episodes: {e}")
        return [] 
    
def extract_content_advisory(header_detail: dict) -> list:
    try:
        rating_badge = header_detail.get("ratingBadge")
        advisory_list = []
        if isinstance(rating_badge, dict):
            description = rating_badge.get("description")
            display_text = rating_badge.get("displayText")
            
            if description:
                advisory_list.append(description)
            if display_text and display_text != description:
                advisory_list.append(display_text)
                
        return advisory_list
    except Exception as e:
        print(f"Error parsing content advisory: {e}")
        return []


# --- 3. Main Orchestrator Function ---
def parse_prime_video_state(init_data: dict) -> dict:
    preparations = init_data.get("init", {}).get("preparations", {}).get("body", {})
    atf = preparations.get("atf", {})
    btf = preparations.get("btf", {})
    
    atf_state = atf.get("state", {})
    btf_state = btf.get("state", {})
    atf_strings = atf.get("strings", {})

    header_detail_root = atf_state.get("detail", {}).get("headerDetail", {})
    
    # Optimized dynamic ID search using generator expressions
    series_id = next((k for k in header_detail_root if k.startswith("amzn1.dv.gti.")), None)
    if not series_id:
        series_id = next((k for k in btf_state.get("containers", {}) if k.startswith("amzn1.dv.gti.")), None)
                
    if not series_id:
        print("CRITICAL: Target dynamic Series GTI ID lookup failed.")
        return {}

    header_detail = header_detail_root.get(series_id, {})
    imdb_data = atf_state.get("imdb", {}).get(series_id, {})
    action_atf = atf_state.get("action", {}).get("atf", {}).get(series_id, {})

    season_list = atf_state.get('seasons', {}).get(series_id)
    series_url = f"https://www.primevideo.com{season_list[0].get('seasonLink', '')}" if season_list and isinstance(season_list, list) else None

    return {
        "series_id": series_id,
        "series_url": series_url,
        "title": header_detail.get("title"),
        "is_new_series": bool(action_atf.get("messages", {}).get("titleMetadataBadge", {}).get("dvMessage", {}).get("string")),
        "ranking": action_atf.get("messages", {}).get("highValueMessage", {}).get("dvMessage", {}).get("string"),
        "synopsis": header_detail.get("synopsis"),
        "genres": extract_genres(header_detail),
        "imdb_rating": extract_imdb_rating(imdb_data),
        "release_year": header_detail.get("releaseYear"),
        "total_seasons_count": atf_strings.get("DV_WEB_ONE_SEASON"),
        "content_advisory": extract_content_advisory(header_detail), 
        "audio_languages": header_detail.get("audioTracks", []),
        "subtitles": header_detail.get("subtitles", []),
        "creators_and_cast": extract_creators_and_cast(header_detail),
        "trailers_and_bonus": extract_trailers_and_bonus(btf_state, series_id),
        "seasons": extract_seasons_and_episodes(btf_state, header_detail, atf_strings, series_id)
    }


# --- 4. Runtime Execution ---
if __name__ == "__main__":
    raw_data = file_handler("amazon_spider_noir.json", mode="r")
    structured_output = parse_prime_video_state(raw_data)
    file_handler("amazon_spider_noir.json", mode="w", data=structured_output)