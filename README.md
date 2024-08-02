# YouTube Search Comment and Transcript Analyzer

This project allows you to analyze YouTube videos to gather public opinions and potential biases on various topics. The tool fetches video details, transcripts, and comments, providing summaries and organized data to help you understand public sentiments.

## Overview

This tool uses the YouTube Data API, YouTube Transcript API, and an LLM (Large Language Model) to:
- Search for YouTube videos based on a query.
- Fetch video details, transcripts, and comments.
- Organize and summarize transcripts and comments.
- Save the results to an Excel file for further analysis.

You can customize the number of videos to analyze, include/exclude videos without transcripts, and handle duplicate videos.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- YouTube Data API Key
- Required Python packages: `os`, `logging`, `scrapetube`, `googleapiclient`, `openpyxl`, `langchain_community`, `youtube_transcript_api`, `youtube_comment_downloader`

### Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/YouTube-Video-Comment-Analyzer.git
   cd YouTube-Video-Comment-Analyzer
   ```

2. Install the required Python packages:
   ```sh
   pip install -r requirements.txt
   ```

3. Set your YouTube Data API key:
   ```python
   API_KEY = 'YOUR_API_KEY'
   ```

### Running the Code

1. Open the `analyze_transcripts.py` file and `analyze_comments.py` file.
2. Update the `API_KEY` variable with your YouTube Data API key.
3. Run the script:
   ```sh
   python analyze_transcripts.py
   ```
   or
   ```sh
   python analyze_comments.py
   ```
4. Follow the prompts to input your search query, number of videos, and other options.

## Demo

Check out this [tutorial walkthrough video](https://youtu.be/_XrP-Ch8D-s) to see how to run the code and what the final output looks like.
