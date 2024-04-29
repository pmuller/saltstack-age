from pytestshellutils.utils.processes import ProcessResult

class SaltCall:
    def run(
        self,
        function: str,
        *arguments: list[str],
        pillar: None | str = None,
    ) -> ProcessResult: ...
