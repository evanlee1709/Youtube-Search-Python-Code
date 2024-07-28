import re
import logging
import scrapetube
from youtube_comment_downloader import YoutubeCommentDownloader
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openpyxl import Workbook
from langchain_community.llms import Ollama

# Initialize the YouTube Data API client
API_KEY = 'AIzaSyBk-J3xo7kVE8TXxWfSkI2PLHhB_Du_oNA'
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
            response = llm.invoke(f"Please summarize the following YouTube comments in 3-4 sentences:\n{chunk}")
            logging.info(f"LLM response: {response}")

            if isinstance(response, str):
                chunk_summaries.append(response.strip())
            elif isinstance(response, dict) and 'text' in response:
                chunk_summaries.append(response['text'].strip())
            else:
                chunk_summaries.append("Summary not available")

        # Summarize the chunk summaries
        combined_summaries = " ".join(chunk_summaries)
        final_summary_response = llm.invoke(
            f"Please provide a concise summary of the following text in 2-3 sentences:\n{combined_summaries}")
        logging.info(f"Final LLM summary response: {final_summary_response}")

        if isinstance(final_summary_response, str):
            final_summary = final_summary_response.strip()
        elif isinstance(final_summary_response, dict) and 'text' in final_summary_response:
            final_summary = final_summary_response['text'].strip()
        else:
            final_summary = "Summary not available"

        return final_summary
    except Exception as e:
        logging.error(f"Error summarizing comments: {e}")
        return "Summary not available"


def save_to_excel(all_data, filename='Comments.xlsx'):
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Comments"
        ws.append(['Video ID', 'Title', 'URL', 'Summary', 'Comment'])

        for data in all_data:
            title, video_id, video_url, comments, summary = data

            # Add the summary in the first row for each video
            ws.append([video_id, title, video_url, summary, ""])

            # Append each comment as a separate row
            for comment in comments:
                ws.append([video_id, title, video_url, "", comment.strip()])

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
    all_data = []
    total_videos = 20

    videos_generator = scrapetube.get_search(search_query, limit=total_videos)
    videos = list(videos_generator)
    unique_videos = remove_duplicates(videos)

    for i, video in enumerate(unique_videos):
        video_id = video['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        title, description, publish_date, views = get_video_details(video_id)

        top_comments = get_all_comments(video_id)
        print('URL:', video_url)
        print("Comments:")
        for j, comment in enumerate(top_comments, 1):
            print(f"Comment {j}: {comment}\n")

        summary = summarize_comments(top_comments)
        print(f"Summary: {summary}\n")

        data = [title, video_id, video_url, top_comments, summary]
        all_data.append(data)

        # Track progress
        track_progress(i + 1, len(unique_videos))

        if i >= total_videos - 1:
            break

    save_to_excel(all_data)


if __name__ == "__main__":
    main()
