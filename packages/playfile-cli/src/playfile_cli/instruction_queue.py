"""User instruction queue for agent intervention."""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass


@dataclass
class UserInstruction:
    """Represents a user instruction to inject into agent execution."""

    text: str
    timestamp: float


class InstructionQueue:
    """Thread-safe queue for user instructions during agent execution."""

    def __init__(self) -> None:
        """Initialize instruction queue."""
        self._queue: queue.Queue[UserInstruction] = queue.Queue()
        self._lock = threading.Lock()

    def add(self, instruction: str) -> None:
        """Add a user instruction to the queue.

        Args:
            instruction: User instruction text
        """
        import time

        with self._lock:
            self._queue.put(UserInstruction(text=instruction, timestamp=time.time()))

    def get_all(self) -> list[UserInstruction]:
        """Get all pending instructions and clear the queue.

        Returns:
            List of pending instructions
        """
        instructions = []
        with self._lock:
            while not self._queue.empty():
                try:
                    instructions.append(self._queue.get_nowait())
                except queue.Empty:
                    break
        return instructions

    def has_pending(self) -> bool:
        """Check if there are pending instructions.

        Returns:
            True if queue has pending instructions
        """
        with self._lock:
            return not self._queue.empty()

    def clear(self) -> None:
        """Clear all pending instructions."""
        with self._lock:
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break
