"use client"

import { useEffect } from "react"
import { useSearchParams, useRouter } from "next/navigation"

export function LoginSearchParamsHandler() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const redirectTo = searchParams.get("redirect")

  useEffect(() => {
    // Handler for redirect parameter if needed
    // This component isolates useSearchParams to allow Suspense wrapping
  }, [searchParams, router, redirectTo])

  return null
}
