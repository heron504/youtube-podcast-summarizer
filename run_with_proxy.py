"""
Run system with proxy - optimized version
"""
import os
import sys
from datetime import datetime

# Set proxy environment variables at startup
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_optimized():
    """Run the system with optimizations"""
    print("YouTube Podcast Summarizer - Proxy Optimized")
    print("=" * 50)

    try:
        from main import YouTubePodcastSummarizer

        app = YouTubePodcastSummarizer()

        # Initialize components
        if not app.initialize_components():
            print("Failed to initialize components")
            return

        print("Components initialized successfully!")
        print("Processing will take several minutes...")
        print("Press Ctrl+C to stop if needed")

        # Run the process
        app.process_daily_summaries()

        print("=" * 50)
        print("Processing completed!")
        print("Check your email and reports/ directory for results.")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_optimized()