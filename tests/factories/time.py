from dataclasses import dataclass


@dataclass(slots=True)
class FakeTimeSource:
    current_ms: int = 0

    def now_ms(self) -> int:
        return self.current_ms

    def advance(self, milliseconds: int) -> None:
        self.current_ms += milliseconds
