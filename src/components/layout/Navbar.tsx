"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Play, Plus } from "lucide-react"
import { cn } from "@/lib/utils"

const navLinks = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/videos", label: "Videos" },
  { href: "/analyze", label: "Analyze" },
  { href: "/settings", label: "Settings" },
]

export function Navbar() {
  const pathname = usePathname()

  return (
    <nav className="border-b border-white/5 bg-[#080a0f]/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
            <Play className="w-3.5 h-3.5 text-white fill-white" />
          </div>
          <span className="font-bold">Videology</span>
        </Link>
        <div className="hidden md:flex items-center gap-6 text-sm text-white/60">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "hover:text-white transition-colors",
                pathname === link.href && "text-white font-medium"
              )}
            >
              {link.label}
            </Link>
          ))}
        </div>
        <Link
          href="/analyze"
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 transition-colors text-sm font-medium"
        >
          <Plus className="w-4 h-4" />
          Analyze Video
        </Link>
      </div>
    </nav>
  )
}