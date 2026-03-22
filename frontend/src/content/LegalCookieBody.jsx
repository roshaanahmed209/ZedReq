import React from 'react'
import { sitePath } from '../config/siteUrl'
import { ZEDREQ_EMAIL, zedreqMailto } from '../config/contact'

/** Cookie policy for /cookies page. */
export function LegalCookieBody() {
  return (
    <>
      <p className="get-started-modal-updated"><strong>Last Updated:</strong> February 2026</p>
      <p>
        This Cookie Policy explains how ZedReq (&quot;we&quot;, &quot;us&quot;) uses cookies and similar technologies when you visit or use our website and services. It should be read together with our{' '}
        <a href={sitePath('/privacy')} className="get-started-modal-email">Privacy Policy</a>.
      </p>

      <h3>1. What are cookies?</h3>
      <p>
        Cookies are small text files stored on your device when you visit a site. They help us recognize your browser, keep you signed in, remember preferences, and understand how the service is used.
      </p>

      <h3>2. How we use cookies</h3>
      <p>We may use cookies and similar technologies to:</p>
      <ul>
        <li><strong>Essential:</strong> operate the site, authentication, security, and load balancing</li>
        <li><strong>Functional:</strong> remember settings such as language or display preferences</li>
        <li><strong>Analytics:</strong> measure traffic and improve product experience (often in aggregated form)</li>
      </ul>

      <h3>3. Third-party cookies</h3>
      <p>
        Some features rely on trusted providers (for example hosting, payments, or analytics). Those providers may set their own cookies subject to their policies.
      </p>

      <h3>4. Your choices</h3>
      <p>
        You can control or delete cookies through your browser settings. Blocking essential cookies may affect sign-in and core functionality. Where applicable, we may also show a cookie preference control in the product.
      </p>

      <h3>5. Contact</h3>
      <p>
        Questions about this policy: <a href={zedreqMailto()} className="get-started-modal-email">{ZEDREQ_EMAIL}</a>
      </p>
    </>
  )
}
