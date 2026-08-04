# pd-live-looper

A Pure Data patch for live music performance: load a WAV, loop it continuously, and control the loop's start point, end point, and playback speed in real time.

Built as the first step toward a multi-track (10-12 file) live looper with per-track effects (echo, phaser, reverse, reverb) and eventual MIDI controller mapping.

## Status

**Phase 1 (current):** single-track loop player
- Load a WAV via file picker
- Loop start / end set as a **percent (0-100)** of the sample's length, not raw sample counts
- Playback speed as a multiplier (1 = normal); pitch shifts with speed, tape-style
- Play/stop toggle
- Waveform display

**Planned next:**
- Reverse, echo, phaser, reverb per track
- Scale up to 10-12 simultaneous tracks
- MIDI controller mapping for all parameters

## Requirements

[Pure Data (Pd) vanilla](https://puredata.info/) 0.52+, or [plugdata](https://plugdata.org/) (same patch works unmodified, nicer UI).

## Usage

Open `01_single_track_loop.pd` in Pd. Click the load button (top-left), pick a `.wav` file, then use the toggle to start/stop playback and the number boxes to adjust start %, end %, and speed while it plays.

## Notes

The patch is hand-written in Pd's text file format rather than built through the Pd GUI editor. A few objects exist purely to work around Pd quirks worth knowing if you're editing this:
- `route symbol` + `list prepend`/`list append`/`list trim` before `soundfiler`, so file paths containing spaces don't get split into multiple message atoms
- `pack`/`unpack` refresh chains around the loop-length and frequency calculations, since Pd's `expr` object only treats its leftmost inlet as "hot" (triggers recompute) — without this, changing `end` or `speed` alone would silently update a stored value without ever refreshing playback
