from collections.abc import Callable
from typing import Any

# __salt__ is typically a dictionary of all the Salt execution modules available (functions).
__salt__: dict[str, Callable[..., Any]]
