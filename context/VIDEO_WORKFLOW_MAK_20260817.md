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

## Aspect-ratio and visual layout policy

This is the canonical decision record for future agents and future renders.
The glass opening is measured from `FRAME2.png`; its effective aspect ratio is
approximately `0.735` (width/height). Source dimensions come from the actual
downloaded image or video, never from a filename and never from an assumption
that every reel is 16:9.

### Input options and active paths

| Input classified by downloader | Active renderer | Layout contract |
| --- | --- | --- |
| `image` | `render_flyer_mak.py` -> `blender_nodes.py` | `fitwidth_fade`: fill the opening width, preserve proportions, center vertically, and use the existing fade for vertical excess/shortfall. |
| any video ratio | `render_video_sequence_mak.py` -> `blender_nodes_video_seq.py` | `fitwidth_fade`: fill the opening width, preserve proportions, center vertically, and use the existing fade for vertical excess/shortfall. The measured source ratio is retained in the manifest for evidence, not to select a different scale policy. |
| `carousel` | image path using the downloaded poster | Current behavior is intentionally equivalent to the image path; it is not silently treated as a multi-video render. |
| unknown or missing type | no renderer | Fail closed; do not guess whether the asset is an image or video. |

### Video aspect evidence

The wrapper measures the source with `ffprobe` before Blender runs and writes
`issue_flow`, `layout.policy`, `layout.source_aspect_ratio`,
`layout.window_aspect_ratio`, `layout.crop_axis`, `layout.fade_axis` and
`layout.black_bars` into `render_manifest.json`. It does not infer a flow
from the filename or from the fact that the URL is an Instagram reel.

| Measured source | Issue flow | Layout | Result |
| --- | --- | --- | --- |
| Ratio within `0.03` of portrait `9:16` | `video_portrait_9_16` | `fitwidth_fade` | Match the lateral borders; center vertically; fade the vertical excess/shortfall; preserve proportions. |
| Any other ratio, including square, 4:5, 4:3, 16:9 and irregular video | `video_other_aspect` | `fitwidth_fade` | Same Blender mapping. The source ratio remains measured evidence; it does not silently switch to contain or cover. |

Neither video flow stretches the image. A caller cannot silently select the
wrong policy: a requested layout that disagrees with the measured flow fails
before Blender starts.

### Non-negotiable production choices

- Preserve aspect ratio; never stretch.
- Match the lateral borders for both stills and videos; use the vertical fade
  for excess or shortfall rather than changing policy by media type.
- Center the source vertically; do not carry a one-off reel offset forward.
- Keep one shared `fitwidth_fade` production path for stills and videos.
- Render video frames as PNG with Cycles 128 samples and verified GPU, as
  described above; do not silently reduce samples to solve a composition issue.

## Historical evidence

The smoke below is historical evidence from a temporary MP4. That source is
not a current input and is no longer present on the MAK filesystem; do not
use this section as proof that a new event has already been processed.

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
