import React from 'react'
import NetworkExpansionGraph from './NetworkExpansionGraph'
import JobDiscoveryFlow from './JobDiscoveryFlow'
import './CombinedNetworkAndJobFlow.css'

const CombinedNetworkAndJobFlow = () => {
  return (
    <div className="combined-sections-wrapper">
      <NetworkExpansionGraph />
      <JobDiscoveryFlow />
    </div>
  )
}

export default CombinedNetworkAndJobFlow
