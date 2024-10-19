# from youtube_search import YoutubeSearch
# import streamlit as st
# from pytube import YouTube
# from moviepy.editor import *
# import smtplib
# from email.message import EmailMessage
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders
# import zipfile
# import re
# import os

# def downloadVideo(singer,n):
# 	search = singer + 'songs'
# 	output = YoutubeSearch(search,max_results = n).to_dict()
# 	for i in output:
# 		ytVideo = YouTube('https://www.youtube.com' + i['url_suffix'])
# 		vid = ytVideo.streams.filter(file_extension = 'mp4').first()
# 		vid.download(output_path=dest)

# def trimToAudio(i):
# 	clips = []
# 	for file in os.listdir(dest):
# 		filePath = os.path.join(dest,file)
# 		subClip = VideoFileClip(filePath).subclip(0,i)
# 		Audio = subClip.audio
# 		clips.append(Audio)
# 	trimmed = concatenate_audioclips(clips)
# 	trimmed.write_audiofile('mashupfile.mp3')


# def send_mail(recipient, content):

#     mail = "aarushibajaj2004@gmail.com"
#     email_password = "aarushi-1"

#     msg = MIMEMultipart("")
#     msg['Subject'] = "MashUp Songs Of Your Favourite Singer"
#     msg['From'] = mail
#     msg['To'] =recipient

#     attachment = open(content,'rb')
#     obj = MIMEBase('application','octet-stream')
#     obj.set_payload((attachment).read())
#     encoders.encode_base64(obj)
#     obj.add_header('Content-Disposition',"attachment; filename= "+content)
#     msg.attach(obj)

#     # send email
#     with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
#         smtp.login(mail, email_password)
#         smtp.send_message(msg)
#         smtp.quit()
#     print("YOUR MAIL HAS BEEN SENT SUCCESSFULLY")

# def zip(file):
#     final='mashupfile.zip'
#     zipped=zipfile.ZipFile(final,'w')
#     zipped.write(file,compress_type=zipfile.ZIP_DEFLATED)
#     zipped.close()
#     return final

# def mainScript(singer,num,duration,to):
# 	downloadVideo(singer,num)
# 	trimToAudio(duration)
# 	file = 'mashupfile.mp3'
# 	send_mail(to,zip(file))

# form = st.form(key='my_form')
# singer = form.text_input(label='Singer',value='')
# n = form.text_input(label='Number of songs',value=0)
# dur = form.text_input(label='Duration of each song',value=0)
# mailTo = form.text_input(label='Email',value='')
# submit_button = form.form_submit_button(label='Submit')
# regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
# if submit_button:
# 	if not singer.strip():
# 		st.error('Enter Name of singer')
# 	elif int(n)==0:
# 		st.error('Enter Number of songss')
# 	elif int(dur)==0:
# 		st.error("Enter Duration")
# 	elif not re.match(regex,mailTo):
# 		st.error('Enter Email')
# 	else:
# 		dest = "D:\predictiveAnalysis\Mashup\VidFiles"
# 		mainScript(singer,int(n),int(dur),mailTo)

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

st.set_page_config(page_title="Mashup Generator", layout="wide")

# Add custom CSS to style the page: white background and orange buttons
st.markdown("""
    <style>
    body {
        background-color: white;
    }
    .main-title {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
    }
    .sidebar .sidebar-content {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    .stTextInput, .stNumberInput {
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #ff6600 !important;
        color: white !important;
        font-size: 16px;
        padding: 10px;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #cc5200 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Main title
st.markdown("<div class='main-title'>Mashup Generator🎶</div>", unsafe_allow_html=True)
st.write("Download videos from YouTube, trim each video and merge to create a Mashup.")

# st.header("Search and Download Settings")
query = st.text_input("Enter Singer Name:")
num = st.number_input("Number of videos to download:", min_value=1, max_value=10, value=3)
duration = st.number_input("Duration of each video:", min_value=0, max_value=60, value=5)
email_address = st.text_input("Your email address:")

output_folder = "videos"
audio_folder = "audio"
merged_audio_path = os.path.join(audio_folder, "merged_audio.wav")
zip_file_path = os.path.join(audio_folder, "merged_audio.zip")

# Ensure output directories exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(audio_folder, exist_ok=True)

# Helper functions
def sanitize_filename(file):
    #the filename is santized to remove invalid characters.
    sanitized_file = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', file)
    return sanitized_file

def download_videos(query, num):
    #Download videos as per the query-singer name , and number of videos
    ydl_opts = {
        'format': 'best[ext=mp4]/best[ext=webm]/best',
        'noplaylist': True, #avoid downloading playlists
        'quiet': True,
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s')
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch{num}:{query}"])

def trim_audio(duration):
    audio_clips = []
    # extract videos 
    videos = [i for i in os.listdir(output_folder) if i.endswith(('.mp4', '.mkv', '.avi', '.mov'))]
    
    for video in videos:
        video_path = os.path.join(output_folder, video)
        audio_filename = sanitize_filename(f"{os.path.splitext(video)[0]}.wav")
        audio_path = os.path.join(audio_folder, audio_filename)
        
        try:
            video = mp.VideoFileClip(video_path).subclip(duration)
            video.audio.write_audiofile(audio_path)
            audio_clips.append(mp.AudioFileClip(audio_path))
        except Exception as e:
            st.error(f"Error processing {video}: {e}")
        finally:
            video.close()
    
    return audio_clips

def merge_audio(audio_clips):
    if audio_clips:
        merged_audio = mp.concatenate_audioclips(audio_clips)
        merged_audio.write_audiofile(merged_audio_path)
        
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            zipf.write(merged_audio_path, os.path.basename(merged_audio_path))
        
        for audio_clip in audio_clips:
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

def send_email(recipient_email):
    #to mail the generated mashup 
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PW")
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
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
    with st.spinner("Processing in the background..."):
        download_videos(query, num)
        audio_clips = trim_audio(duration)
        merge_audio(audio_clips)
        
        if email_address:
            send_email(email_address)
            st.sidebar.success(f"Merged audio sent to {email_address}.")
        
        delete_files()