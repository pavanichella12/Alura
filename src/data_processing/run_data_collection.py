#!/usr/bin/env python3
"""
Simple script to run the misogyny data collection
"""

from data_collector import main

if __name__ == "__main__":
    print("🚀 Starting Misogyny Data Collection...")
    print("This will scrape academic and educational sources for misogyny detection data.")
    print("=" * 60)
    
    try:
        data = main()
        print("\n✅ Data collection completed successfully!")
        print(f"📊 Collected {data['metadata']['total_scraped_items']} scraped items")
        print(f"📝 Added {data['metadata']['total_terms']} structured misogyny terms")
        print(f"💾 Data saved to: collected_misogyny_data.json")
        
    except Exception as e:
        print(f"❌ Error during data collection: {str(e)}")
        print("Please check your internet connection and try again.") 