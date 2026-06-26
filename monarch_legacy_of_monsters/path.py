{
    # --- Series Level Data ---
    "series_id": str, data[1].data.shelves[0].items[0].buttons[0].action.actionMetrics.data[0].fields.canonicalId             # Unique alphabetic alphanumeric identifier
    "series_url": str,   data[1].data.canonicalURL           # Full target path URL
    "title": str,  data[1].data.shelves[0].items[0].title                 # Title of the show
    "is_new_series": bool,          # True/False flag for tags like "NEW SERIES"
    "ranking": str,                 # Category ranking information (e.g., "#1 in...")
    "synopsis": str, data[1].data.shelves[0].items[0].description         # Series overview narrative
    "genres": list[str],  data[1].data.shelves[7].items[0].genres          # Dynamic list of associated genre tags
    "imdb_rating": str,             # Score string representation
    "release_year": int, data[1].data.shelves[8].items[0].items[0].info        # Production/Release calendar year
    "total_seasons_count": str, data[1].data.shelves[1].header.seasons[0].seasonNumber in this you check how many seson is here    # Summary metadata label of available seasons

    # --- Technical & Compliance Specifications ---
    "content_advisory": list[str],  # Array of content flag strings
    "audio_languages": list[str], data[1].data.shelves[2].playlistItems[0].playable.audioTrackLocales[0].displayName  # Array of all available audio stream tracks
    "subtitles": list[str],  data[1].data.shelves[2].playlistItems[0].playable.locales[16].hasSubtitles if this is true then fetch data[1].data.shelves[2].playlistItems[0].playable.locales[16].displayName this data       # Array of all available subtitle options

    # --- Creative Production Credits ---
    "creators_and_cast": {
        "directors": list[str],     # List of directors' full names
        "producers": list[str], in this data[1].data.shelves[5].items[0].subtitle == "Executive Producer" then fetch data of this path data[1].data.shelves[5].items[10].title     # List of executive/line producers
        "cast": list[str],   in this data[1].data.shelves[5].items[0].subtitle != "Executive Producer" then fetch data of this path data[1].data.shelves[5].items[10].title       # List of main credited talent
        "studio": str               # Distribution or production studio name
    },

    # --- Promotional & Media Links ---
    "trailers_and_bonus": list[{
        "title": str, data[1].data.shelves[2].items[2].contextAction.title          # Trailer instance title string
        "video_stream_url": str, data[1].data.shelves[2].items[3].contextAction.url   # Actionable URL to play video stream
        "thumbnail_url": str,   data[1].data.shelves[2].playlistItems[0].playlist.tabData.artwork.template    # Direct image hosting link for cover item
        "content_rating": str, None     # Age rating tag specific to clip
        "duration": str data[1].data.shelves[2].items[2].metadata          # Runtime string representation
    }],

    # --- Seasonal Breakdown & Episodic Data ---
    "seasons": list[{
        "season_label": str,  data[1].data.shelves[1].header.seasons[0].title       # Human-readable selector key (e.g., 'Season 1')
        "total_episodes_count": int, data[1].data.shelves[1].header.seasons[0].episodeCount   # Total counted episodes within this specific season
        "episodes": list[{
            "episode_number": int, data[1].data.shelves[1].items[6].tag      # Chronological ordering counter index
            "episode_title": str, data[1].data.shelves[1].items[6].title      # Custom episode specific title
            "episode_url": str,  data[1].data.shelves[1].items[5].contextAction.url       # Direct navigation launch or deep play asset URL
            "thumbnail_url": str, data[1].data.shelves[1].items[5].artwork.template also format this type ""template": "https://is1-ssl.mzstatic.com/image/thumb/r1heTTebrcs3xunpqHVwGg/{w}x{h}KF.TVALC02.{f}?color=241B0F" also cosider this parameter
                  data[1].data.shelves[1].items[5].artwork.width and data[1].data.shelves[1].items[5].artwork.height      # Direct image hosting link for frame thumbnail
            "synopsis": str, data[1].data.shelves[1].items[5].description           # Brief plot setup details
            "content_rating": str,    data[0].data.configuration.applicationProps.ratings.IN_TV.IN_TV_UA_16Plus.displayValue  # Age classification value
            "duration": str,   data[1].data.shelves[1].items[5].metadata         # Total tracking watch duration value
            "release_date": str         # Regional catalog publishing string representation
        }]
    }]
}