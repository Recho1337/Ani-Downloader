"""
Search functionality for AnimeKai
"""
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import cloudscraper

def search_anime(query: str, max_results: int = 20) -> List[Dict[str, str]]:
    """
    Search for anime on AnimeKai
    Returns list of anime with name, url, and image
    """
    try:
        scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "desktop": True}
        )
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "Referer": "https://anikai.to/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "sec-ch-ua": '"Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "upgrade-insecure-requests": "1"
        }
        
        # AnimeKai search URL
        search_url = f"https://anikai.to/browser?keyword={query}"
        
        response = scraper.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Debug: Print some of the HTML to see structure
        print(f"Response status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        # Try multiple possible selectors
        anime_items = (
            soup.select('.anime-item') or 
            soup.select('.film_list-wrap .flw-item') or 
            soup.select('.block_area-content .item') or
            soup.select('article') or
            soup.select('.anime-card') or
            soup.select('[class*="anime"]') or
            soup.select('[class*="item"]')
        )
        
        print(f"Found {len(anime_items)} potential items")
        
        seen_urls = set()
        
        for item in anime_items[:max_results * 2]:  # Check more items to account for duplicates
            try:
                # Try multiple selector patterns
                link_elem = (
                    item.select_one('a[href*="/watch/"]') or
                    item.select_one('a[href*="/anime/"]') or
                    item.select_one('a.film-poster-ahref') or
                    item.select_one('.film-name a') or
                    item.select_one('a')
                )
                
                title_elem = (
                    item.select_one('.film-name') or
                    item.select_one('.title') or
                    item.select_one('h3') or
                    item.select_one('.anime-name') or
                    item.select_one('[class*="title"]')
                )
                
                img_elem = item.select_one('img')
                
                if link_elem:
                    anime_url = link_elem.get('href', '')
                    if not anime_url.startswith('http'):
                        anime_url = f"https://anikai.to{anime_url}"
                    
                    # Skip duplicates
                    if anime_url in seen_urls:
                        continue
                    
                    seen_urls.add(anime_url)
                    
                    anime_title = title_elem.get_text(strip=True) if title_elem else link_elem.get_text(strip=True)
                    anime_img = img_elem.get('src', '') or img_elem.get('data-src', '') if img_elem else ''
                    
                    if anime_title and anime_url:
                        results.append({
                            'title': anime_title,
                            'url': anime_url,
                            'image': anime_img,
                            'anime_id': anime_url.split('/')[-1] if anime_url else ''
                        })
                        print(f"Found: {anime_title}")
                        
                        # Stop once we have enough unique results
                        if len(results) >= max_results:
                            break
            except Exception as e:
                print(f"Error parsing anime item: {e}")
                continue
        
        print(f"Total results: {len(results)}")
        return results
        
    except Exception as e:
        print(f"Search error: {e}")
        import traceback
        traceback.print_exc()
        return []
