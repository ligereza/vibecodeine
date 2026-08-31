# Phase 182 — apps and src consumer gate

Status: `CLASSIFIED_WITH_VISUAL_READ_GATE_PASS`

## Surface classification

| Path | Observed | MAK consumer | Decision |
|---|---|---|---|
| `/home/mak/apps/antigravity` | Installed Electron/ELF application payload, about 476M | No runtime import or MAK source consumer found; bridge references are file-based operator communication | Keep as application layer; do not merge into `flujo` code or classify its bundled files as duplicate tools. |
| `/home/mak/apps/vscode` | Installed application tree, about 923M | No direct MAK runtime import found; `mak_research/puente.py` documents a VSCode/Antigravity mailbox boundary | Keep as application layer; its binaries are not a migration slice. |
| `/home/mak/src/ml-mobileclip` | External MobileCLIP source with package, model configs, evaluation/training/iOS material and declared requirements | `cultura/mak_plataforma/visual_index.py` lazily imports `mobileclip` for the bounded visual-index builder | Keep as external dependency/source evidence; no install or copy. It is a real consumer-backed candidate, not dead code. |

## Runtime gate

`visual_index.py` compiled successfully and imported without loading Torch,
FAISS, MobileCLIP, or reserving the GPU. A temporary fixture proved safe path
resolution, carousel grouping, video classification, and deterministic sample
selection. The read-only status command for the existing derived surface
returned exit 0:

```text
available=true
model=MobileCLIP-S0
dimension=512
indexed_units=100
eligible_neighbors=345
abstained_neighbors=455
updated_at=2026-08-10T18:16:35-0400
```

The configured checkpoint `/home/mak/models/mobileclip/mobileclip_s0.pt` is
present. A full rebuild was intentionally not run: it would load the model,
use the shared GPU lease and write a new derived index. That is a separate
foreground execution gate, not a static migration proof.

## Dependency decision

`src/ml-mobileclip/requirements.txt` declares `clip-benchmark`, `datasets`,
`open-clip-torch`, `timm`, `torch`, and `torchvision`. These are not converted
into the global MAK requirements and no package was installed. The active
consumer already isolates the expensive imports inside `build_index`; the
lightweight Hub/read path works without them.

## Validation record

- `py_compile visual_index.py`: exit `0`.
- Temporary grouping/read-surface fixture: exit `0`.
- Existing visual-index `status` read: exit `0`.
- No GPU, provider, index rebuild, package install, service, cron, WIN or Git
  action occurred; no persistent process remained.

Next: inspect the next active consumer entry points after the visual index
(`mak_research`/bridge and remaining platform projections), preserving
application binaries and external model source. A full GPU visual-index run
must remain a separately authorized, bounded validation.
