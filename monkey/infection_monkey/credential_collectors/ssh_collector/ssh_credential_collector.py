import logging
from typing import Sequence

from common.credentials import Credentials
from common.event_queue import IAgentEventQueue
from infection_monkey.credential_collectors.ssh_collector import ssh_handler
from infection_monkey.i_puppet import ICredentialCollector

logger = logging.getLogger(__name__)


class SSHCredentialCollector(ICredentialCollector):
    """
    SSH keys credential collector
    """

    def __init__(self, agent_event_queue: IAgentEventQueue):
        self._agent_event_queue = agent_event_queue

    def collect_credentials(self, _options=None) -> Sequence[Credentials]:
        logger.info("Started scanning for SSH credentials")
        ssh_info = ssh_handler.get_ssh_info(self._agent_event_queue)
        logger.info("Finished scanning for SSH credentials")

        return ssh_handler.to_credentials(ssh_info)
