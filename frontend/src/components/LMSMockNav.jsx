import { Home, Users, Briefcase, MessageSquare, Bell, Search, LogOut } from 'lucide-react';
import '../css/components/LMSMock.css';

const navItems = [
  { icon: Home, label: 'Home' },
  { icon: Users, label: 'Network' },
  { icon: Briefcase, label: 'Jobs' },
  { icon: MessageSquare, label: 'Messages' },
  { icon: Bell, label: 'Notifications', active: true },
];

export default function LMSMockNav() {
  return (
    <header className="lms-mock__nav">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <span className="lms-mock__brand">ZedReq</span>
        <Search size={15} className="lms-mock__nav-icon" />
      </div>

      <nav className="lms-mock__nav-links" aria-label="App navigation">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.label}
              className={`lms-mock__nav-link${item.active ? ' is-active' : ''}`}
            >
              <Icon size={15} />
              <span>{item.label}</span>
            </div>
          );
        })}
      </nav>

      <button type="button" className="lms-mock__logout">
        Logout <LogOut size={11} />
      </button>
    </header>
  );
}
