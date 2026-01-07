"""Base use case class."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

InputDTO = TypeVar("InputDTO")
OutputDTO = TypeVar("OutputDTO")


class UseCase(ABC, Generic[InputDTO, OutputDTO]):
    """Base class for all use cases."""

    @abstractmethod
    async def execute(self, input_dto: InputDTO) -> OutputDTO:
        """Execute the use case."""
        pass
