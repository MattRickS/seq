import collections
import glob
import os
import re

import frameseq


class Sequence(object):
    def __init__(self, prefix, padding, suffix, expression):
        self._prefix = prefix
        self.padding = padding
        self._suffix = suffix
        self.frames = expression

    def __repr__(self):
        return "{}{}{}({})".format(
            self._prefix, self.format_padding(), self._suffix, self.frames
        )

    def __str__(self):
        return self._prefix + self.format_padding() + self._suffix

    def __iter__(self):
        return (self[i] for i in self.frames)

    def __len__(self):
        return len(self.frames)

    def __getitem__(self, frame):
        return "{}{:0{pad}d}{}".format(self._prefix, frame, self._suffix, pad=self.padding)

    def format_padding(self):
        return "#" * self.padding


def split_padding(pattern):
    match = re.search("#+|%(\d+)d", pattern)
    if not match:
        return ("", 0, "")

    num = match.group(1)
    padding = len(match.group(0)) if num is None else int(num)
    start, end = match.span()
    return pattern[:start], padding, pattern[end:]


def find_sequence_by_pattern(pattern):
    prefix, padding, suffix = split_padding(pattern)
    if padding == 0:
        return None

    glob_pattern = "{}*{}".format(prefix, suffix)
    re_pattern = "{}(\d{{{}}}){}".format(prefix, padding, suffix)
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
        segments = re.split("(\d+)", os.path.join(filename))
        mapping[tuple(segments[::2])].append(segments[1::2])

    sequences = []
    for (prefix, suffix), values in mapping.items():
        if len(values[0]) > 1:
            print("Multi-numbered files not currently supported")
            continue
        else:
            padding = len(values[0][0])
            expression = frameseq.frames_to_expressions([int(val[0]) for val in values])

        sequences.append(Sequence(os.path.join(directory, prefix), padding, suffix, expression))

    return sequences
