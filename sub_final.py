import requests
import isodate

API_KEY = "YOUR_API_KEY"
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

# Junk content to block
BLOCKED_KEYWORDS = [
    "asmr", "funny", "meme", "prank", "edit", "remix", "challenge",
    "cartoon", "animation", "anime", "illusion", "compilation", "dj", "beats", "shortfilm", "reaction",
    "interview", "celebrity", "bollywood", "hollywood", "gossip",
    "actor", "actress", "rumor", "news"
]

def is_clean(title, description):
    text = (title + " " + description).lower()
    return not any(b in text for b in BLOCKED_KEYWORDS)


def build_query(topic):
    topic = topic.lower().strip()

    # Special AI handling
    if topic == "ai":
        return (
            "ai artificial intelligence ai update ai news ai tools "
            "machine learning openai chatgpt deep learning ai tech"
        )

    # Special MOVIE handling → remove gossip/news
    if topic == "movie" or topic == "movies":
        return (
        "action movie scene action scene intense scene thriller scene "
        "movie clip movie clips movie scene fight scene battle scene "
        "cinematic scene dramatic scene emotional scene serious scene "
        "best movie scene top movie scenes powerful scene iconic scene "
        "high tension scene suspense scene dramatic movie moment "
        "new movie scene latest movie clip latest movie scene"
    )

    # Normal topic
    return topic


def get_top_shorts(topic, max_results=50):

    query = build_query(topic)

    params = {
        "part": "snippet",
        "q": query,
        "maxResults": max_results,
        "type": "video",
        "order": "viewCount",  # First filter trending
        "key": "YOUR_API_KEY"
    }

    data = requests.get(SEARCH_URL, params=params).json()
    if "items" not in data:
        return []

    video_ids = [item["id"]["videoId"] for item in data["items"]]

    details_params = {
        "part": "snippet,contentDetails,statistics",
        "id": ",".join(video_ids),
        "key": "YOUR_API_KEY"
    }

    video_data = requests.get(VIDEO_URL, params=details_params).json()

    results = []

    for v in video_data.get("items", []):

        title = v["snippet"]["title"]
        desc = v["snippet"]["description"]
        views = int(v["statistics"].get("viewCount", 0))
        video_id = v["id"]

        # Shorts filter
        duration = isodate.parse_duration(v["contentDetails"]["duration"]).total_seconds()
        if duration > 60:
            continue

        # Junk removal
        if not is_clean(title, desc):
            continue

        url = f"https://www.youtube.com/shorts/{video_id}"
        results.append((title, views, url))

    # Final sorting to guarantee top 5 highest view
    results.sort(key=lambda x: x[1], reverse=True)

    return results[:5]


# Run
topic = input("Enter topic: ")
shorts = get_top_shorts(topic)

print(f"\nTop Highest View Shorts for '{topic}':\n")
if not shorts:
    print("No useful shorts found.")
else:
    for i, (title, views, url) in enumerate(shorts, 1):
        print(f"{i}. {title} — {views} views\n{url}\n")

