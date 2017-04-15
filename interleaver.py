from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from tqdm import tqdm
import json
import os.path
import sys

vid1_offset = 0
vid2_offset = 0

def check_safe():
  if any([ os.path.exists(f) for f in [ "beats_out.mp4", "bars_out.mp4" ] ]):
    print "exiting because beats_out.mp4 or bars_out.mp4 exists"
    sys.exit(1)

def load_files():
  print "Loading files..."
  song = AudioFileClip("hyuna.mp3")
  clip1 = VideoFileClip("hyuna1.mp4")
  clip1 = clip1.subclip(vid1_offset, song.duration + vid1_offset)
  clip2 = VideoFileClip("hyuna2.mp4")
  clip2 = clip2.subclip(vid2_offset, song.duration + vid2_offset)
  info = json.load(file("hyuna.json"))
  bars = info['bars']
  beats = info['beats']
  print "Loaded."
  return song, clip1, clip2, bars, beats

def generate_bars(clip1, clip2, song, bars):
  print "Generating bars..."
  bar_times = []
  clip1_bars = []
  clip2_bars = []
  bar_times = [(bar['start'], bar['start'] + bar['duration']) for bar in bars ]
  for (t1, t2) in tqdm(bar_times):
    clip1_bars.append(clip1.subclip(t1, t2))
  for (t1, t2) in tqdm(bar_times):
    clip2_bars.append(clip2.subclip(t1, t2))

  out_bars = []
  for i, clips in tqdm(enumerate(zip(clip1_bars, clip2_bars))):
    out_bars.append(clips[i % 2])
  print "Generated."

  print "Generating bars video..."
  out_bars_clip = concatenate_videoclips(out_bars)
  out_bars_clip = out_bars_clip.set_audio(song)
  print "Generated."

  print "Writing bars video..."
  out_bars_clip.write_videofile("bars_out.mp4")
  print "Generated."

def generate_beats(clip1, clip2, song, beats):
  print "Generating beats..."
  beat_times = []
  clip1_beats = []
  clip2_beats = []
  beat_times = [(beat['start'], beat['start'] + beat['duration']) for beat in beats ]
  for (t1, t2) in tqdm(beat_times):
    clip1_beats.append(clip1.subclip(t1, t2))
  for (t1, t2) in tqdm(beat_times):
    clip2_beats.append(clip2.subclip(t1, t2))

  out_beats = []
  for i, clips in tqdm(enumerate(zip(clip1_beats, clip2_beats))):
    out_beats.append(clips[i % 2])
  print "Generated."

  print "Generating beats video..."
  out_beats_clip = concatenate_videoclips(out_beats)
  out_beats_clip = out_beats_clip.set_audio(song)
  print "Generated."

  print "Writing beats video..."
  out_beats_clip.write_videofile("beats_out.mp4")
  print "Generated."

check_safe()
song, clip1, clip2, bars, beats = load_files()
generate_bars(clip1, clip2, song, bars)
generate_beats(clip1, clip2, song, beats)
