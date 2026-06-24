"""
TakeMeter — Reddit Scraper (Fixed Version)
Chạy trên máy tính của bạn: python scrape_reddit.py
Không cần API key.
"""

import requests
import csv
import time
import random

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
})

def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            r = SESSION.get(url, timeout=15)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f"  Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  HTTP {r.status_code} for {url}")
                return None
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(5)
    return None

def get_posts(subreddit, sort="hot", limit=25, after=None):
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}&raw_json=1"
    if after:
        url += f"&after={after}"
    data = fetch(url)
    if not data:
        return [], None
    children = data["data"]["children"]
    after_token = data["data"]["after"]
    return children, after_token

def get_comments_from_post(subreddit, post_id):
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json?limit=50&depth=1&raw_json=1"
    data = fetch(url)
    if not data or len(data) < 2:
        return []
    
    comments = []
    for child in data[1]["data"]["children"]:
        if child["kind"] != "t1":
            continue
        body = child["data"].get("body", "").strip()
        score = child["data"].get("score", 0)
        
        # filters
        if body in ("[deleted]", "[removed]", ""):
            continue
        if len(body) < 40:        # too short
            continue
        if len(body) > 2000:      # too long
            continue
        if score < 3:             # low quality
            continue
        
        comments.append({
            "text": body.replace("\n", " ").strip(),
            "label": "",
            "notes": "",
            "source": f"r/{subreddit}",
            "reddit_url": f"https://reddit.com/r/{subreddit}/comments/{post_id}/"
        })
    return comments

def scrape_subreddit(subreddit, target=150):
    collected = []
    seen = set()
    sorts = ["hot", "top", "controversial", "new"]
    
    for sort in sorts:
        if len(collected) >= target:
            break
        print(f"\n  Sort: {sort}")
        after = None
        
        for page in range(8):
            if len(collected) >= target:
                break
            
            posts, after = get_posts(subreddit, sort=sort, limit=25, after=after)
            if not posts:
                break
            
            print(f"    Page {page+1}: {len(posts)} posts found")
            
            for post in posts:
                if len(collected) >= target:
                    break
                
                post_data = post["data"]
                post_id = post_data["id"]
                
                # also grab the post selftext if it has one
                selftext = post_data.get("selftext", "").strip()
                if selftext and len(selftext) > 60 and selftext not in ("[deleted]", "[removed]"):
                    key = selftext[:80]
                    if key not in seen:
                        seen.add(key)
                        collected.append({
                            "text": selftext.replace("\n", " ").strip()[:800],
                            "label": "",
                            "notes": "",
                            "source": f"r/{subreddit}",
                            "reddit_url": f"https://reddit.com/r/{subreddit}/comments/{post_id}/"
                        })
                
                # grab comments
                comments = get_comments_from_post(subreddit, post_id)
                for c in comments:
                    key = c["text"][:80]
                    if key not in seen:
                        seen.add(key)
                        collected.append(c)
                
                print(f"      Post {post_id}: +{len(comments)} comments | Total: {len(collected)}")
                time.sleep(random.uniform(1.0, 2.0))
            
            if not after:
                break
            time.sleep(2)
    
    return collected

def main():
    print("🎬 TakeMeter Reddit Scraper (Fixed)")
    print("=" * 45)
    
    all_comments = []
    
    for sub in ["TrueFilm", "television"]:
        print(f"\n📡 Scraping r/{sub}...")
        comments = scrape_subreddit(sub, target=160)
        all_comments.extend(comments)
        print(f"  ✅ Got {len(comments)} from r/{sub}")
        time.sleep(3)
    
    # Save
    filename = "reddit_raw.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text","label","notes","source","reddit_url"])
        writer.writeheader()
        writer.writerows(all_comments)
    
    print(f"\n✅ Saved {len(all_comments)} rows to {filename}")
    print("\n📝 NEXT STEP:")
    print("  Open reddit_raw.csv in Excel or Google Sheets")
    print("  Fill in the 'label' column for each row:")
    print("    analysis  = structured argument with specific scenes/techniques")
    print("    reaction  = immediate emotion, little/no argument")  
    print("    hot_take  = bold opinion, no real evidence")
    print("  Delete rows that are news/questions/off-topic")
    print("  Target: ~70 per label (210 total)")

if __name__ == "__main__":
    main()