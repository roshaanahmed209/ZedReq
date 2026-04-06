import React from 'react'
import { sitePath } from '../config/siteUrl'
import './SiteFooter.css'

export default function SiteFooter() {
  return (
    <footer className="footer scroll-reveal">
      <div className="footer-content">
        <div className="footer-section scroll-reveal">
          <h4>Product</h4>
          <ul>
            <li><a href={sitePath('/features')}>Features</a></li>
            <li><a href={sitePath('/pricing')}>Pricing</a></li>
          </ul>
        </div>
        <div className="footer-section scroll-reveal">
          <h4>Company</h4>
          <ul>
            <li><a href={sitePath('/about')}>About</a></li>
            <li><a href={sitePath('/careers')}>Careers</a></li>
            <li><a href={sitePath('/contact')}>Contact</a></li>
          </ul>
        </div>
        <div className="footer-section scroll-reveal">
          <h4>Resources</h4>
          <ul>
            <li><a href={sitePath('/blog')}>Blog</a></li>
            <li><a href={sitePath('/help')}>Help Center</a></li>
            <li><a href={sitePath('/privacy')}>Privacy Policy</a></li>
          </ul>
        </div>
        <div className="footer-section scroll-reveal">
          <h4>Legal</h4>
          <ul>
            <li><a href={sitePath('/terms')}>Terms of Use</a></li>
            <li><a href={sitePath('/privacy')}>Privacy Policy</a></li>
            <li><a href={sitePath('/cookies')}>Cookie Policy</a></li>
          </ul>
        </div>
      </div>
      <div className="footer-bottom scroll-reveal">
        <p>&copy; 2024 ZedReq — All rights reserved.</p>
      </div>
    </footer>
  )
}
