import os
# import whisper
import openai_whisper as whisper
from pytube import YouTube
from flask import Flask, request,render_template, jsonify, redirect
import re
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import BartForConditionalGeneration, BartTokenizer
from transformers import BartTokenizer, pipeline
import torch
import subprocess
# Load Whisper model
whisper_model = whisper.load_model("base")  # You can use "small", "medium", or "large" for better accuracy

""" Functions Start """
print(torch.cuda.is_available())  # Should return True
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"devise is {device}")

def download_audio(video_url, video_id):
    try:
        directory_path = os.getcwd()
        output_dir = os.path.join(directory_path, "Audios")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{video_id}.mp3")
        
        # yt-dlp command
        command = [
            "yt-dlp", "-x", "--audio-format", "mp3",
            "-o", output_path, video_url
        ]

        #or use this if the above command doesn't work
        # command = [
        #     "python", "-m", "yt_dlp", "-x", "--audio-format", "mp3",
        #     "-o", output_path, video_url
        # ]
        
        print(f"Running command: {' '.join(command)}")
        
        # Run the command and capture output
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # print("STDOUT:", process.stdout)
        # print("STDERR:", process.stderr)
        # process.check_returncode()
        
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Audio file not created at {output_path}")
        
        return output_path
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

def transcribe_audio(audio_path):
    try:
        result = whisper_model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None


def extract_video_id(youtube_url):
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)
    return None

def get_captions(video_id):
    try:
        # Attempt to fetch YouTube captions
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = "\n".join([entry['text'] for entry in transcript])
        return text
    except Exception as e:
        print(f"No YouTube captions found, falling back to Whisper: {e}")
        # If captions are unavailable, use Whisper
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        audio_path = download_audio(youtube_url, video_id)
        if audio_path:
            captions = transcribe_audio(audio_path)
            os.remove(audio_path)  
            return captions
        return "Unable to generate captions."

""" summarising!! Starts """
model_name = 'facebook/bart-large-cnn'
model = BartForConditionalGeneration.from_pretrained(model_name).to(device) 
tokenizer = BartTokenizer.from_pretrained(model_name)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)
def summarize_text(text):

    tokenized_text = tokenizer.encode(text, truncation=False, add_special_tokens=False)
    num_tokens = len(tokenized_text)
    print(f"Number of tokens in input text: {num_tokens}")

    # Function to summarize text
    def summarize_chunk(chunk):
        inputs = tokenizer.encode(chunk, return_tensors='pt').to(device)
        summary_ids = model.generate(inputs, max_length=100, min_length=50, do_sample=False)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

    # Summarize the text in chunks if necessary
    if num_tokens < 50:  # Handle short texts
        print("Input text is too short for summarization.")
        return text
    elif num_tokens <= 1024:
        summary = summarize_chunk(text)
        return summary
    else:
        # Split the text into chunks of 1022 tokens
        chunks = [tokenized_text[i:i + 1022] for i in range(0, num_tokens, 1022)]
        summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i + 1}/{len(chunks)}")
            chunk_text = tokenizer.decode(chunk, skip_special_tokens=True)
            summary = summarize_chunk(chunk_text)
            summaries.append(summary)
        combined_summary = ' '.join(summaries)
        return combined_summary
""" summarising!! Ends """

""" Functions End """

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/text')
def textsum():
    return render_template('textsum.html')

@app.route('/captions')
def captions():
    return render_template('captions.html')

@app.post('/get-captions')
def getCaptions():
    data = request.get_json()
    youtube_link = data.get('youtube_link')
    video_id = extract_video_id(youtube_link)
    video_captions = get_captions(video_id)
    return jsonify({"video_captions": video_captions })

@app.post('/get-text-summary')
def text_summarise():
    data = request.get_json()
    text = data.get('text_input')
    summary = summarize_text(text)
    return jsonify({"summary": summary })


@app.post('/get-summarise')
def do_summarise():
    data = request.get_json()
    youtube_link = data.get('youtube_link')
    video_id = extract_video_id(youtube_link)
    video_captions = get_captions(video_id)
    summary = summarize_text(video_captions)
    print(youtube_link)
    if youtube_link:
        print(f'received the youtube video link it is: {youtube_link}')
        # summary = f"Summary for the video at {youtube_link} and video id is {video_id}\n and captions are {video_captions} \n \n \n the Summary is {summary}"
        return jsonify({"summary": summary, "video_captions": video_captions })
    else:
        return jsonify({"error": "YouTube link is required!"}), 400


if __name__ == '__main__':
    app.run(port=8000, debug=True)