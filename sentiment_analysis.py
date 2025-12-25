#!/usr/bin/env python3
"""
YouTube Comment Sentiment Analysis - Pop the Balloon
Analyzes comments using VADER sentiment analyzer
"""

import csv
import logging
from typing import List, Dict
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download VADER lexicon if not already present
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
INPUT_CSV = 'pop_the_balloon_comments.csv'
OUTPUT_CSV = 'pop_the_balloon_sentiment_analysis.csv'
POSITIVE_THRESHOLD = 0.05
NEGATIVE_THRESHOLD = -0.05


class SentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.comments = []
        self.analyzed_comments = []

    def load_comments(self, input_file: str = INPUT_CSV) -> bool:
        """Load comments from CSV file"""
        logger.info(f"Loading comments from {input_file}")
        try:
            with open(input_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                self.comments = list(reader)
            logger.info(f"Loaded {len(self.comments)} comments")
            return True
        except FileNotFoundError:
            logger.error(f"{input_file} not found")
            return False
        except Exception as e:
            logger.error(f"Error loading comments: {e}")
            return False

    def classify_sentiment(self, compound_score: float) -> str:
        """Classify sentiment based on compound score"""
        if compound_score > POSITIVE_THRESHOLD:
            return 'Positive'
        elif compound_score < NEGATIVE_THRESHOLD:
            return 'Negative'
        else:
            return 'Neutral'

    def analyze_comments(self) -> None:
        """Analyze sentiment for each comment"""
        logger.info("Analyzing sentiment for comments...")
        for i, comment in enumerate(self.comments, 1):
            if i % 500 == 0:
                logger.info(f"Processed {i}/{len(self.comments)} comments")

            comment_text = comment.get('comment_text', '')
            scores = self.sia.polarity_scores(comment_text)

            analyzed = {
                'author_name': comment.get('author_name', ''),
                'comment_text': comment_text,
                'likes': comment.get('likes', 0),
                'reply_count': comment.get('reply_count', 0),
                'positive_score': round(scores['pos'], 4),
                'negative_score': round(scores['neg'], 4),
                'neutral_score': round(scores['neu'], 4),
                'compound_score': round(scores['compound'], 4),
                'sentiment': self.classify_sentiment(scores['compound'])
            }
            self.analyzed_comments.append(analyzed)

        logger.info(f"Completed sentiment analysis for {len(self.analyzed_comments)} comments")

    def export_to_csv(self, output_file: str = OUTPUT_CSV) -> None:
        """Export analyzed comments to CSV"""
        if not self.analyzed_comments:
            logger.warning("No analyzed comments to export")
            return

        logger.info(f"Exporting {len(self.analyzed_comments)} analyzed comments to {output_file}")
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'author_name',
                    'sentiment',
                    'compound_score',
                    'positive_score',
                    'negative_score',
                    'neutral_score',
                    'likes',
                    'reply_count',
                    'comment_text'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.analyzed_comments)

            logger.info(f"CSV export successful: {output_file}")
        except Exception as e:
            logger.error(f"Error writing CSV file: {e}")
            raise

    def print_summary(self) -> None:
        """Print summary statistics"""
        if not self.analyzed_comments:
            logger.info("No comments to summarize")
            return

        # Calculate sentiment distribution
        sentiment_counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
        sentiment_likes = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
        sentiment_replies = {'Positive': 0, 'Negative': 0, 'Neutral': 0}

        for comment in self.analyzed_comments:
            sentiment = comment['sentiment']
            sentiment_counts[sentiment] += 1
            sentiment_likes[sentiment] += int(comment['likes'])
            sentiment_replies[sentiment] += int(comment['reply_count'])

        total_comments = len(self.analyzed_comments)
        total_likes = sum(int(c['likes']) for c in self.analyzed_comments)
        total_replies = sum(int(c['reply_count']) for c in self.analyzed_comments)
        avg_compound = sum(c['compound_score'] for c in self.analyzed_comments) / total_comments

        logger.info("\n" + "="*70)
        logger.info("SENTIMENT ANALYSIS SUMMARY")
        logger.info("="*70)
        logger.info(f"Total Comments Analyzed: {total_comments}")
        logger.info(f"Total Likes: {total_likes}")
        logger.info(f"Total Replies: {total_replies}")
        logger.info(f"Average Compound Sentiment Score: {avg_compound:.4f}")
        logger.info("")
        logger.info("SENTIMENT DISTRIBUTION:")
        logger.info("-" * 70)

        for sentiment in ['Positive', 'Negative', 'Neutral']:
            count = sentiment_counts[sentiment]
            percentage = (count / total_comments * 100) if total_comments > 0 else 0
            avg_likes = (sentiment_likes[sentiment] / count if count > 0 else 0)
            avg_replies = (sentiment_replies[sentiment] / count if count > 0 else 0)

            logger.info(f"{sentiment:12} | Count: {count:5} ({percentage:5.2f}%) | "
                       f"Avg Likes: {avg_likes:6.2f} | Avg Replies: {avg_replies:6.2f}")

        logger.info("="*70 + "\n")

    def run(self) -> None:
        """Execute the full workflow"""
        logger.info("Starting Sentiment Analysis...")

        if not self.load_comments():
            return

        self.analyze_comments()
        self.export_to_csv()
        self.print_summary()

        logger.info("Workflow completed successfully")


def main():
    try:
        analyzer = SentimentAnalyzer()
        analyzer.run()
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == '__main__':
    main()
