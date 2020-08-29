import frameseq
import pathseq


def test_sequence():
    seq = pathseq.Sequence("abc.", 3, ".def", frameseq.parse_expression("1-3"))
    assert len(seq) == 3
    assert list(seq) == ["abc.001.def", "abc.002.def", "abc.003.def"]
    assert bool(seq) is True
    assert seq[1] == "abc.001.def"
    # Out of range shouldn't matter
    assert seq[10] == "abc.010.def"
    assert str(seq) == "abc.###.def"
    assert repr(seq) == "abc.###.def(1-3)"


def test_find_sequence_by_pattern(fs):
    for i in range(1, 11):
        fs.create_file("/path/to/frame.{:04d}.ext".format(i))
    sequence = pathseq.find_sequence_by_pattern("/path/to/frame.####.ext")
    assert sequence is not None
    assert sequence.frames.range() == (1, 10)


def test_find_sequences_in_directory(fs):
    # /path/to/frame.####.ext(1-3,5-7)
    for i in range(1, 4):
        fs.create_file("/path/to/frame.{:04d}.ext".format(i))
    for i in range(5, 8):
        fs.create_file("/path/to/frame.{:04d}.ext".format(i))

    # /path/to/otherFrame.##.ext(10-100x10)
    for i in range(10, 101, 10):
        fs.create_file("/path/to/otherFrame.{:02d}.ext".format(i))

    # /path/to/someFrame.#.ext(8,12,20,42)
    for i in (8, 12, 20, 42):
        fs.create_file("/path/to/someFrame.{}.ext".format(i))

    sequences = pathseq.find_sequences_in_directory("/path/to")
    assert len(sequences) == 3
