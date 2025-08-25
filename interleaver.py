import hashlib
import math
import random
from typing import Iterable, Optional

import moviepy as mp
from tqdm import tqdm


def _init(
    filename: str,
    bar_length: float,
    offset: float = 0,
) -> tuple[mp.VideoClip, Iterable[tuple[float, float]]]:
    video_clip = mp.VideoFileClip(filename)

    def segment_gen():
        start = offset
        while start < video_clip.duration:
            end = min(start + bar_length, video_clip.duration)
            yield (start, end)
            start = end

    return (video_clip, segment_gen())


def cut_and_save(
    filename: str,
    bar_length: float,
    offset: float = 0,
):
    (video_clip, segments_gen) = _init(filename, bar_length, offset)

    segments = list(segments_gen)

    with tqdm(total=len(segments)) as tqdm_outer:
        for i, segment in tqdm(enumerate(segments)):
            clip = video_clip.subclipped(*segment)
            clip.write_videofile(
                f"clip{i:02d}.webm",
                codec="libvpx",
                fps=15,
                preset="ultrafast",
                ffmpeg_params=["-aspect", "9:16", "-loglevel", "error"],
            )
            tqdm_outer.update(1)


def interleave(
    filename: str,
    beat_length: float,
    cut_count: int,
    offset: float = 0,
    audio_offset_beats: float = 0,
    whitelist: list[int] = [],
    target_length: Optional[int] = None,
):
    cut_length = beat_length * cut_count
    (video_clip, segments_gen) = _init(filename, cut_length, offset)
    audio_clip = video_clip.audio
    if not audio_clip:
        raise Exception("No audio on video")

    segments = list(segments_gen)

    segments_needed_num = (
        math.ceil(target_length / cut_length) if target_length else len(segments)
    )

    segments_whitelisted = [
        seg for (_i, seg) in filter((lambda e: e[0] in whitelist), enumerate(segments))
    ]
    segments_sample = random.sample(segments_whitelisted, segments_needed_num)
    subclips = [video_clip.subclipped(*seg) for seg in segments_sample]
    clip_concatenated = mp.concatenate_videoclips(subclips)

    audio_offset = offset + audio_offset_beats * beat_length
    clip_with_audio = clip_concatenated.with_audio(
        audio_clip.subclipped(audio_offset, audio_offset + clip_concatenated.duration)
    )

    segments_hash = hashlib.sha256(repr(segments_sample).encode()).hexdigest()

    clip_with_audio.write_videofile(
        f"mixed-{cut_count}-{segments_hash}.webm",
        codec="libvpx",
        preset="ultrafast",
        ffmpeg_params=["-aspect", "9:16", "-loglevel", "error"],
    )


if __name__ == "__main__":
    tempo_bpm = 83
    bar_count = 6

    beat_length = 60 / tempo_bpm
    bar_length = beat_length * bar_count

    audio_offset_beats = 3 * 6

    whitelist_bars = list(set(range(2, 23)).difference(set([16])))
    whitelist = []

    cut_count = 4

    interleave(
        "./your-file.mp4",
        beat_length=beat_length,
        cut_count=cut_count,
        offset=0.77,
        audio_offset_beats=audio_offset_beats,
        whitelist=whitelist,
        target_length=30,
    )
