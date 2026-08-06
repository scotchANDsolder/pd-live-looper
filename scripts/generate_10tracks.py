"""
Regenerates 01_engine_10tracks.pd and 02_gui_10tracks.pd from the single-track
templates (01_single_track_loop.pd and 02_gui_control_panel.pd).

Each track gets its own uniquely-suffixed (_tN) delay-line names, array name,
and loopergui_* send/receive symbols, and its own vertically-offset block of
objects with indices renumbered so every #X connect line stays internally
consistent. Run this after editing either single-track template so the
10-track files pick up the change:

    python3 scripts/generate_10tracks.py
"""
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NUM_TRACKS = 10
Y_OFFSET_PER_TRACK = 2200

DELAY_NAMES = ['echoline', 'comb1', 'comb2', 'comb3', 'comb4', 'ap1', 'ap2']
ARRAY_NAME = 'trackArray'
SEND_NAMES = [
    'loopergui_load', 'loopergui_play1', 'loopergui_play2', 'loopergui_start',
    'loopergui_end', 'loopergui_speed', 'loopergui_volume', 'loopergui_echoonoff',
    'loopergui_delayms', 'loopergui_feedback', 'loopergui_echowet',
    'loopergui_reverbonoff', 'loopergui_decay', 'loopergui_reverbwet',
    'loopergui_filename',
]

OBJ_KEYWORDS = ('#X obj ', '#X msg ', '#X floatatom ', '#X text ', '#X symbolatom ')
COUNTED_KEYWORDS = ('#X obj ', '#X msg ', '#X floatatom ', '#X text ', '#X restore ', '#X symbolatom ')


def rename_track_specific(line, n):
    for name in sorted(DELAY_NAMES, key=len, reverse=True):
        line = re.sub(r'\b' + re.escape(name) + r'\b', f'{name}_t{n}', line)
    line = re.sub(r'\b' + re.escape(ARRAY_NAME) + r'\b', f'{ARRAY_NAME}_t{n}', line)
    for name in SEND_NAMES:
        line = re.sub(r'\b' + re.escape(name) + r'\b', f'{name}_t{n}', line)
    return line


def offset_coords(line, dy):
    for kw in OBJ_KEYWORDS:
        if line.startswith(kw):
            parts = line.split(' ')
            y = int(parts[3])
            parts[3] = str(y + dy)
            return ' '.join(parts)
    if line.startswith('#X restore '):
        parts = line.split(' ')
        y = int(parts[2])
        parts[2] = str(y + dy)
        return ' '.join(parts)
    return line


def is_counted(line):
    return line.startswith(COUNTED_KEYWORDS)


def process_engine():
    src = os.path.join(REPO_ROOT, '01_single_track_loop.pd')
    dst = os.path.join(REPO_ROOT, '01_engine_10tracks.pd')

    with open(src) as f:
        lines = f.read().split('\n')
    body = [l for l in lines[1:] if l.strip() != '']

    obj_lines = []
    connect_lines = []
    for l in body:
        if l.startswith('#X connect '):
            connect_lines.append(l)
        else:
            obj_lines.append(l)

    out = ['#N canvas 40 40 950 800 12;']
    running_index = 0

    title_line = ('#X text 20 10 PD LIVE LOOPER - 10 TRACK ENGINE (this file is the DSP\\, '
                  'not meant to be interacted with directly -- use the GUI rack file);')
    out.append(title_line)
    running_index += 1

    track_start_index = {}

    for n in range(1, NUM_TRACKS + 1):
        dy = (n - 1) * Y_OFFSET_PER_TRACK

        out.append(f'#X text 20 {30 + dy} == TRACK {n} ==;')
        running_index += 1

        track_start_index[n] = running_index

        for l in obj_lines:
            nl = offset_coords(l, dy + 30)
            nl = rename_track_specific(nl, n)
            out.append(nl)
            if is_counted(l):
                running_index += 1

    for n in range(1, NUM_TRACKS + 1):
        idx_offset = track_start_index[n]
        for l in connect_lines:
            m = re.match(r'#X connect (\d+) (\d+) (\d+) (\d+);', l)
            csrc, sout, cdst, din = (int(x) for x in m.groups())
            out.append(f'#X connect {csrc + idx_offset} {sout} {cdst + idx_offset} {din};')

    with open(dst, 'w') as f:
        f.write('\n'.join(out) + '\n')

    print(f'engine: {len(connect_lines)} connects/track, {NUM_TRACKS} tracks, '
          f'total_objects={running_index}')


def process_gui():
    src = os.path.join(REPO_ROOT, '02_gui_control_panel.pd')
    dst = os.path.join(REPO_ROOT, '02_gui_10tracks.pd')

    with open(src) as f:
        lines = [l for l in f.read().split('\n') if l.strip() != '']

    title_line = lines[2]
    rack_unit = lines[3:]

    # rack_unit's objects start at global index 2 in the single-track template
    # (index 0 = background cnv, index 1 = title cnv), so connect lines within
    # rack_unit reference indices >= 2 -- convert those to rack-local (0-based)
    # indices here, mirroring process_engine's approach.
    RACK_UNIT_BASE_INDEX = 2

    rack_obj_lines = []
    rack_connect_lines = []
    for l in rack_unit:
        if l.startswith('#X connect '):
            rack_connect_lines.append(l)
        else:
            rack_obj_lines.append(l)

    total_height = NUM_TRACKS * 380 + 20
    out = ['#N canvas 40 40 1150 700 12;']
    out.append(f'#X obj 0 0 cnv 15 1120 {total_height} empty empty empty 0 0 0 10 '
               f'-1184279 -1184279 0;')
    out.append(title_line)

    running_index = 2  # background cnv + title cnv already emitted above
    rack_start_index = {}

    for n in range(1, NUM_TRACKS + 1):
        dy = 30 + (n - 1) * 380
        out.append(f'#X obj 20 {dy - 15} cnv 1 1 1 empty empty TRACK_{n} 0 -5 0 12 '
                   f'-1184279 -16755241 0;')
        running_index += 1  # the TRACK_N label consumes one index

        rack_start_index[n] = running_index

        for l in rack_obj_lines:
            nl = offset_coords(l, dy)
            nl = rename_track_specific(nl, n)
            out.append(nl)
            if is_counted(l):
                running_index += 1

    for n in range(1, NUM_TRACKS + 1):
        idx_offset = rack_start_index[n] - RACK_UNIT_BASE_INDEX
        for l in rack_connect_lines:
            m = re.match(r'#X connect (\d+) (\d+) (\d+) (\d+);', l)
            csrc, sout, cdst, din = (int(x) for x in m.groups())
            out.append(f'#X connect {csrc + idx_offset} {sout} {cdst + idx_offset} {din};')

    with open(dst, 'w') as f:
        f.write('\n'.join(out) + '\n')

    print(f'gui: {NUM_TRACKS} racks, total height {total_height}, '
          f'{len(rack_connect_lines)} connects/rack, total_objects={running_index}')


if __name__ == '__main__':
    process_engine()
    process_gui()
