import React from 'react'
import SkillGapHeatmap from './SkillGapHeatmap'
import NetworkExpansionGraph from './NetworkExpansionGraph'
import WaveBackgroundCanvas from './WaveBackgroundCanvas'
import './CombinedSkillGapAndNetwork.css'

const CombinedSkillGapAndNetwork = () => {
  return (
    <div className="combined-skill-network-wrapper">
      <WaveBackgroundCanvas className="wave-bg-canvas-wrap--section" />
      <SkillGapHeatmap />
      <NetworkExpansionGraph />
    </div>
  )
}

export default CombinedSkillGapAndNetwork
