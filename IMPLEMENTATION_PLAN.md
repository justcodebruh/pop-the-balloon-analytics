# YouTube Comment Analytics - Implementation Plan

## Project Goal
Scrape YouTube comment analytics from the latest episode of "Pop the Balloon" by Arlette Amuli and organize data into CSV files containing author name, likes, reply count, and comment text.

## Approach: YouTube Data API v3

### Why YouTube Data API
- Official, reliable method to access YouTube data
- Free tier supports reasonable usage quotas
- No terms of service violations
- More stable than DOM scraping

---

## Phase 1: Setup & Configuration

### Prerequisites
- Go 1.19+
- Google Cloud Project with YouTube Data API v3 enabled
- OAuth 2.0 credentials (or API key for read-only access)

### Required Go Libraries
```
google.golang.org/api/youtube/v3
google.golang.org/oauth2
google.golang.org/oauth2/google
encoding/csv
```

### Installation
```bash
go get google.golang.org/api/youtube/v3
go get google.golang.org/oauth2
go get google.golang.org/oauth2/google
```

### Google Cloud Setup
1. Create new project in Google Cloud Console
2. Enable YouTube Data API v3
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials as `credentials.json`
5. Place in project root or specify path in code

---

## Phase 2: Implementation Steps

### Step 1: Initialize Project
- Create `main.go`
- Set up package structure
- Define configuration struct for API credentials

### Step 2: Authentication
- Implement OAuth 2.0 flow
- Cache token locally to avoid re-authentication
- Handle token refresh

### Step 3: Find Channel
- Search for "Pop the Balloon" channel by Arlette Amuli
- Extract channel ID
- Verify correct channel

### Step 4: Get Latest Video
- List videos from channel (sorted by newest first)
- Extract video ID from latest episode

### Step 5: Fetch Comments
- Use `commentThreads.list()` endpoint
- Iterate through paginated results
- Extract for each comment:
  - Author name (snippet.authorDisplayName)
  - Likes (snippet.likeCount)
  - Reply count (snippet.replyCount)
  - Comment text (snippet.textDisplay)

### Step 6: Data Organization
- Store comments in structured format
- Handle pagination (max 100 per request)
- Accumulate all comments in memory or stream to CSV

### Step 7: CSV Export
- Create output CSV file: `pop_the_balloon_comments.csv`
- Columns: `author_name,likes,reply_count,comment_text`
- Write all comments to file
- Handle special characters and escaping

### Step 8: Logging & Error Handling
- Log API calls and pagination progress
- Handle rate limits gracefully
- Report total comments retrieved

---

## Phase 3: Data Structure

### Comment Struct
```go
type Comment struct {
    AuthorName string
    Likes      int64
    ReplyCount int64
    Text       string
}
```

### Output CSV Format
```
author_name,likes,reply_count,comment_text
"John Doe",42,3,"Great video!"
"Jane Smith",15,1,"Love this content"
```

---

## Phase 4: Execution Flow

1. Load credentials from `credentials.json`
2. Authenticate with Google OAuth 2.0
3. Search for "Pop the Balloon" channel
4. Fetch latest video from channel
5. Iterate through all comment threads
6. Collect comment metadata
7. Write to CSV file
8. Print summary statistics (total comments, likes range, etc.)

---

## Phase 5: Error Handling

- API quota exceeded → inform user, can retry after quota reset
- Network errors → retry with backoff
- Invalid channel/video → clear error message
- CSV write failures → panic with details

---

## Phase 6: Optional Enhancements (Future)

- Filter comments by date range
- Sort comments by likes or recency
- Include replies in separate CSV
- Generate analytics (avg likes, most liked comment, etc.)
- Support multiple channels
- Concurrent API requests for faster processing

---

## Files to Create

- `main.go` - Main application logic
- `credentials.json` - Google OAuth credentials (not committed)
- `pop_the_balloon_comments.csv` - Output file
- `go.mod` & `go.sum` - Dependency management

---

## Testing Checklist

- [ ] OAuth authentication works
- [ ] Correct channel identified
- [ ] Latest video found correctly
- [ ] Comments fetched with pagination
- [ ] CSV file created with proper formatting
- [ ] Special characters handled correctly
- [ ] All fields populated accurately
