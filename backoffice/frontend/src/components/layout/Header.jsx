import React from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { LogOut, User } from 'lucide-react'
import { Button } from '../ui/button'

const Header = () => {
  const { admin, logout } = useAuth()

  return (
    <header className="h-16 border-b border-border bg-card flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold">Admin Panel</h2>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-sm">
          <User className="h-4 w-4" />
          <span className="font-medium">{admin?.username}</span>
          <span className="text-muted-foreground">({admin?.role})</span>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={logout}
          className="gap-2"
        >
          <LogOut className="h-4 w-4" />
          Logout
        </Button>
      </div>
    </header>
  )
}

export default Header
