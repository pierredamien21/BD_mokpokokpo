"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { CommercialDashboard } from "@/components/commercial/commercial-dashboard"

export default function CommercialPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()

  useEffect(() => {
    if (!isLoading && (!user || user.role !== "commercial")) {
      router.push("/login?redirect=/commercial")
    }
  }, [user, isLoading, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Chargement...</p>
      </div>
    )
  }

  if (!user || user.role !== "commercial") {
    return null
  }

  return <CommercialDashboard />
}
