import time
import schedule
import main
from threader import generate_thread
from poster import post_thread

def run_quote_tweets():
    print("\n" + "="*50)
    print(f"[auto] 🚀 Starting scheduled Quote Tweet run...")
    try:
        main.run()
    except Exception as e:
        print(f"[auto] ❌ Error in quote tweet run: {e}")

def run_daily_thread():
    print("\n" + "="*50)
    print(f"[auto] 🧵 Starting scheduled Daily Thread run...")
    try:
        thread_data = generate_thread()
        if thread_data:
            post_thread(thread_data)
    except Exception as e:
        print(f"[auto] ❌ Error in daily thread run: {e}")

# Quote tweets 4 times a day
schedule.every().day.at("09:00").do(run_quote_tweets)
schedule.every().day.at("13:00").do(run_quote_tweets)
schedule.every().day.at("18:00").do(run_quote_tweets)
schedule.every().day.at("21:00").do(run_quote_tweets)

# Daily viral thread
schedule.every().day.at("07:30").do(run_daily_thread)

if __name__ == "__main__":
    import os
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("=======================================================")
    print("  Twitter Auto-Agent started! Leave this window open.")
    print("=======================================================")
    print("Schedule:")
    print(" - 07:30 : Post Daily Viral Thread")
    print(" - 09:00 : Quote Tweet Run")
    print(" - 13:00 : Quote Tweet Run")
    print(" - 18:00 : Quote Tweet Run")
    print(" - 21:00 : Quote Tweet Run")
    print("\nWaiting for next scheduled job...")

    while True:
        schedule.run_pending()
        time.sleep(60)
