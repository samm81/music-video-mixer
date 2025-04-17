from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
from tqdm import tqdm
import json
import os.path
import sys
from collections import namedtuple

# change these
offsets = {"vid1.mp4": 1.2, "vid2.mp4": 0, "vid3.mp4": 1.2, "vid4.mp4": 1.1}
jsonfilename = "data.json"
songfilename = "song.mp4"


def check_safe():
    if any([os.path.exists(f) for f in ["beatsmix.mp4", "barsmix.mp4"]]):
        print("exiting because beatsmix.mp4 or barsmix.mp4 exists")
        sys.exit(1)


def load_files(offsets=offsets, jsonfilename=jsonfilename, songfilename=songfilename):
    print("Loading files...")
    song = AudioFileClip(songfilename)
    clips = [VideoFileClip(name).subclipped(offset) for name, offset in offsets.items()]
    info = json.load(open(jsonfilename))
    bars = info["bars"]
    beats = info["beats"]
    print("Loaded.")
    return clips, song, bars, beats


Segment = namedtuple("Segment", ["start", "end"])


def unraw(seq):
    for json_seg in seq:
        start, duration = json_seg["start"], json_seg["duration"]
        yield Segment(start, start + duration)


def generate(clips, segments, song, name):
    print(f"Generating {name}...")
    clips = [
        clips[i % len(clips)].subclip(*segment)
        for i, segment in tqdm(enumerate(segments))
    ]
    print(f"Generated. Generating {name} video...")
    clip = concatenate_videoclips(clips)
    clip = clip.with_audio(song)
    print(f"Generated. Writing {name} video...")
    clip.write_videofile(f"{name}mix.mp4")
    print("Generated.")


if __name__ == "__main__":
    check_safe()
    clips, song, raw_bars, raw_beats = load_files()
    bars, beats = unraw(raw_bars), unraw(raw_beats)
    generate(clips, bars, song, "bars")
    generate(clips, beats, song, "beats")
