import React from 'react'
import privacyPolicyText from '@repoLegal/privacy.txt?raw'
import { LegalPlainDocument } from './LegalPlainDocument'

/** Full Privacy Policy from ZedReq/privacy.txt — used on /privacy, Settings → Privacy Policy, and anywhere this component is mounted. */
export function LegalPrivacyBody() {
  return <LegalPlainDocument text={privacyPolicyText} />
}
