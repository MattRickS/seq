import pytest

import frameseq


@pytest.mark.parametrize(
    "frames, expected_string",
    [
        ([1], "1"),
        ([1, 2, 3, 4, 5], "1-5"),
        ([1, 3, 5], "1-5x2"),
        ([1, 3, 5, 10], "1-5x2,10"),
        ([1, 3, 5, 10, 13, 16, 20, 50], "1-5x2,10-16x3,20,50"),
        ([1, 3, 5, 8, 10, 13, 16, 20, 50], "1-5x2,8,10-16x3,20,50"),
        ([-5, -4, -3, 1, 3, 5, 8, 10, 13, 16, 20, 50], "-5--3,1-5x2,8,10-16x3,20,50"),
    ],
)
def test_frames_to_expressions(frames, expected_string):
    assert str(frameseq.frames_to_expressions(frames)) == expected_string


@pytest.mark.parametrize(
    "expression, is_valid",
    [
        ("1-5", True),
        ("1-100x10", True),
        ("1-100x-10", False),
        ("3--3x-1", True),
        ("3--3x1", False),
    ],
)
def test_parse_expressions__valid(expression, is_valid):
    assert bool(frameseq.parse_expression(expression)) is is_valid


@pytest.mark.parametrize(
    "expression, size, frames, start, end, last, range_, ranget",
    [
        ("1", 1, [1], 1, 1, 1, (1, 1), (1, 1)),
        ("0", 1, [0], 0, 0, 0, (0, 0), (0, 0)),
        ("1-5", 5, [1, 2, 3, 4, 5], 1, 5, 5, (1, 5), (1, 5)),
        ("1-5x2", 3, [1, 3, 5], 1, 5, 5, (1, 5), (1, 5)),
        ("1-5x2,10", 4, [1, 3, 5, 10], 1, 10, 10, (1, 10), (1, 10)),
        ("1-5x2,10,15-20x2", 7, [1, 3, 5, 10, 15, 17, 19], 1, 20, 19, (1, 20), (1, 19)),
        ("-1", 1, [-1], -1, -1, -1, (-1, -1), (-1, -1)),
        ("-1-3", 5, [-1, 0, 1, 2, 3], -1, 3, 3, (-1, 3), (-1, 3)),
        ("-1-10x4", 3, [-1, 3, 7], -1, 10, 7, (-1, 10), (-1, 7)),
        ("-4--1", 4, [-4, -3, -2, -1], -4, -1, -1, (-4, -1), (-4, -1)),
        ("-4--1x2", 2, [-4, -2], -4, -1, -2, (-4, -1), (-4, -2)),
        (
            "-10--1x2,1-10x3",
            9,
            [-10, -8, -6, -4, -2, 1, 4, 7, 10],
            -10,
            10,
            10,
            (-10, 10),
            (-10, 10),
        ),
        ("-100,100,500", 3, [-100, 100, 500], -100, 500, 500, (-100, 500), (-100, 500)),
    ],
)
def test_parse_expression(expression, size, frames, start, end, last, range_, ranget):
    expr = frameseq.parse_expression(expression)
    assert str(expr) == expression
    assert len(expr) == size
    assert list(expr) == frames
    assert expr.start() == start
    assert expr.end() == end
    assert expr.last() == last
    assert expr.range() == range_
    assert expr.range(trimmed=True) == ranget
