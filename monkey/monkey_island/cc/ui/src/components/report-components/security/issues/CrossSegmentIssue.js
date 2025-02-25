import React from 'react';
import CollapsibleWellComponent from '../CollapsibleWell';
import { generateInfoBadges } from './utils';

export function crossSegmentIssueOverview() {
  return (<li key="segmentation">Weak segmentation - Machines from
    different segments are able to communicate.</li>)
}

export function crossSegmentIssueReport(crossSegmentIssue) {
  let crossSegmentIssueOverview = 'Communication possible from '
    + `${crossSegmentIssue['source_subnet']} to ${crossSegmentIssue['target_subnet']}`;

  return (
    <li key={crossSegmentIssueOverview}>
      {crossSegmentIssueOverview}
      <CollapsibleWellComponent>
        <ul className='cross-segment-issues'>
          {crossSegmentIssue['issues'].map(
            issue => getCrossSegmentIssueListItem(issue)
          )}
        </ul>
      </CollapsibleWellComponent>
    </li>
  );
}

export function getCrossSegmentIssueListItem(issue) {
  if (issue['is_self']) {
    return getCrossSegmentSingleHostMessage(issue);
  }

  return getCrossSegmentMultiHostMessage(issue);
}

export function getCrossSegmentSingleHostMessage(issue) {
  return (
    <li key={issue['hostname']}>
      {`Machine ${issue['hostname']} has both ips: ${issue['source']} and ${issue['target']}`}
    </li>
  );
}

export function getCrossSegmentMultiHostMessage(issue) {
  return (
    <li key={issue['source'] + issue['target']}>
      IP {issue['source']} ({issue['hostname']}) was able to communicate with
      IP {issue['target']} using:
      <ul>
        {getScanTypeListItems(issue)}
        {getCrossSegmentServiceListItems(issue)}
      </ul>
    </li>
  );
}

export function getScanTypeListItems(issue) {
  let scan_type_list_items = [];

  for (const scan_type of issue['types']) {
    scan_type_list_items.push(
      <li key={scan_type}>{scan_type}</li>
    );
  }

  return scan_type_list_items;
}

export function getCrossSegmentServiceListItems(issue) {
  let service_list_items = [];

  for (const [service, info] of Object.entries(issue['services'])) {
    service_list_items.push(
      <li key={service}>
        <span className='cross-segment-service'>{service}</span> ({info})
      </li>
    );
  }

  return service_list_items;
}

export function islandCrossSegmentIssueReport(issue) {
  return (
    <>
      Segment your network and make sure there is no communication between machines from different segments.
      <CollapsibleWellComponent>
        The network can probably be segmented. A monkey instance on <span
          className="badge badge-primary">{issue.machine}</span> in the
        networks {generateInfoBadges(issue.networks)}
        could directly access the Monkey Island server in the
        networks {generateInfoBadges(issue.server_networks)}.
      </CollapsibleWellComponent>
    </>
  );
}
