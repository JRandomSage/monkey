import React from 'react';
import CollapsibleWellComponent from '../CollapsibleWell';
import {getMachineByAgent, getMachineByIP, getMachineHostname, getMachineIPs} from '../../../utils/ServerUtils';


export function getAllTunnels(agents, machines) {
  let islandIPs = [];
  for (let machine of machines) {
    if (machine.island === true) {
      islandIPs = islandIPs.concat(
        ...getMachineIPs(machine)
      );
    }
  }

  let tunnels = [];
  for (let agent of agents) {
    if (!islandIPs.includes(agent.cc_server.ip)) {
      let agentMachine = getMachineByAgent(agent, machines);
      let tunnelMachine = getMachineByIP(agent.cc_server.ip, machines);

      if ((agentMachine !== null) && (tunnelMachine !== null)) {
        let agentMachineInfo = {
          'id': agentMachine.id,
          'ip': getMachineIPs(agentMachine)[0],
          'hostname': getMachineHostname(agentMachine)
        };

        let tunnelMachineInfo = {
          'id': tunnelMachine.id,
          'ip': agent.cc_server.ip,
          'hostname': getMachineHostname(tunnelMachine)
        };

        tunnels.push({
          'agent_machine': agentMachineInfo,
          'tunnel_machine': tunnelMachineInfo
        });
      }
    }
  }
  return tunnels;
}

export function tunnelIssueOverview(allTunnels) {
  if (allTunnels.length > 0) {
    return ( <li key="tunnel">Weak segmentation -
      Machines were able to relay communications over unused ports.</li>)
  } else {
    return null;
  }
}

export function tunnelIssueReportByMachine(machineId, allTunnels) {
  if (allTunnels.length > 0) {
    let tunnelIssuesByMachine = getTunnelIssuesByMachine(machineId, allTunnels);

    if (tunnelIssuesByMachine.length > 0) {
      return (
        <>
          Use micro-segmentation policies to disable communication other than the required.
          <CollapsibleWellComponent>
            Machines are not locked down at port level.
            Network tunnels were set up between the following.
            <ul>
              {tunnelIssuesByMachine}
            </ul>
          </CollapsibleWellComponent>
        </>
      );
    }
  }

  return null;
}

function machineNameComponent(tunnelMachineInfo) {
  return <>
      <span className="badge badge-primary">{tunnelMachineInfo.hostname}</span> (
      <span className="badge badge-info" style={{ margin: '2px' }}>{tunnelMachineInfo.ip}</span>)</>
}

function getTunnelIssuesByMachine(machineId, allTunnels) {
  let tunnelIssues = [];

  for (let tunnel of allTunnels) {
    if (tunnel.agent_machine.id === machineId || tunnel.tunnel_machine.id === machineId) {
      let agentMachineNameComponent = machineNameComponent(tunnel.agent_machine);
      let tunnelMachineNameComponent = machineNameComponent(tunnel.tunnel_machine);

      tunnelIssues.push(
        <li key={tunnel.agent_machine+tunnel.tunnel_machine}>
          from {agentMachineNameComponent} to {tunnelMachineNameComponent}
        </li>
      );
    }
  }

  return tunnelIssues;
}
