"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ArrowLeft, Plus, CheckCircle, AlertCircle } from "lucide-react"

interface StockMovement {
  productId: string
  productName: string
  movementType: "entrée" | "sortie" | "récolte" | ""
  quantity: number
  date: string
  notes: string
}

const products = [
  { id: "1", name: "Menthe Poivrée" },
  { id: "2", name: "Gingembre Bio" },
  { id: "3", name: "Basilic Sacré" },
  { id: "4", name: "Curcuma Premium" },
  { id: "5", name: "Aloe Vera" },
  { id: "6", name: "Thé Moringa" },
  { id: "7", name: "Coriandre Frais" },
  { id: "8", name: "Échinacée" },
]

export default function StockMovementPage() {
  const [formData, setFormData] = useState<StockMovement>({
    productId: "",
    productName: "",
    movementType: "",
    quantity: 0,
    date: new Date().toISOString().split("T")[0],
    notes: "",
  })

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [error, setError] = useState("")

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === "quantity" ? (value === "" ? 0 : Number.parseInt(value)) : value,
    }))
    setError("")
  }

  const handleProductChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const productId = e.target.value
    const selected = products.find((p) => p.id === productId)
    setFormData((prev) => ({
      ...prev,
      productId,
      productName: selected?.name || "",
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (!formData.productId || !formData.movementType || formData.quantity <= 0 || !formData.date) {
      setError("Veuillez remplir tous les champs requis")
      return
    }

    setIsSubmitting(true)

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500))

    setIsSubmitted(true)
    setFormData({
      productId: "",
      productName: "",
      movementType: "",
      quantity: 0,
      date: new Date().toISOString().split("T")[0],
      notes: "",
    })

    // Reset after 3 seconds
    setTimeout(() => setIsSubmitted(false), 3000)
    setIsSubmitting(false)
  }

  const getMovementTypeLabel = (type: string) => {
    switch (type) {
      case "entrée":
        return "Entrée de stock"
      case "sortie":
        return "Sortie de stock"
      case "récolte":
        return "Récolte"
      default:
        return ""
    }
  }

  const getMovementTypeColor = (type: string) => {
    switch (type) {
      case "entrée":
        return "bg-green-50 border-green-200"
      case "sortie":
        return "bg-red-50 border-red-200"
      case "récolte":
        return "bg-blue-50 border-blue-200"
      default:
        return "bg-muted border-border"
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <div className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 h-16 flex items-center">
          <Link href="/stock" className="flex items-center gap-2 text-primary hover:text-primary/80">
            <ArrowLeft className="w-4 h-4" />
            Retour au stock
          </Link>
        </div>
      </div>

      <main className="flex-1 py-12 px-4">
        <div className="container mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-foreground mb-2">Nouveau mouvement de stock</h1>
            <p className="text-muted-foreground">Enregistrez une entrée, sortie ou récolte de produit</p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <Card className="p-8">
                {isSubmitted && (
                  <div className="flex gap-4 p-4 bg-green-50 border border-green-200 rounded-lg mb-6">
                    <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-green-900">Mouvement enregistré avec succès!</p>
                      <p className="text-sm text-green-700">Le mouvement de stock a été ajouté à la base de données.</p>
                    </div>
                  </div>
                )}

                {error && (
                  <div className="flex gap-4 p-4 bg-destructive/10 border border-destructive/30 rounded-lg mb-6">
                    <AlertCircle className="w-6 h-6 text-destructive flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-destructive">{error}</p>
                    </div>
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label htmlFor="productId" className="block text-sm font-semibold text-foreground mb-3">
                      Produit *
                    </label>
                    <select
                      id="productId"
                      name="productId"
                      value={formData.productId}
                      onChange={handleProductChange}
                      required
                      className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">-- Sélectionnez un produit --</option>
                      {products.map((product) => (
                        <option key={product.id} value={product.id}>
                          {product.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="movementType" className="block text-sm font-semibold text-foreground mb-3">
                      Type de mouvement *
                    </label>
                    <div className="grid grid-cols-3 gap-3">
                      {["entrée", "sortie", "récolte"].map((type) => (
                        <label
                          key={type}
                          className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                            formData.movementType === type
                              ? "border-primary bg-primary/10"
                              : "border-border hover:border-muted-foreground"
                          }`}
                        >
                          <input
                            type="radio"
                            name="movementType"
                            value={type}
                            checked={formData.movementType === type}
                            onChange={handleInputChange}
                            className="sr-only"
                          />
                          <div className="font-medium text-foreground capitalize">{type}</div>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="quantity" className="block text-sm font-semibold text-foreground mb-3">
                        Quantité (kg) *
                      </label>
                      <input
                        id="quantity"
                        type="number"
                        name="quantity"
                        value={formData.quantity === 0 ? "" : formData.quantity}
                        onChange={handleInputChange}
                        min="0"
                        step="0.1"
                        required
                        placeholder="0"
                        className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>
                    <div>
                      <label htmlFor="date" className="block text-sm font-semibold text-foreground mb-3">
                        Date *
                      </label>
                      <input
                        id="date"
                        type="date"
                        name="date"
                        value={formData.date}
                        onChange={handleInputChange}
                        required
                        className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="notes" className="block text-sm font-semibold text-foreground mb-3">
                      Notes (optionnel)
                    </label>
                    <textarea
                      id="notes"
                      name="notes"
                      value={formData.notes}
                      onChange={handleInputChange}
                      placeholder="Ajoutez des notes sur ce mouvement (localisation, fournisseur, etc.)"
                      rows={4}
                      className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                    />
                  </div>

                  <Button type="submit" className="w-full" size="lg" disabled={isSubmitting}>
                    {isSubmitting ? (
                      <>Enregistrement...</>
                    ) : (
                      <>
                        <Plus className="w-4 h-4 mr-2" />
                        Enregistrer le mouvement
                      </>
                    )}
                  </Button>
                </form>
              </Card>
            </div>

            <div>
              <Card className="p-6 sticky top-24">
                <h3 className="font-bold text-foreground mb-4">Résumé du mouvement</h3>
                <div className="space-y-4">
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Produit</p>
                    <p className="font-semibold text-foreground">{formData.productName || "Non sélectionné"}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Type</p>
                    <p
                      className={`font-semibold px-3 py-1 rounded-full inline-block text-sm ${
                        formData.movementType
                          ? getMovementTypeColor(formData.movementType)
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {formData.movementType ? getMovementTypeLabel(formData.movementType) : "Non sélectionné"}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Quantité</p>
                    <p className="font-semibold text-foreground">{formData.quantity || 0} kg</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Date</p>
                    <p className="font-semibold text-foreground">
                      {formData.date
                        ? new Date(formData.date).toLocaleDateString("fr-BJ", {
                            year: "numeric",
                            month: "long",
                            day: "numeric",
                          })
                        : "Non sélectionnée"}
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-6 mt-6 bg-muted/50">
                <h3 className="font-bold text-foreground mb-3">Types de mouvement</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex gap-2">
                    <span className="font-bold text-green-600">↓</span>
                    <span>
                      <span className="font-semibold text-foreground">Entrée</span> - Stock entrant (achat, réception)
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-bold text-red-600">↑</span>
                    <span>
                      <span className="font-semibold text-foreground">Sortie</span> - Stock sortant (vente, utilisation)
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-bold text-blue-600">◉</span>
                    <span>
                      <span className="font-semibold text-foreground">Récolte</span> - Production interne
                    </span>
                  </li>
                </ul>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
