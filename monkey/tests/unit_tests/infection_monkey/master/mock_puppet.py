import logging
import threading
from typing import Dict, Sequence

from common import OperatingSystem
from common.agent_plugins import AgentPluginType
from common.credentials import Credentials, LMHash, Password, SSHKeypair, Username
from common.types import PingScanData, PortStatus
from infection_monkey.i_puppet import ExploiterResultData, FingerprintData, IPuppet, PortScanData
from infection_monkey.model import VictimHost

DOT_1 = "10.0.0.1"
DOT_2 = "10.0.0.2"
DOT_3 = "10.0.0.3"
DOT_4 = "10.0.0.4"

logger = logging.getLogger()


class MockPuppet(IPuppet):
    def load_plugin(self, plugin_name: str, plugin: object, plugin_type: AgentPluginType) -> None:
        logger.debug(f"load_plugin({plugin}, {plugin_type})")

    def run_credential_collector(self, name: str, options: Dict) -> Sequence[Credentials]:
        logger.debug(f"run_credential_collector({name})")

        if name == "SSHCollector":
            ssh_credentials = [
                Credentials(
                    identity=Username(username="m0nk3y"),
                    secret=SSHKeypair(private_key="Public_Key_0", public_key="Private_Key_0"),
                ),
                Credentials(
                    identity=Username(username="m0nk3y"),
                    secret=SSHKeypair(private_key="Public_Key_1", public_key="Private_Key_1"),
                ),
            ]
            return ssh_credentials
        elif name == "MimikatzCollector":
            windows_credentials = [
                Credentials(
                    identity=Username(username="test_user"), secret=Password(password="1234")
                ),
                Credentials(
                    identity=Username(username="test_user"), secret=LMHash(lm_hash="DEADBEEF")
                ),
            ]
            return windows_credentials

        return []

    def ping(self, host: str, timeout: float = 1) -> PingScanData:
        logger.debug(f"run_ping({host}, {timeout})")
        if host == DOT_1:
            return PingScanData(True, OperatingSystem.WINDOWS)

        if host == DOT_2:
            return PingScanData(False, None)

        if host == DOT_3:
            return PingScanData(True, OperatingSystem.LINUX)

        if host == DOT_4:
            return PingScanData(False, None)

        return PingScanData(False, None)

    def scan_tcp_ports(
        self, host: str, ports: Sequence[int], timeout: float = 3
    ) -> Dict[int, PortScanData]:
        logger.debug(f"run_scan_tcp_port({host}, {ports}, {timeout})")
        dot_1_results = {
            22: PortScanData(22, PortStatus.CLOSED, None, None),
            445: PortScanData(445, PortStatus.OPEN, "SMB BANNER", "tcp-445"),
            3389: PortScanData(3389, PortStatus.OPEN, "", "tcp-3389"),
        }
        dot_3_results = {
            22: PortScanData(22, PortStatus.OPEN, "SSH BANNER", "tcp-22"),
            443: PortScanData(443, PortStatus.OPEN, "HTTPS BANNER", "tcp-443"),
            3389: PortScanData(3389, PortStatus.CLOSED, "", None),
        }

        if host == DOT_1:
            return {port: dot_1_results.get(port, _get_empty_results(port)) for port in ports}

        if host == DOT_3:
            return {port: dot_3_results.get(port, _get_empty_results(port)) for port in ports}

        return {port: _get_empty_results(port) for port in ports}

    def fingerprint(
        self,
        name: str,
        host: str,
        ping_scan_data: PingScanData,
        port_scan_data: Dict[int, PortScanData],
        options: Dict,
    ) -> FingerprintData:
        logger.debug(f"fingerprint({name}, {host})")
        empty_fingerprint_data = FingerprintData(None, None, {})

        dot_1_results = {
            "SMBFinger": FingerprintData(
                "windows", "vista", {"tcp-445": {"name": "smb_service_name"}}
            )
        }

        dot_3_results = {
            "SSHFinger": FingerprintData(
                "linux", "ubuntu", {"tcp-22": {"name": "SSH", "banner": "SSH BANNER"}}
            ),
            "HTTPFinger": FingerprintData(
                None,
                None,
                {
                    "tcp-80": {"name": "http", "data": ("SERVER_HEADERS", False)},
                    "tcp-443": {"name": "http", "data": ("SERVER_HEADERS_2", True)},
                },
            ),
        }

        if host == DOT_1:
            return dot_1_results.get(name, empty_fingerprint_data)

        if host == DOT_3:
            return dot_3_results.get(name, empty_fingerprint_data)

        return empty_fingerprint_data

    def exploit_host(
        self,
        name: str,
        host: VictimHost,
        current_depth: int,
        servers: Sequence[str],
        options: Dict,
        interrupt: threading.Event,
    ) -> ExploiterResultData:
        logger.debug(f"exploit_hosts({name}, {host}, {options})")
        info_wmi = {
            "display_name": "WMI",
            "started": "2021-11-25T15:57:06.307696",
            "finished": "2021-11-25T15:58:33.788238",
            "vulnerable_urls": [],
            "vulnerable_ports": [],
            "executed_cmds": [
                {
                    "cmd": "/tmp/monkey m0nk3y -s 10.10.10.10:5000 -d 1 >git s /dev/null 2>&1 &",
                    "powershell": True,
                }
            ],
        }
        info_ssh = {
            "display_name": "SSH",
            "started": "2021-11-25T15:57:06.307696",
            "finished": "2021-11-25T15:58:33.788238",
            "vulnerable_urls": [],
            "vulnerable_ports": [22],
            "executed_cmds": [],
        }

        successful_exploiters = {
            DOT_1: {
                "ZerologonExploiter": ExploiterResultData(
                    False, False, OperatingSystem.WINDOWS.value, {}, "Zerologon failed"
                ),
                "SSHExploiter": ExploiterResultData(
                    False,
                    False,
                    OperatingSystem.LINUX.value,
                    info_ssh,
                    "Failed exploiting",
                ),
                "WmiExploiter": ExploiterResultData(
                    True, True, OperatingSystem.WINDOWS.value, info_wmi
                ),
            },
            DOT_3: {
                "PowerShellExploiter": ExploiterResultData(
                    False,
                    False,
                    OperatingSystem.WINDOWS.value,
                    info_wmi,
                    "PowerShell Exploiter Failed",
                ),
                "SSHExploiter": ExploiterResultData(
                    False,
                    False,
                    OperatingSystem.LINUX.value,
                    info_ssh,
                    "Failed exploiting",
                ),
                "ZerologonExploiter": ExploiterResultData(
                    True, False, OperatingSystem.WINDOWS.value, {}
                ),
            },
        }

        try:
            return successful_exploiters[host.ip_addr][name]
        except KeyError:
            return ExploiterResultData(
                False,
                False,
                OperatingSystem.LINUX.value,
                {},
                f"{name} failed for host {host}",
            )

    def run_payload(self, name: str, options: Dict, interrupt: threading.Event):
        logger.debug(f"run_payload({name}, {options})")

    def cleanup(self) -> None:
        print("Cleanup called!")
        pass


def _get_empty_results(port: int):
    return PortScanData(port, PortStatus.CLOSED, None, None)
