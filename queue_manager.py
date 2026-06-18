from collections import deque


class MusicQueue:
    def __init__(self):
        self._queue = deque()

    def add(self, track: dict):
        self._queue.append(track)

    def next(self):
        if self._queue:
            self._queue.popleft()

    def current(self):
        if self._queue:
            return self._queue[0]
        return None

    def is_empty(self):
        return len(self._queue) == 0

    def size(self):
        return len(self._queue)

    def clear(self):
        self._queue.clear()

    def get_all(self):
        return list(self._queue)
