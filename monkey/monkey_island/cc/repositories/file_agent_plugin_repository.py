from common.agent_plugins import AgentPlugin, AgentPluginType

from . import IAgentPluginRepository, IFileRepository, RetrievalError
from .plugin_archive_parser import parse_plugin


class FileAgentPluginRepository(IAgentPluginRepository):
    """
    A repository for retrieving agent plugins.
    """

    def __init__(self, plugin_file_repository: IFileRepository):
        """
        :param plugin_file_repository: IFileRepository containing the plugins
        """
        self._plugin_file_repository = plugin_file_repository

    def get_plugin(self, plugin_type: AgentPluginType, name: str) -> AgentPlugin:
        plugin_file_name = f"{name}-{plugin_type.value.lower()}.tar"

        try:
            with self._plugin_file_repository.open_file(plugin_file_name) as f:
                return parse_plugin(f)
        except ValueError as err:
            raise RetrievalError(f"Error retrieving the agent plugin {plugin_file_name}: {err}")
