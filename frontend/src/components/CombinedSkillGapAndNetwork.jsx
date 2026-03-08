import React from 'react'
import SkillGapHeatmap from './SkillGapHeatmap'
import NetworkExpansionGraph from './NetworkExpansionGraph'
import './CombinedSkillGapAndNetwork.css'

const CombinedSkillGapAndNetwork = () => {
  return (
    <div className="combined-skill-network-wrapper">
      <SkillGapHeatmap />
      <NetworkExpansionGraph />
    </div>
  )
}

export default CombinedSkillGapAndNetwork
