# Video workflow on MAK

## Active contract

The active path is:

`Gmail Apps Script -> GitHub issue -> self-hosted MAK runner -> download_post -> input_ig.mp4 -> render_video_sequence_mak.py -> PNG sequence -> OneDrive`

Image posts still use `render_flyer_mak.py`. Reel links use the MP4 and keep
`input_ig.jpg` only as a poster for operators and the curatoria inbox.

`WIN` is historical evidence only. The active runner does not invoke a
Windows executable or a Windows path.

## Render contract

- Template: `/home/mak/RD/AUTOMATIZACION/RD.blend`
- Blender: `/home/mak/blender/blender` (4.5.4 LTS)
- Input: the downloaded MP4, loaded as a Blender `MOVIE` image
- Frame count: `bpy.data.images.load(video).frame_duration` (not hardcoded)
- FPS: copied from the movie when Blender exposes it
- Engine: `CYCLES`
- Samples: exactly `128`
- Device: GPU required; the run fails if `force_gpu()` reports CPU
- Output: `frame_0001.png ... frame_NNNN.png` plus `render_manifest.json`
- Resume: an existing PNG at least 20,000 bytes is skipped
- Template safety: no `.blend` save operation is performed

The PNG sequence uses the real flyer graph in `RD.blend`: `Material.002` and
`Material.008` are both updated with the MOVIE content, while `FRAME2.png`
remains the frame layer. `RD.paravideo.blend` is a separate historical video
template and is not the active PNG-sequence template.

## Evidence

The local smoke used the existing video
`/home/mak/RD/AUTOMATIZACION/Sundeck vuelve para encender la temporada
🌌Después de un tiempo, nos reencontramos con una noch.mp4`:

- ffprobe estimate: 13.666667 s, 30 fps, 410 source frames
- bounded render: frame 1 only
- result: 1 PNG, 12,464,001 bytes
- manifest: `samples=128`, `engine=CYCLES`, `gpu.device=GPU`,
  `gpu.backend=CUDA`, `NVIDIA GeForce GTX 1650`

The full reel is deliberately not rendered during the smoke; at the measured
single-frame time, 410 full Cycles frames would be a long unattended job.
