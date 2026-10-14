"""Build web media from the untouched original project's public directory."""
import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys

import imageio_ffmpeg
from PIL import Image

source = Path(sys.argv[1]).resolve()
root = Path(__file__).resolve().parents[1]
target = root / 'public'
assert source != target.resolve(), 'Use the original public directory as input.'
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
excluded = {'premu-lfw-final.mp4', 'church-loop.mp4', 'FENGMIAN3.mp4',
            'fengmian.mp4', 'project-15.mp4', 'project-18.mp4', 'project-21.mp4'}
for name in excluded:
    (target / 'videos' / name).unlink(missing_ok=True)
(target / 'posters').mkdir(exist_ok=True)
(target / 'thumbnails').mkdir(exist_ok=True)

def run(args):
    subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', *args], check=True)

def video(path):
    reader = imageio_ffmpeg.read_frames(str(path))
    meta = next(reader)
    reader.close()
    width, height = meta['source_size']
    card = path.name.startswith('project-')
    hero = path.name == 'FENGMIAN3-web.mp4'
    bound = 960 if card else 1280 if hero else 1920
    scale = min(1, bound / max(width, height))
    w, h = max(2, int(width * scale) // 2 * 2), max(2, int(height * scale) // 2 * 2)
    out = target / 'videos' / path.name
    run(['-i', str(path), '-map', '0:v:0', '-an', '-vf', f'scale={w}:{h},fps={min(30, meta["fps"])}',
         '-c:v', 'libx264', '-crf', '26' if hero else '22', '-preset', 'medium', '-threads', '2',
         '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out)])
    # Preserve an already smaller source while still moving metadata to the front and removing unused audio.
    if out.stat().st_size >= path.stat().st_size:
        run(['-i', str(path), '-map', '0:v:0', '-c:v', 'copy', '-an', '-movflags', '+faststart', str(out)])
    middle = not card and path.name not in {'FENGMIAN3-web.mp4', 'evil-loop.mp4'} and not path.name.startswith('xingtong-')
    poster = target / 'posters' / (path.stem + '.webp')
    run(['-ss', str(meta['duration'] / 2 if middle else 0), '-i', str(path),
         '-frames:v', '1', '-vf', f'scale={w}:{h}', '-c:v', 'libwebp', '-quality', '84', str(poster)])
    print(f'{path.name}: {path.stat().st_size / 1048576:.2f} -> {out.stat().st_size / 1048576:.2f} MiB', flush=True)
    return 'videos/' + path.name, {'poster': 'posters/' + poster.name, 'width': w, 'height': h}

paths = [p for p in (source / 'videos').glob('*.mp4') if p.name not in excluded]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    manifest = dict(pool.map(video, paths))
(root / 'src/videoAssets.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

thumbnails = {}
for path in (source / 'images').iterdir():
    if path.suffix.lower() not in {'.webp', '.jpg', '.png'} or path.name.endswith('-qr.png'):
        continue
    im = Image.open(path).convert('RGB')
    if path.suffix == '.webp':
        optimized = im.copy()
        optimized.thumbnail((2560, 2560), Image.Resampling.LANCZOS)
        out = target / 'images' / path.name
        optimized.save(out, 'WEBP', quality=90, method=6)
        if out.stat().st_size >= path.stat().st_size:
            out.write_bytes(path.read_bytes())
    im.thumbnail((720, 720), Image.Resampling.LANCZOS)
    thumb = target / 'thumbnails' / (path.stem + '.webp')
    im.save(thumb, 'WEBP', quality=85, method=6)
    thumbnails['images/' + path.name] = 'thumbnails/' + thumb.name
(root / 'src/thumbnailAssets.json').write_text(json.dumps(thumbnails, indent=2), encoding='utf-8')
print('Media optimization complete.', flush=True)
