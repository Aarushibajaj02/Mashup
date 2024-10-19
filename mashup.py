
import streamlit as st
import yt_dlp
import moviepy.editor as mp
import os
import zipfile
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import traceback

st.set_page_config(page_title="Mashup Generator", layout="wide")

st.markdown("""
    <style>
    body {
        background-color:white ; 
    }
    .main-title {
        font-size: 2.5rem;
        color: red;
        text-align: center;
        font-weight:bold;
    }
    .sidebar .sidebar-content {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    .stTextInput, .stNumberInput {
        margin-bottom: 20px;
    }

    </style>
    """, unsafe_allow_html=True)

# Main title
st.markdown("<div class='main-title'>Mashup Generator</div>", unsafe_allow_html=True)
st.write("Download videos from YouTube, trim each video and merge to create a Mashup.")

st.header("Please fill in the details")
query = st.text_input("Enter Singer Name:","Sharry Mann")
num = st.number_input("Number of videos to download:", min_value=1, max_value=10)
duration = st.number_input("Duration of each video(seconds):", min_value=0, max_value=60)
email_address = st.text_input("Your email address:")

output_folder = "videos"
audio_folder = "audio"
merged_audio_path = os.path.join(audio_folder, "merged_audio.wav")
zip_file_path = os.path.join(audio_folder, "merged_audio.zip")

# Ensure output directories exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(audio_folder, exist_ok=True)
os.makedirs(os.path.dirname(merged_audio_path), exist_ok=True)

def sanitize_filename(file):
    #the filename is santized to remove invalid characters.
    sanitized_file = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', file)
    return sanitized_file

def download_videos(query, num):
    #Download videos as per the query-singer name , and number of videos
    ydl_opts = {
        'ignoreerrors': True,  # Skip errors
        'format': 'best',
        'noplaylist': True, #avoid downloading playlists
        'quiet': True,
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s')
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
         # Construct and run the ytsearch query correctly
        ydl.download([f"ytsearch{num_videos}:{search_query}"])

def trim_audio(duration):
    audio = []
    # extract videos 
    videos = [i for i in os.listdir(output_folder) if i.endswith(('.mp4', '.mkv', '.avi', '.mov'))]
    
    for video in videos:
        video_path = os.path.join(output_folder, video)
        audio_filename = sanitize_filename(f"{os.path.splitext(video)[0]}.wav")
        audio_path = os.path.join(audio_folder, audio_filename)
        
        try:
            video = mp.VideoFileClip(video_path).subclip(duration)
            video.audio.write_audiofile(audio_path)
            audio.append(mp.AudioFileClip(audio_path))
        except Exception as e:
            st.error(f"Error processing {video}: {e}")
        finally:
            video.close()
    
    return audio

def merge_audio(audio):
    if audio:
        merged_audio = mp.concatenate_audioclips(audio)
        merged_audio.write_audiofile(merged_audio_path)
        
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            zipf.write(merged_audio_path, os.path.basename(merged_audio_path))
        
        for audio_clip in audio:
            audio_clip.close()

def delete_files():

    video_files = [f for f in os.listdir(output_folder) if f.endswith(('.mp4', '.mkv', '.avi', '.mov'))]
    for video_file in video_files:
        video_path = os.path.join(output_folder, video_file)
        os.remove(video_path)
    
    audio_files = [f for f in os.listdir(audio_folder) if f.endswith('.wav') and f != 'merged_audio.wav']
    for audio_file in audio_files:
        audio_path = os.path.join(audio_folder, audio_file)
        os.remove(audio_path)
    
    st.success("Temporary files have been deleted.")

def send_email(email):
    #to mail the generated mashup 
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PW")
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Your Mashup has been generated.ENJOY! "
    
    body = "Please find the attached Mashup."
    msg.attach(MIMEText(body, 'plain'))
#ATTACHING AUDIO TO MAIL
    with open(merged_audio_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(merged_audio_path)}")
        msg.attach(part)
#SENDING THE MAIL
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

# Button to trigger the process
if st.sidebar.button("Download and Process"):
    with st.spinner("Downloading videos..."):
        download_videos(search_query, num_videos)
        st.success(f"Downloaded {num_videos} videos.")
    
    with st.spinner("Processing audio..."):
        audio_clips = process_audio(trim_seconds)
        merge_audio(audio_clips)
        st.success("Audio processed and merged.")

    st.audio(merged_audio_path)

    with open(merged_audio_path, "rb") as audio_file:
        st.download_button(label="Download Merged Audio", data=audio_file, file_name="merged_audio.wav", mime="audio/wav")
    if email_address:
        with st.spinner("Sending email..."):
            send_email(email_address)
            st.success(f"Merged audio sent to {email_address}.")
    
    delete_files()