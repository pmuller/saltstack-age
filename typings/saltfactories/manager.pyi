from typing import Any

from saltfactories.daemons.minion import SaltMinion

class FactoriesManager:
    def salt_minion_daemon(
        self,
        minion_id: str,
        overrides: None | dict[str, Any] = None,
    ) -> SaltMinion: ...
