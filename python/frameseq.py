import re


class Expression(object):
    """
    Represents an A-BxC frame expression, treated as a container of the evaluated frames
    """

    def __init__(self, start, end=None, step=1):
        """
        Args:
            start (int): Frame to start frame (inclusive)
            end (int): Frame to end on (inclusive)
            step (int): Frames to jump between start and end
        """
        self._start = start
        self._end = start if end is None else end
        self._step = step

    def __nonzero__(self):
        start, end, step = self.start(), self.end(), self.step()
        return (end >= start and step > 0) or (end <= start and step < 0)

    __bool__ = __nonzero__

    def __str__(self):
        start, end, step = self.start(), self.end(), self.step()
        if start == end:
            return str(start)
        elif step == 1:
            return "{}-{}".format(start, end)
        else:
            return "{}-{}x{}".format(start, end, self.step())

    def __iter__(self):
        return iter(range(self.start(), self.end() + 1, self.step()))

    def __len__(self):
        if not self:
            return 0
        count, rem = divmod(1 + self.end() - self.start(), self.step())
        return count + int(rem > 0)

    def start(self):
        return self._start

    def end(self):
        return self._end

    def step(self):
        return self._step

    def last(self):
        """
        Returns:
            int: Last frame that can be evaluated. May be different from end if
                the step is not evenly divided into the range. If the expression
                is invalid, this will always return the end.
        """
        if not self:
            return self.end()
        remainder = (self.end() - self.start()) % self.step()
        return self.end() - remainder

    def range(self, trimmed=False):
        """
        Args:
            trimmed (bool): Whether or not to only return the range of evaluated
                values or the full expression range, eg, 1-4x2 resolves to [1, 3]
                and so has a range of (1, 4), and a trimmed range of (1, 3).
                Defaults to False.
        """
        return (self.start(), self.last() if trimmed else self.end())


class Expressions(object):
    """ Represents one or more simple expressions, comma separated """

    def __init__(self, expressions):
        """
        Args:
            expressions (list[Expression]): List of simple expressions
        """
        end = expressions[0].end()
        frames = set()
        for expr in expressions:
            frames.update(expr)
            end = max(end, expr.end())
        self._expressions = expressions
        self._frames = sorted(frames)
        self._end = end

    def __nonzero__(self):
        return bool(self._frames)

    __bool__ = __nonzero__

    def __str__(self):
        return ",".join(map(str, self._expressions))

    def __iter__(self):
        return iter(self._frames)

    def __len__(self):
        return len(self._frames)

    def start(self):
        return min(self._frames)

    def end(self):
        return self._end

    def last(self):
        """
        Returns:
            int: Last frame that can be evaluated. If the expression is invalid,
                this will raise an exception.
        """
        return max(self._frames)

    def range(self, trimmed=False):
        """
        Args:
            trimmed (bool): Whether or not to only return the range of evaluated
                values or the full expression range, eg, 1-4x2 resolves to [1, 3]
                and so has a range of (1, 4), and a trimmed range of (1, 3).
                Defaults to False.
        """
        return (self.start(), self.last() if trimmed else self.end())


def parse_simple_expression(expression):
    re_num = r"((?:-)?\d+)"
    match = re.match("{0}(?:-{0})?(?:x{0})?$".format(re_num), expression)
    if match is None:
        raise ValueError("Unknown expression: {}".format(expression))
    start, end, step = map(int, match.groups(default=0))
    return Expression(start, end=end or start, step=step or 1)


def parse_expression(expression):
    expressions = []
    for expr in expression.split(","):
        expressions.append(parse_simple_expression(expr.strip()))
    return Expressions(expressions)


def consecutive_steps(frames):
    i = last = 0
    # 3 values required to calculate two consecutive differences
    while i < len(frames) - 2:
        a, b, c = frames[i : i + 3]
        # If the differences don't match, there is a break before the last value
        if b - a != c - b:
            # As we check in 3s, if the last break was more than one iteration
            # ago, we must have at least 3 values with equal diff
            if i - last > 0:
                yield frames[last : i + 2]
                # Fast forward past the group just yielded
                i += 1
            # Otherwise we have 1 or 2 values, which don't form a pattern
            else:
                for j in range(last, i + 1):
                    yield frames[j : j + 1]
            # Track the last index we broke on
            last = i + 1
        i += 1
    remainder = frames[last:]
    if len(remainder) >= 3:
        yield remainder
    else:
        for val in remainder:
            yield [val]


def frames_to_expression(frames):
    frames = sorted(frames)
    if not frames:
        start = end = step = 0
    elif len(frames) == 1:
        start = end = frames[0]
        step = 1
    else:
        start = frames[0]
        end = frames[-1]
        step = frames[1] - start

    return Expression(start, end=end, step=step)


def frames_to_expressions(frames):
    expressions = [
        frames_to_expression(segment) for segment in consecutive_steps(sorted(frames))
    ]
    return Expressions(expressions)
