import React from 'react';
import CollapsibleWellComponent from '../CollapsibleWell';

export function smbReport(issue) {
  return (
    <>
      Change user passwords to a complex one-use password that is not shared with other computers on the network.
      <CollapsibleWellComponent>
        The machine <span className="badge badge-primary">{issue.machine}</span> (<span
          className="badge badge-info" style={{ margin: '2px' }}>{issue.ip_address}</span>) is vulnerable to an <span
            className="badge badge-danger">SMB</span> attack.
        <br />
        The Monkey authenticated over the SMB protocol.
      </CollapsibleWellComponent>
    </>
  );
}
