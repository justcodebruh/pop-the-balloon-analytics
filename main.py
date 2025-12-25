#!/usr/bin/env python3
"""
YouTube Comment Analytics - Pop the Balloon
Scrapes comments from the latest episode and exports to CSV
"""

import os
import csv
import logging
from typing import Optional, List, Dict
from googleapiclient.discovery import build

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
API_KEY_FILE = 'api_key.txt'
OUTPUT_CSV = 'pop_the_balloon_comments.csv'
CHANNEL_QUERY = 'Pop the Balloon'
CHANNEL_OWNER = 'Arlette Amuli'


class YouTubeCommentScraper:
    def __init__(self):
        self.youtube = None
        self.api_key = self.load_api_key()
        self.authenticate()

    def load_api_key(self) -> str:
        """Load API key from file"""
        if not os.path.exists(API_KEY_FILE):
            raise FileNotFoundError(
                f"{API_KEY_FILE} not found. "
                "Create it with your YouTube Data API key from Google Cloud Console."
            )
        with open(API_KEY_FILE, 'r') as f:
            key = f.read().strip()
        if not key:
            raise ValueError("API key file is empty")
        return key

    def authenticate(self) -> None:
        """Authenticate with YouTube API using API key"""
        logger.info("Authenticating with YouTube API key...")
        self.youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=self.api_key
        )
        logger.info("Authentication successful")

    def find_channel(self, channel_name: str) -> Optional[str]:
        """Search for a channel and return its ID"""
        logger.info(f"Searching for channel: {channel_name}")
        try:
            request = self.youtube.search().list(
                q=channel_name,
                type='channel',
                part='snippet',
                maxResults=5
            )
            response = request.execute()

            if not response.get('items'):
                logger.error(f"No channels found matching '{channel_name}'")
                return None

            # Log found channels for verification
            logger.info("Found channels:")
            for i, item in enumerate(response['items'], 1):
                channel_title = item['snippet']['title']
                channel_id = item['id']['channelId']
                logger.info(f"  {i}. {channel_title} (ID: {channel_id})")

            # Return first result (user can verify it's correct)
            channel_id = response['items'][0]['id']['channelId']
            logger.info(f"Using channel: {response['items'][0]['snippet']['title']}")
            return channel_id

        except Exception as e:
            logger.error(f"Error searching for channel: {e}")
            return None

    def get_latest_video(self, channel_id: str) -> Optional[str]:
        """Get the latest video ID from a channel"""
        logger.info(f"Fetching latest video from channel {channel_id}")
        try:
            request = self.youtube.search().list(
                channelId=channel_id,
                type='video',
                part='snippet',
                maxResults=1,
                order='date'
            )
            response = request.execute()

            if not response.get('items'):
                logger.error("No videos found in channel")
                return None

            video_id = response['items'][0]['id']['videoId']
            video_title = response['items'][0]['snippet']['title']
            logger.info(f"Latest video: {video_title} (ID: {video_id})")
            return video_id

        except Exception as e:
            logger.error(f"Error fetching latest video: {e}")
            return None

    def fetch_comments(self, video_id: str) -> List[Dict]:
        """Fetch all comments from a video with pagination"""
        logger.info(f"Fetching comments from video {video_id}")
        comments = []
        page_token = None
        page_count = 0
        total_comments = 0

        try:
            while True:
                page_count += 1
                logger.info(f"Fetching page {page_count}...")

                request = self.youtube.commentThreads().list(
                    videoId=video_id,
                    part='snippet',
                    maxResults=100,  # Maximum allowed per request
                    pageToken=page_token,
                    textFormat='plainText'
                )
                response = request.execute()

                for item in response.get('items', []):
                    snippet = item['snippet']['topLevelComment']['snippet']
                    comment = {
                        'author_name': snippet.get('authorDisplayName', ''),
                        'likes': snippet.get('likeCount', 0),
                        'reply_count': item['snippet'].get('replyCount', 0),
                        'comment_text': snippet.get('textDisplay', '')
                    }
                    comments.append(comment)
                    total_comments += 1

                # Check if there are more pages
                page_token = response.get('nextPageToken')
                if not page_token:
                    break

            logger.info(f"Total comments fetched: {total_comments} across {page_count} pages")
            return comments

        except Exception as e:
            logger.error(f"Error fetching comments: {e}")
            return comments

    def export_to_csv(self, comments: List[Dict], output_file: str = OUTPUT_CSV) -> None:
        """Export comments to CSV file"""
        if not comments:
            logger.warning("No comments to export")
            return

        logger.info(f"Exporting {len(comments)} comments to {output_file}")
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['author_name', 'likes', 'reply_count', 'comment_text']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                writer.writerows(comments)

            logger.info(f"CSV export successful: {output_file}")

        except Exception as e:
            logger.error(f"Error writing CSV file: {e}")
            raise

    def print_summary(self, comments: List[Dict]) -> None:
        """Print summary statistics"""
        if not comments:
            logger.info("No comments to summarize")
            return

        total_likes = sum(c['likes'] for c in comments)
        total_replies = sum(c['reply_count'] for c in comments)
        avg_likes = total_likes / len(comments) if comments else 0
        max_likes = max(c['likes'] for c in comments) if comments else 0
        max_likes_comment = next(
            (c for c in comments if c['likes'] == max_likes), None
        )

        logger.info("\n" + "="*60)
        logger.info("SUMMARY STATISTICS")
        logger.info("="*60)
        logger.info(f"Total Comments: {len(comments)}")
        logger.info(f"Total Likes: {total_likes}")
        logger.info(f"Total Replies: {total_replies}")
        logger.info(f"Average Likes per Comment: {avg_likes:.2f}")
        logger.info(f"Most Liked Comment: {max_likes} likes")
        if max_likes_comment:
            text_preview = max_likes_comment['comment_text'][:60] + "..."
            logger.info(f"  By: {max_likes_comment['author_name']}")
            logger.info(f"  Text: {text_preview}")
        logger.info("="*60 + "\n")

    def run(self) -> None:
        """Execute the full workflow"""
        logger.info("Starting YouTube Comment Analytics...")

        # Step 1: Find channel
        channel_id = self.find_channel(CHANNEL_QUERY)
        if not channel_id:
            logger.error("Failed to find channel")
            return

        # Step 2: Get latest video
        video_id = self.get_latest_video(channel_id)
        if not video_id:
            logger.error("Failed to get latest video")
            return

        # Step 3: Fetch comments
        comments = self.fetch_comments(video_id)
        if not comments:
            logger.warning("No comments retrieved")
            return

        # Step 4: Export to CSV
        self.export_to_csv(comments)

        # Step 5: Print summary
        self.print_summary(comments)

        logger.info("Workflow completed successfully")


def main():
    try:
        scraper = YouTubeCommentScraper()
        scraper.run()
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == '__main__':
    main()
