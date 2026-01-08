"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/lib/auth-context"
import { Leaf, ShoppingCart, User, LogOut, ChevronDown } from "lucide-react"
import { useState } from "react"

export function Header() {
  const { user } = useAuth()
  const [isProfileOpen, setIsProfileOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary">
            <Leaf className="w-6 h-6 text-primary-foreground" />
          </div>
          <span className="text-xl font-bold text-foreground">Mokpokpo</span>
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          <Link href="/" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
            Accueil
          </Link>
          <Link
            href="/catalog"
            className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
          >
            Catalogue
          </Link>
          <Link
            href="/about"
            className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
          >
            À propos
          </Link>
          <Link
            href="/contact"
            className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
          >
            Contact
          </Link>
        </nav>

        <div className="flex items-center gap-2">
          <Link href="/cart">
            <Button variant="ghost" size="icon" className="relative">
              <ShoppingCart className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-5 h-5 text-xs flex items-center justify-center bg-primary text-primary-foreground rounded-full">
                3
              </span>
            </Button>
          </Link>

          {user ? (
            <div className="relative">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="flex items-center gap-2"
              >
                <User className="w-5 h-5" />
                <ChevronDown className="w-4 h-4" />
              </Button>

              {isProfileOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-background border border-border rounded-lg shadow-lg py-2 z-50">
                  <div className="px-4 py-2 border-b border-border">
                    <p className="text-sm font-medium text-foreground">{user.email}</p>
                    <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
                  </div>

                  <Link href="/client" className="block">
                    <button className="w-full text-left px-4 py-2 text-sm text-foreground hover:bg-muted transition-colors">
                      Mon dashboard
                    </button>
                  </Link>

                  {user.role === "admin" && (
                    <Link href="/admin" className="block">
                      <button className="w-full text-left px-4 py-2 text-sm text-foreground hover:bg-muted transition-colors">
                        Panel admin
                      </button>
                    </Link>
                  )}

                  {user.role === "commercial" && (
                    <Link href="/commercial" className="block">
                      <button className="w-full text-left px-4 py-2 text-sm text-foreground hover:bg-muted transition-colors">
                        Dashboard commercial
                      </button>
                    </Link>
                  )}

                  {user.role === "stock" && (
                    <Link href="/stock" className="block">
                      <button className="w-full text-left px-4 py-2 text-sm text-foreground hover:bg-muted transition-colors">
                        Gestion stock
                      </button>
                    </Link>
                  )}

                  <div className="border-t border-border">
                    <Link href="/logout" className="block">
                      <button className="w-full text-left px-4 py-2 text-sm text-destructive hover:bg-destructive/10 transition-colors flex items-center gap-2">
                        <LogOut className="w-4 h-4" />
                        Déconnexion
                      </button>
                    </Link>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <Link href="/login">
              <Button variant="ghost" size="icon">
                <User className="w-5 h-5" />
              </Button>
            </Link>
          )}

          <Link href="/catalog">
            <Button className="hidden md:inline-flex">Commander</Button>
          </Link>
        </div>
      </div>
    </header>
  )
}
