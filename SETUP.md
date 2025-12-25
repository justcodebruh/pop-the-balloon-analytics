# Setup Instructions

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Get YouTube Data API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the **YouTube Data API v3**:
   - Search for "YouTube Data API v3" in the console
   - Click "Enable"
4. Create an API key:
   - Go to Credentials → Create Credentials → API Key
   - Copy the API key
5. Create `api_key.txt` in the project root and paste your API key (just the key, nothing else)

## 3. Run the Script

```bash
python main.py
```

The script will:
- Load API key from `api_key.txt`
- Search for "Pop the Balloon" channel
- Get the latest episode
- Fetch all comments with pagination
- Export to `pop_the_balloon_comments.csv`
- Print summary statistics

## Output

The script creates `pop_the_balloon_comments.csv` with columns:
- `author_name` - Comment author's display name
- `likes` - Number of likes on the comment
- `reply_count` - Number of replies to the comment
- `comment_text` - Full text of the comment
