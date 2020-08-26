import collections
import glob
import os
import re

import frameseq


class Sequence(object):
    def __init__(self, prefix, padding, suffix, expression):
        self.prefix = prefix
        self.padding = padding
        self.suffix = suffix
        self.frames = expression

    def __repr__(self):
        return "{}{}{}({})".format(
            self.prefix, self.format_padding(), self.suffix, self.frames
        )

    def __str__(self):
        return "{}{}{}".format(self.prefix + self.format_padding() + self.suffix)

    def __iter__(self):
        return (self[i] for i in self.frames)

    def __len__(self):
        return len(self.frames)

    def __getitem__(self, frame):
        return "{}{:0{pad}d}{}".format(
            self.prefix, frame, self.suffix, pad=self.padding
        )

    def format_padding(self):
        return "#" * self.padding


def split_padding(pattern):
    match = re.search(r"#+|%(\d+)d", pattern)
    if not match:
        return ("", 0, "")

    num = match.group(1)
    padding = len(match.group(0)) if num is None else int(num)
    start, end = match.span()
    return pattern[:start], padding, pattern[end:]


def find_sequence_by_pattern(pattern, strict_padding=False):
    prefix, padding, suffix = split_padding(pattern)
    if padding == 0:
        return None

    # Padding is a minimum requirement
    glob_pattern = "{}*{}".format(prefix, suffix)
    re_pattern = r"{}(\d{{{}{}}}){}".format(
        prefix, padding, "" if strict_padding else ",", suffix
    )
    frames = []
    for path in glob.iglob(glob_pattern):
        match = re.match(re_pattern, path)
        if match:
            frame = int(match.group(1))
            frames.append(frame)

    expressions = frameseq.frames_to_expressions(frames)
    if not expressions:
        return None

    return Sequence(prefix, padding, suffix, expressions)


def find_sequences_in_directory(directory):
    mapping = collections.defaultdict(list)

    for filename in os.listdir(directory):
        match = re.search(r"(\d+)(?:\D+)?$", filename)
        if match is None:
            continue

        frame_string = match.group(1)
        start, end = match.span(1)
        prefix = filename[:start]
        suffix = filename[end:]
        mapping[(prefix, suffix)].append(frame_string)

    sequences = []
    for (prefix, suffix), frame_strings in mapping.items():
        lengths = {len(f) for f in frame_strings}
        padding = max(lengths) if len(lengths) == 1 else 1
        frames = sorted(map(int, frame_strings))
        expression = frameseq.frames_to_expressions(frames)
        sequences.append(
            Sequence(os.path.join(directory, prefix), padding, suffix, expression)
        )

    return sequences
