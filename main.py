import sys
from app.fpl import FPLClient
from app.scraper import collect_posts
from app.recommender import generate_recommendations
from app.formatter import format_markdown_digest

def run_once():
    fpl = FPLClient()
    posts = collect_posts()  # tweets/posts list
    data = fpl.load_bootstrap()
    recs = generate_recommendations(posts=posts, fpl_bootstrap=data)
    print(format_markdown_digest(recs))

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "once"
    run_once()
