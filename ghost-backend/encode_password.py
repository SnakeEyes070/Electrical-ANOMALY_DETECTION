# encode_password.py
import urllib.parse

# Your password
password = "Kyv8bP9XXT1BJKUx"

# URL encode the password
encoded_password = urllib.parse.quote_plus(password)

print(f"Original password: {password}")
print(f"URL encoded password: {encoded_password}")

# Full URL
url = f"mongodb+srv://billoreparth80_db_user:{encoded_password}ghostapi.3qe1pdk.mongodb.net/?appName=GHOSTapi"
print(f"\nFull URL: {url}")