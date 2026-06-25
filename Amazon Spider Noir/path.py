{
    # --- Series Level Data ---
    "series_id": str, init.preparations.body.atf.state.self['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].compactGTI          # Unique alphabetic alphanumeric identifier
    "series_url": str, https://www.primevideo.com/init.preparations.body.atf.state.seasons['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'][0].seasonLink         # Full target path URL
    "title": str,  init.preparations.body.atf.state.detail.headerDetail['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].title                 # Title of the show
    "is_new_series": bool, init.preparations.body.atf.state.action.atf['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].messages.titleMetadataBadge.dvMessage.string         # True/False flag for tags like "NEW SERIES"
    "ranking": str,  init.preparations.body.atf.state.action.atf['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].messages.highValueMessage.dvMessage.string               # Category ranking information (e.g., "#1 in...")
    "synopsis": str, init.preparations.body.atf.state.detail.headerDetail['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].synopsis               # Series overview narrative
    "genres": list[str],  [
        {
            init.preparations.body.atf.state.detail.headerDetail['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].genres[0].id
            init.preparations.body.atf.state.detail.headerDetail['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].genres[0].searchLink
            init.preparations.body.atf.state.detail.headerDetail['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].genres[0].text
        }
    ]          # Dynamic list of associated genre tags
    "imdb_rating": str, init.preparations.body.atf.state.imdb['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].score/init.preparations.body.atf.state.imdb['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].maxScore            # Score string representation
    "release_year": int, init.preparations.body.atf.state.detail.headerDetail['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].releaseYear           # Production/Release calendar year
    "total_seasons_count": str, init.preparations.body.atf.strings.DV_WEB_ONE_SEASON    # Summary metadata label of available seasons

    # --- Technical & Compliance Specifications ---
    "content_advisory": list[str],  # Array of content flag strings
    "audio_languages": list[str], [init.preparations.body.atf.state.detail.headerDetail['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].audioTracks]   # Array of all available audio stream tracks
    "subtitles": list[str],  [init.preparations.body.atf.state.detail.headerDetail['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].subtitles]       # Array of all available subtitle options

    # --- Creative Production Credits ---
    "creators_and_cast": {
        "directors": list[str],[
            init.preparations.body.atf.state.detail.headerDetail['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].contributors.directors[0].name
        ]     # List of directors' full names
        "producers": list[str],  [
            init.preparations.body.atf.state.detail.headerDetail['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].contributors.producers[0].name
        ]   # List of executive/line producers
        "cast": list[str],    [
                init.preparations.body.atf.state.detail.headerDetail['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].contributors.cast[0].name
                ]      # List of main credited talent
        "studio": str, init.preparations.body.atf.state.detail.headerDetail['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].studios               # Distribution or production studio name
    },

    # --- Promotional & Media Links ---
    "trailers_and_bonus": list[{
        "title": str,  init.preparations.body.btf.state.containers['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'][0].entities[0].displayTitle             # Trailer instance title string
        "video_stream_url": str, init.preparations.body.btf.state.containers['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'][0].entities[1].link.url   # Actionable URL to play video stream
        "thumbnail_url": str, init.preparations.body.btf.state.containers['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'][0].entities[0].images.cover      # Direct image hosting link for cover item
        "content_rating": str, init.preparations.body.btf.state.containers['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'][0].entities[0].maturityRatingBadge.displayText     # Age rating tag specific to clip
        "duration": str  init.preparations.body.btf.state.containers['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'][0].entities[0].runtime           # Runtime string representation
    }],

    # --- Seasonal Breakdown & Episodic Data ---
    "seasons": list[{
        "season_label": str,  init.preparations.body.atf.strings.DV_WEB_ONE_SEASON          # Human-readable selector key (e.g., 'Season 1')
        "total_episodes_count": int, init.preparations.body.btf.state.episodeList.totalCardSize    # Total counted episodes within this specific season
        "episodes": list[{
            "episode_number": int, init.preparations.body.btf.state.detail.detail['amzn1.dv.gti.c4bd2658-32f6-460b-b9f5-b5ac66678003'].episodeNumber     # Chronological ordering counter index
            "episode_title": str,  init.preparations.body.btf.state.detail.detail['amzn1.dv.gti.c4bd2658-32f6-460b-b9f5-b5ac66678003'].title     # Custom episode specific title
            "episode_url": str,   init.preparations.body.btf.state.self['amzn1.dv.gti.773e327a-83f4-435e-a6a6-f5a007c81ad6'].link and init.preparations.body.btf.state.self['amzn1.dv.gti.773e327a-83f4-435e-a6a6-f5a007c81ad6'].sequenceNumber      # Direct navigation launch or deep play asset URL
            "thumbnail_url": str, init.preparations.body.btf.state.detail.detail['amzn1.dv.gti.c4bd2658-32f6-460b-b9f5-b5ac66678003'].images.packshot      # Direct image hosting link for frame thumbnail
            "synopsis": str,   init.preparations.body.btf.state.detail.detail['amzn1.dv.gti.c4bd2658-32f6-460b-b9f5-b5ac66678003'].synopsis         # Brief plot setup details
            "content_rating": str,   init.preparations.body.atf.state.detail.headerDetail['amzn1.dv.gti.f5b53647-e608-46ed-8228-a609fd9b2d7e'].ratingBadge.displayText   # Age classification value
            "duration": str,   init.preparations.body.btf.state.detail.detail['amzn1.dv.gti.c4bd2658-32f6-460b-b9f5-b5ac66678003'].runtime         # Total tracking watch duration value
            "release_date": str,init.preparations.body.btf.state.detail.detail['amzn1.dv.gti.c4bd2658-32f6-460b-b9f5-b5ac66678003'].releaseDate         # Regional catalog publishing string representation
        }]
    }]

}