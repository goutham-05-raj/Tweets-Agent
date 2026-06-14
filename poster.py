import os
import time
from dotenv import load_dotenv

load_dotenv()

def setup_playwright_page(p):
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1280, 'height': 800})
    
    auth_token = os.getenv("TWITTER_AUTH_TOKEN")
    if not auth_token:
        print("[poster] ❌ WARNING: TWITTER_AUTH_TOKEN in .env is missing!")
        
    context.add_cookies([{
        "name": "auth_token",
        "value": auth_token,
        "domain": ".x.com",
        "path": "/",
        "secure": True,
        "httpOnly": True
    }])
    page = context.new_page()
    return browser, page

def post_quote_tweet(quote_text: str, original_tweet_id: str, author: str = "x") -> bool:
    from playwright.sync_api import sync_playwright
    
    if original_tweet_id == "unknown":
        print("[poster] ❌ Cannot quote tweet an unknown ID. Skipping.")
        return False
        
    try:
        with sync_playwright() as p:
            browser, page = setup_playwright_page(p)
            
            # Use the exact tweet URL to open the specific tweet page
            tweet_url = f"https://x.com/{author}/status/{original_tweet_id}"
            print(f"[poster] ⏳ Opening original tweet: {tweet_url}...")
            page.goto(tweet_url, wait_until="domcontentloaded")
            
            # Wait for the tweet to load
            page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
            time.sleep(2)
            
            print("[poster] 🔄 Clicking the Repost/Quote menu...")
            # Click the retweet button on the main tweet (the first one)
            page.locator('article[data-testid="tweet"] [data-testid="retweet"]').first.click()
            time.sleep(1)
            
            print("[poster] 📝 Selecting 'Quote'...")
            # The Quote button is an anchor link to /compose/post inside the dropdown menu
            page.locator('a[role="menuitem"][href="/compose/post"]').click()
            time.sleep(2)
            
            print(f"[poster] ✍️ Typing quote text natively...")
            # Target the active composer modal
            composer = page.locator('div[role="dialog"]').filter(has=page.locator('[data-testid="tweetTextarea_0"]'))
            textarea = composer.locator('[data-testid="tweetTextarea_0"]').first
            textarea.wait_for(timeout=15000)
            textarea.click()
            time.sleep(0.5)
            
            page.keyboard.type(quote_text, delay=10)
            time.sleep(2)
            
            print("[poster] 🚀 Hitting Post...")
            with page.expect_response(lambda response: "CreateTweet" in response.url and response.status == 200, timeout=30000):
                try:
                    composer.locator('[data-testid="tweetButton"]').first.click(timeout=10000)
                except:
                    print("[poster] Warning: Click failed, using Ctrl+Enter fallback...")
                    textarea.click(force=True)
                    page.keyboard.press("Control+Enter")
            
            print("[poster] ✅ Posted native quote tweet successfully!")
            browser.close()
            return True
            
    except Exception as e:
        print(f"[poster] ❌ Failed: {e}")
        return False

def post_thread(thread_data: list) -> bool:
    from playwright.sync_api import sync_playwright
    
    posted_tweet_ids = []
    
    try:
        with sync_playwright() as p:
            browser, page = setup_playwright_page(p)
            
            for i, tweet in enumerate(thread_data):
                if i == 0:
                    print(f"[poster] ⏳ Opening home timeline for Tweet {i+1}...")
                    page.goto("https://x.com/home", wait_until="domcontentloaded")
                    try:
                        page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=10000)
                        page.click('[data-testid="SideNav_NewTweet_Button"]')
                        time.sleep(1)
                    except:
                        print("[poster] Warning: Side compose button not found.")
                else:
                    prev_id = posted_tweet_ids[-1] if posted_tweet_ids else "unknown"
                    print(f"[poster] ⏳ Opening reply window for Tweet {i+1}...")
                    page.goto(f"https://x.com/intent/tweet?in_reply_to={prev_id}", wait_until="domcontentloaded")
                    time.sleep(2)
                
                # Target the active composer modal to avoid hitting background page elements under masks
                composer = page.locator('div[role="dialog"]').filter(has=page.locator('[data-testid="tweetTextarea_0"]'))
                
                textarea = composer.locator('[data-testid="tweetTextarea_0"]').first
                textarea.wait_for(timeout=15000)
                textarea.click()
                time.sleep(0.5)
                
                print(f"[poster] ✍️ Typing thread part {i+1}...")
                page.keyboard.type(tweet["text"], delay=10)
                time.sleep(1)
                
                img_path = tweet.get("image_path")
                if img_path and os.path.exists(img_path):
                    print(f"[poster] 📸 Attaching image...")
                    composer.locator('input[data-testid="fileInput"]').first.set_input_files(img_path)
                    
                    try:
                        composer.locator('[data-testid="attachments"]').first.wait_for(timeout=30000)
                        print("[poster] 📸 Image fully uploaded and previewed.")
                    except:
                        print("[poster] Warning: Image preview didn't load in time.")
                    
                    # Give Twitter's React UI plenty of time to process the image and enable the button
                    time.sleep(5)
                        
                    try:
                        os.remove(img_path) 
                    except:
                        pass
                
                print(f"[poster] 🚀 Hitting Post for Tweet {i+1}...")
                
                with page.expect_response(lambda response: "CreateTweet" in response.url and response.status == 200, timeout=45000) as response_info:
                    try:
                        # Wait up to 20 seconds for the button to become enabled and click it
                        composer.locator('[data-testid="tweetButton"]').first.click(timeout=20000)
                    except:
                        print("[poster] Warning: Click failed, using Ctrl+Enter fallback...")
                        textarea.click(force=True)
                        page.keyboard.press("Control+Enter")
                
                response = response_info.value
                data = response.json()
                tweet_id = data['data']['create_tweet']['tweet_results']['result']['rest_id']
                posted_tweet_ids.append(tweet_id)
                print(f"[poster] 🔗 Successfully grabbed Tweet ID: {tweet_id}")
            
            print("[poster] ✅ Posted entire thread successfully via synchronized sequential replies!")
            browser.close()
            return True
            
    except Exception as e:
        print(f"[poster] ❌ Failed to post thread: {e}")
        return False
