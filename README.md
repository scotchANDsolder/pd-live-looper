# pd-live-looper

A Pure Data patch for live music performance: load a WAV, loop it continuously, and control the loop's start point, end point, and playback speed in real time.

Built as the first step toward a multi-track (10-12 file) live looper with per-track effects (echo, phaser, reverse, reverb) and eventual MIDI controller mapping.

## Status

**Phase 1 (current):** single-track loop player
- Load a WAV via file picker
- Loop start / end set as a **percent (0-100)** of the sample's length, not raw sample counts
- Playback speed as a multiplier (1 = normal); pitch shifts with speed, tape-style
- Play/stop toggle that actually freezes the loop position (not just a mute) — the source `phasor~` frequency is gated to 0 on stop and resumes from the same spot, with the `dac~` output also muted for clean silence
- Waveform display
- Echo effect: on/off toggle, delay time (1-2000 ms), feedback (0-0.95), wet mix (0-1)
- Master volume slider (0-1.5) on the output stage

**Planned next:**
- Reverse, phaser, reverb per track
- Scale up to 10-12 simultaneous tracks
- MIDI controller mapping for all parameters

## Requirements

[Pure Data (Pd) vanilla](https://puredata.info/) 0.52+, or [plugdata](https://plugdata.org/) (same patch works unmodified, nicer UI).

## Usage

Open `01_single_track_loop.pd` in Pd. Click the load button (top-left), pick a `.wav` file, then use the toggle to start/stop playback and the number boxes to adjust start %, end %, and speed while it plays. The echo section (below the waveform display) toggles on/off and adjusts delay time, feedback, and wet mix. The volume slider near the output stage sets master output level.

## Notes

The patch is hand-written in Pd's text file format rather than built through the Pd GUI editor. A few objects exist purely to work around Pd quirks worth knowing if you're editing this:
- `route symbol` + `list prepend`/`list append`/`list trim` before `soundfiler`, so file paths containing spaces don't get split into multiple message atoms
- `pack`/`unpack` refresh chains around the loop-length and frequency calculations, since Pd's `expr` object only treats its leftmost inlet as "hot" (triggers recompute) — without this, changing `end` or `speed` alone would silently update a stored value without ever refreshing playback
- The echo effect is wired as an always-on-dry send/return rather than a wet/dry crossfade: the dry signal passes through unchanged, and the delayed signal is added on top (gated by the on/off toggle) before the play/stop mute stage. This sidesteps the same `expr` hot-inlet refresh problem entirely — no recompute chain needed for the mix
- `+~`/`-~` and friends: giving them a creation argument (e.g. `+~ 0`) locks the right inlet to float-only — it silently stops accepting a signal. The echo feedback sum and the final wet/dry mixer both needed a live *signal* on their right inlet, so those two are declared as bare `+~` (no argument); Pd will silently drop a signal connection into a non-signal inlet with a console warning ("audio signal outlet connected to nonsignal inlet") and never actually mix the audio, which is exactly what a `+~ 0` there would do
- The source freeze-on-stop uses the same pack/trigger/unpack refresh idiom as the loop-length/frequency chain, gating the frequency signal fed to `phasor~` (0 = frozen in place) rather than just muting the output, so stop/resume preserves loop position and live parameter edits still take effect immediately whether playing or paused
