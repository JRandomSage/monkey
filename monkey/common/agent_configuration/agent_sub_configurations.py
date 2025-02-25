from typing import Dict, Tuple

from pydantic import PositiveFloat, conint, validator

from common.base_models import MutableInfectionMonkeyBaseModel
from common.types import NetworkPort

from .validators import validate_ip, validate_subnet_range


class PluginConfiguration(MutableInfectionMonkeyBaseModel):
    """
    A configuration for plugins

    Attributes:
        :param name: Name of the plugin
                     Example: "ransomware"
        :param options: Any other information/configuration fields relevant to the plugin
                        Example: {
                            "encryption": {
                                "enabled": True,
                                "directories": {
                                    "linux_target_dir": "~/this_dir",
                                    "windows_target_dir": "C:\that_dir"
                                },
                            },
                            "other_behaviors": {
                                "readme": True
                            },
                        }
    """

    name: str
    options: Dict


class ScanTargetConfiguration(MutableInfectionMonkeyBaseModel):
    """
    Configuration of network targets to scan and exploit

    Attributes:
        :param blocked_ips: IP's that won't be scanned
                            Example: ("1.1.1.1", "2.2.2.2")
        :param inaccessible_subnets: Subnet ranges that shouldn't be accessible for the agent
                                     Example: ("1.1.1.1", "2.2.2.2/24", "myserver")
        :param scan_my_networks: If true the Agent will scan networks it belongs to
         in addition to the provided subnet ranges
        :param subnets: Subnet ranges to scan
                        Example: ("192.168.1.1-192.168.2.255", "3.3.3.3", "2.2.2.2/24",
                                  "myHostname")
    """

    blocked_ips: Tuple[str, ...]
    inaccessible_subnets: Tuple[str, ...]
    scan_my_networks: bool
    subnets: Tuple[str, ...]

    @validator("blocked_ips", each_item=True)
    def blocked_ips_valid(cls, ip):
        validate_ip(ip)
        return ip

    @validator("inaccessible_subnets", each_item=True)
    def inaccessible_subnets_valid(cls, subnet_range):
        validate_subnet_range(subnet_range)
        return subnet_range

    @validator("subnets", each_item=True)
    def subnets_valid(cls, subnet_range):
        validate_subnet_range(subnet_range)
        return subnet_range


class ICMPScanConfiguration(MutableInfectionMonkeyBaseModel):
    """
    A configuration for ICMP scanning

    Attributes:
        :param timeout: Maximum time in seconds to wait for a response from the target
    """

    timeout: PositiveFloat


class TCPScanConfiguration(MutableInfectionMonkeyBaseModel):
    """
    A configuration for TCP scanning

    Attributes:
        :param timeout: Maximum time in seconds to wait for a response from the target
        :param ports: Ports to scan
    """

    timeout: PositiveFloat
    ports: Tuple[NetworkPort, ...]


class NetworkScanConfiguration(MutableInfectionMonkeyBaseModel):
    """
    A configuration for network scanning

    Attributes:
        :param tcp: Configuration for TCP scanning
        :param icmp: Configuration for ICMP scanning
        :param fingerprinters: Configuration for fingerprinters to run
        :param targets: Configuration for targets to scan
    """

    tcp: TCPScanConfiguration
    icmp: ICMPScanConfiguration
    fingerprinters: Tuple[PluginConfiguration, ...]
    targets: ScanTargetConfiguration


class ExploitationOptionsConfiguration(MutableInfectionMonkeyBaseModel):
    """
    A configuration for exploitation options

    Attributes:
        :param http_ports: HTTP ports to exploit
    """

    http_ports: Tuple[NetworkPort, ...]


class ExploitationConfiguration(MutableInfectionMonkeyBaseModel):
    """
    A configuration for exploitation

    Attributes:
        :param options: Exploitation options shared by all exploiters
        :param brute_force: Configuration for brute force exploiters
        :param vulnerability: Configuration for vulnerability exploiters
    """

    options: ExploitationOptionsConfiguration
    brute_force: Tuple[PluginConfiguration, ...]
    vulnerability: Tuple[PluginConfiguration, ...]


class PropagationConfiguration(MutableInfectionMonkeyBaseModel):
    """
    A configuration for propagation

    Attributes:
        :param maximum_depth: Maximum number of hops allowed to spread from the machine where
                              the attack started i.e. how far to propagate in the network from the
                              first machine
        :param network_scan: Configuration for network scanning
        :param exploitation: Configuration for exploitation
    """

    maximum_depth: conint(ge=0)  # type: ignore[valid-type]
    network_scan: NetworkScanConfiguration
    exploitation: ExploitationConfiguration
