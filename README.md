```markdown
# YouTube Video Analysis for Restaurant Robots

This project aims to gather and analyze transcripts and comments from YouTube videos related to the use of robots in restaurants. The goal is to understand public opinions and potential prejudices about digitalizing dining experiences in America compared to Asia.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Introduction

This project was created to search YouTube for videos on a specific topic, gather either the transcripts or comments of a certain number of videos, and analyze them to understand public sentiment. The focus was on researching how people feel about robots being used in restaurants, comparing the opinions in America to those in Asia.

## Features

- Search YouTube for videos on a specific topic
- Retrieve video details such as title, description, publish date, and views
- Fetch transcripts of videos and organize them with proper punctuation and capitalization
- Summarize video transcripts
- Download and summarize comments from YouTube videos
- Save data to Excel for further analysis

## Installation

To run this project, you need to have Python installed along with several libraries. Follow these steps to set up the environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/your-repository.git

# Navigate to the project directory
cd your-repository

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Transcript Analysis

This script fetches transcripts of YouTube videos and saves them along with video details to an Excel file.

```python
import os
import logging
import scrapetube
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openpyxl import Workbook, load_workbook
from langchain_community.llms import Ollama
from youtube_transcript_api import YouTubeTranscriptApi as yta

API_KEY = 'YOUR_API_KEY'
youtube = build('youtube', 'v3', developerKey=API_KEY)

llm = Ollama(base_url="http://131.123.41.132:11434", model="llava:34b")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_video_details(video_id):
    """Fetch video details such as title, description, and publish date using the YouTube Data API."""
    try:
        request = youtube.videos().list(part="snippet, statistics", id=video_id)
        response = request.execute()
        items = response.get('items', [])
        if items:
            snippet = items[0].get('snippet', {})
            statistics = items[0].get('statistics', {})
            title = snippet.get('title', '')
            description = snippet.get('description', '')
            publish_date = snippet.get('publishedAt', '')
            views = statistics.get('viewCount', '')
            return title, description, publish_date, views
    except HttpError as e:
        logging.error(f"API error for video {video_id}: {e}")
    except Exception as e:
        logging.error(f"Error fetching details for video {video_id}: {e}")
    return '', '', '', ''


def get_transcript(video_id):
    try:
        data = yta.get_transcript(video_id)
        transcript = ' '.join([val['text'] for val in data if 'text' in val])
        return transcript
    except Exception as e:
        logging.error(f"Error fetching transcript for video {video_id}: {e}")
        return ''


def organize_transcript(transcript):
    if not transcript:
        return "Transcript does not exist"

    summary_text = llm.invoke(f"""
                              edit the following video transcript with proper punctuation and capitalization:
                              "{transcript}"
                              """)
    return summary_text

def summarize_transcript(transcript):
    if not transcript:
        return "Transcript does not exist"

    summary_text = llm.invoke(f"""
                              please give me a summary of the following text:
                              "{transcript}"
                              """)
    return summary_text

def save_to_excel(data, filename='AI DataLog_Transcript_Record.xlsx'):
    """Save data to an Excel file."""
    try:
        if os.path.exists(filename):
            wb = load_workbook(filename)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(['Title', 'Video ID', 'URL', 'Description', 'Publish Date', 'Views', 'Edited Transcript',
                       'Transcript Summary'])

        for row in data:
            ws.append(row)

        wb.save(filename)
    except Exception as e:
        logging.error(f"Error saving data to Excel: {e}")


def track_progress(current, total):
    logging.info(f"Processed {current}/{total} videos. {total - current} videos left.")


def remove_duplicates(videos):
    seen = set()
    unique_videos = []
    for video in videos:
        video_id = video['videoId']
        if video_id not in seen:
            seen.add(video_id)
            unique_videos.append(video)
    return unique_videos


def main():
    search_query = input("YouTube Search: ")
    total_videos = int(input("How many videos do you want to analyze? "))
    include_no_transcript = input("Do you want to include videos without transcripts? (yes/no): ").strip().lower() == 'yes'
    all_data = []

    videos_generator = scrapetube.get_search(search_query, limit=total_videos)
    videos = list(videos_generator)
    unique_videos = remove_duplicates(videos)

    for i, video in enumerate(unique_videos):
        video_id = video['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        title, description, publish_date, views = get_video_details(video_id)

        transcript = get_transcript(video_id)
        if not transcript and not include_no_transcript:
            continue

        edited_transcript = organize_transcript(transcript) if transcript else "Transcript not available"
        summary = summarize_transcript(transcript) if transcript else "Summary not available"

        # Print details in the specified order
        print("\nURL:", video_url)
        print("Title:", title)
        print("Publish Date:", publish_date)
        print("Views:", views)
        print("Description:", description)
        print("Transcript:", edited_transcript)
        print("Transcript Summary:", summary)

        data = [title, video_id, video_url, description, publish_date, views, edited_transcript, summary]
        all_data.append(data)

        # Track progress
        track_progress(i + 1, len(unique_videos))

        if i >= total_videos - 1:
            break

    save_to_excel(all_data)


if __name__ == "__main__":
    main()
```

### Comments Analysis

This script downloads comments from YouTube videos and summarizes them, saving the data to an Excel file.

```python
import re
import logging
import scrapetube
from youtube_comment_downloader import YoutubeCommentDownloader
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openpyxl import Workbook
from langchain_community.llms import Ollama

# Initialize the YouTube Data API client
API_KEY = 'YOUR_API_KEY'
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Initialize the Ollama LLM instance
llm = Ollama(base_url="http://131.123.41.132:11434", model="llava:34b")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_video_details(video_id):
    try:
        request = youtube.videos().list(part="snippet,statistics", id=video_id)
        response = request.execute()
        items = response.get('items', [])
        if items:
            snippet = items[0].get('snippet', {})
            statistics = items[0].get('statistics', {})
            title = snippet.get('title', '')
            description = snippet.get('description', '')
            publish_date = snippet.get('publishedAt', '')
            views = statistics.get('viewCount', '')
            return title, description, publish_date, views
    except HttpError as e:
        logging.error(f"API error for video {video_id}: {e}")
    except Exception as e:
        logging.error(f"Error fetching details for video {video_id}: {e}")
    return '', '', '', ''


def get_all_comments(video_id):
    try:
        downloader = YoutubeCommentDownloader()
        comments = []
        for comment in downloader.get_comments_from_url(f'https://www.youtube.com/watch?v={video_id}'):
            comments.append(comment['text'])
        return comments
    except Exception as e:
        logging.error(f"Error downloading comments for video {video_id}: {e}")
        return []


def summarize_comments(comments):
    if not comments:
        return "Transcript does not exist"

    # Join all comments into a single text block
    comments_text = "\n".join(comments)

    # Break comments into chunks if they are too long
    max_chunk_size = 2000  # Define a reasonable chunk size
    comment_chunks = [comments_text[i:i + max_chunk_size] for i in range(0, len(comments_text), max_chunk_size)]

    chunk_summaries = []

    try:
        for chunk in comment_chunks:
            response = llm.invoke(f"Please summarize the following
