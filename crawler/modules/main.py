from .reader import read_keywords_from_file
from .crawler import crawl_keyword
from .utils import print_result, find_specific_blog
from .config import KEYWORD_FILE, TARGET_BLOG_URL

def run():
    keywords = read_keywords_from_file(KEYWORD_FILE)
    for kw in keywords:
        results = crawl_keyword(kw)
        print_result(kw, results)
        find_specific_blog(results, TARGET_BLOG_URL)

if __name__ == "__main__":
    run()
