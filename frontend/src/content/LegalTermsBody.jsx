import React from 'react'
import termsOfUseText from '@repoLegal/terms.txt?raw'
import { LegalPlainDocument } from './LegalPlainDocument'

/** Full Terms of Use from ZedReq/terms.txt — used on /terms, Settings → Terms of Use, and anywhere this component is mounted. */
export function LegalTermsBody() {
  return <LegalPlainDocument text={termsOfUseText} />
}
