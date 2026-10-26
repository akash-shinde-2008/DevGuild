import time
from supabase import create_client

# Replace with your actual credentials
SUPABASE_URL = "https://vbhxgcxwfjzwkamzgqhi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZiaHhnY3h3Zmp6d2thbXpncWhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI5ODIyMzAsImV4cCI6MjEwODU1ODIzMH0.vTPjnXksTFxpv1JCSfGRkyJ5d03v5WOVNUUqhjlu1ZQ"

client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 55)
print("📡 DEVGUILD TERMINAL MONITOR ACTIVE")
print("Listening for new profile publications from the UI...")
print("=" * 55)

# Fetch existing IDs so we only alert on new ones
try:
    initial_res = client.table("freelance_profiles").select("id").execute()
    known_ids = {record["id"] for record in initial_res.data}
except Exception as e:
    print(f"Failed to connect: {e}")
    known_ids = set()

while True:
    try:
        # Check for updates every 3 seconds
        res = client.table("freelance_profiles").select("*").execute()
        
        for record in res.data:
            if record["id"] not in known_ids:
                known_ids.add(record["id"])
                
                print("\n" + "🟢 NEW PROFILE PUBLISHED VIA UI!")
                print(f"Name   : {record.get('name', 'Unknown')}")
                print(f"Role   : {record.get('role', 'Developer')}")
                print(f"GitHub : {record.get('github_url', 'N/A')}")
                print(f"Skills : {', '.join(record.get('skills', []))}")
                print("-" * 55)
                
        time.sleep(3)
    except Exception:
        # Silently retry on temporary network drops
        time.sleep(5)