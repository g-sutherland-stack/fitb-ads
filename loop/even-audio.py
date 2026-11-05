#!/usr/bin/env python3
"""Even out the reel's sound: every segment to the same loudness (-16 LUFS, true peak -1.5 dB), quiet voices
lifted within a clip, each segment cut back to exactly its video length, then one continuous track muxed
onto the untouched picture."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
W = os.path.dirname(os.path.abspath(__file__)); O = W + '/work4'; A = W + '/audio5'; os.makedirs(A, exist_ok=True)
segs = [l.strip()[6:-1] for l in open(O + '/list.txt') if l.startswith("file '")]
def vdur(f):
    j = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=duration', '-of', 'json', f]))
    return float(j['streams'][0]['duration'])
def one(i):
    src = segs[i]; out = f'{A}/a-{i:03d}.wav'
    D = vdur(src)
    af = (f'aresample=48000,aformat=channel_layouts=stereo,'
          f'dynaudnorm=f=400:g=15:p=0.9:m=6,'                      # lifts the quiet passages gently, no pumping
          f'loudnorm=I=-16:TP=-1.5:LRA=9,'                         # the same level for every clip and promo
          # timestamps rebuilt from the sample count, then padded and cut to the exact number of samples
          # the picture lasts: loudnorm shifts timestamps, and a time-based trim came out short
          f'aresample=48000,asetpts=N/SR/TB,apad,atrim=end_sample={round(D * 48000)},asetpts=N/SR/TB')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-af', af, '-c:a', 'pcm_s16le', out], check=True)
with ThreadPoolExecutor(4) as ex: list(ex.map(one, range(len(segs))))
with open(A + '/list.txt', 'w') as fh:
    for i in range(len(segs)): fh.write(f"file 'a-{i:03d}.wav'\n")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', A + '/list.txt', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', A + '/track.m4a'], check=True)
for src, out in [(W + '/fitb-wall-loop-v3-720p.mp4', W + '/fitb-wall-loop-v4-720p.mp4'), (W + '/fitb-wall-loop-v3-1080p.mp4', W + '/fitb-wall-loop-v4-1080p.mp4')]:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-i', A + '/track.m4a', '-map', '0:v', '-map', '1:a', '-c', 'copy', '-shortest', '-movflags', '+faststart', out], check=True)
print('AUDIO DONE', flush=True)
