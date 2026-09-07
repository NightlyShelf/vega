from os import getenv
from pathlib import Path

from ahocorasick import Automaton

from vega.router.model.wakeword_config import AgentModel, WakeWordConfig


class WakeWordDetector:
    """
    Class for detecting WakeWords from content
    """

    def __init__(self):
        """
        Initializes WakeWordDetector. $WAKEWORD_CONFIG environment variable should be set with path to config JSON file.
        """
        config_path: str | None = getenv("WAKEWORD_CONFIG")
        assert config_path is not None

        if not Path(config_path).exists():
            raise FileNotFoundError("WakeWord Config not found")

        with open(config_path, "r") as config_file:
            self._config: WakeWordConfig = WakeWordConfig.model_validate_json(
                config_file.read()
            )
            self._wakewords: list[tuple[int, str]] = [
                (idx, word)
                for idx, agent in enumerate(self._config.agents)
                for word in agent.wakewords
            ]

    def search_wakewords(self, content: str) -> AgentModel | None:
        """
        Searches for wakewords from config
        :param content: Content to search
        :return: Endpoint of the corresponding agent with X-Api-Key header or None if not found
        """
        content: str = content.lower()
        automation: Automaton = Automaton()
        for idx, word in self._wakewords:
            automation.add_word(word, idx)
        automation.make_automaton()
        # TODO: implement multiple wakewords usage
        # (position_found, agent_list_index)
        wakewords_found: list[tuple[int, int]] = list(automation.iter(content))
        if not wakewords_found:
            return None
        else:
            return self._config.agents[wakewords_found[0][1]]
