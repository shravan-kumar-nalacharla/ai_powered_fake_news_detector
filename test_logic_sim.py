def detect_category(text):
    t = text.lower()
    breaking_kw = ["died", "dead", "killed", "passes away", "crash", "happening"]
    if any(x in t for x in breaking_kw): return "BREAKING"
    political_kw = ["minister", "election", "pawar", "modi"]
    if any(x in t for x in political_kw): return "POLITICAL"
    return "GENERAL"

def authority(url, category="GENERAL"):
    d = url
    wiki = "wikipedia.org"
    news = ["reuters", "ndtv", "bbc"]
    
    is_wiki = wiki in d
    is_news = any(x in d for x in news)

    if category in ["BREAKING", "POLITICAL"]:
        if is_news: return 0.95
        if is_wiki: return 0.5
    else: # GENERAL
        if is_wiki: return 1.0
        if is_news: return 0.8
    return 0.3

# Test Cases
queries = [
    ("Ajit Pawar dies", "ndtv.com", "wikipedia.org"),
    ("Who is Ajit Pawar", "wikipedia.org", "ndtv.com")
]

for q, url1, url2 in queries:
    cat = detect_category(q)
    score1 = authority(url1, cat)
    score2 = authority(url2, cat)
    print(f"Query: '{q}' -> Category: {cat}")
    print(f"  Url: {url1} -> Score: {score1}")
    print(f"  Url: {url2} -> Score: {score2}")
