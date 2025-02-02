# YouTube Video Summarizer

## Description
This is a Flask-based web application that extracts captions from a YouTube video and provides a summarized version of the content using AI-powered NLP models.

## Features
- Extracts captions from YouTube videos.
- Uses OpenAI Whisper for speech-to-text transcription if captions are unavailable.
- Summarizes captions using Facebook's BART-Large-CNN model.
- Supports GPU acceleration for better performance.
- User-friendly web interface.

## Technologies Used
- Python
- Flask
- Whisper AI
- YouTube Transcript API
- PyTube
- Transformers (BART)
- yt-dlp
- HTML, CSS, JavaScript

## Installation
### Prerequisites
- Python 3.8+
- pip
- CUDA-enabled GPU (optional but recommended)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/youtube-video-summarizer.git
   cd youtube-video-summarizer
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask app:
   ```bash
   python app.py
   ```
4. Open the application in your browser at `http://localhost:8000`.

## Usage
1. Enter a YouTube video link in the input field.
2. Click the "Summarize" button.
3. Wait while the system processes the video.
4. View the extracted captions and summarized content.

## API Endpoints
- `POST /get-summarise`
  - Request Body: `{ "youtube_link": "<youtube_video_url>" }`
  - Response: `{ "summary": "<summarized_text>", "video_captions": "<full_transcript>" }`

## Contributing
1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

## Authors
- [Shujath Nawaz]([https://github.com/shujathnawaz](https://github.com/mrranger939))
- [Meer Aakif](https://github.com/meer-aakif-33)

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- OpenAI for Whisper AI
- Hugging Face for Transformers
- yt-dlp for YouTube audio extraction
