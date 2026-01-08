"use client"

import { useState } from "react"
import Link from "next/link"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Search } from "lucide-react"

interface Plant {
  id: number
  name: string
  category: "plantes-medicinales" | "herbes-aromatiques" | "superaliments" | "epices"
  price: number
  image: string
  availability: boolean
  description: string
}

const plants: Plant[] = [
  {
    id: 1,
    name: "Menthe Poivrée",
    category: "herbes-aromatiques",
    price: 2500,
    image: "/menthe-poivr-e-plante.jpg",
    availability: true,
    description: "Herbe aromatique fraîche et revigorante",
  },
  {
    id: 2,
    name: "Gingembre Bio",
    category: "superaliments",
    price: 3500,
    image: "/gingembre-bio-racine.jpg",
    availability: true,
    description: "Gingembre frais cultivé biologiquement",
  },
  {
    id: 3,
    name: "Basilic Sacré",
    category: "plantes-medicinales",
    price: 2000,
    image: "/basilic-sacr--tulsi.jpg",
    availability: true,
    description: "Plante médicinale ayurvédique adaptogène",
  },
  {
    id: 4,
    name: "Curcuma Premium",
    category: "epices",
    price: 4000,
    image: "/curcuma-premium-poudre.jpg",
    availability: true,
    description: "Épice précieuse anti-inflammatoire",
  },
  {
    id: 5,
    name: "Aloe Vera",
    category: "plantes-medicinales",
    price: 5000,
    image: "/aloe-vera-plante-grasse.jpg",
    availability: true,
    description: "Plante médicinale polyvalente",
  },
  {
    id: 6,
    name: "Thé Moringa",
    category: "superaliments",
    price: 3000,
    image: "/moringa-th--feuilles.jpg",
    availability: true,
    description: "Superfood nutritif aux multiples bienfaits",
  },
  {
    id: 7,
    name: "Coriandre Frais",
    category: "herbes-aromatiques",
    price: 1500,
    image: "/coriandre-herbe-fra-che.jpg",
    availability: false,
    description: "Herbe aromatique pour la cuisine",
  },
  {
    id: 8,
    name: "Échinacée",
    category: "plantes-medicinales",
    price: 2800,
    image: "/-chinac-e-fleur-pourpre.jpg",
    availability: true,
    description: "Plante médicinale renforçant l'immunité",
  },
]

const categories = [
  { value: "plantes-medicinales", label: "Plantes Médicinales" },
  { value: "herbes-aromatiques", label: "Herbes Aromatiques" },
  { value: "superaliments", label: "Superaliments" },
  { value: "epices", label: "Épices" },
]

export default function CatalogPage() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")

  const filteredPlants = plants.filter((plant) => {
    const matchCategory = !selectedCategory || plant.category === selectedCategory
    const matchSearch = plant.name.toLowerCase().includes(searchQuery.toLowerCase())
    return matchCategory && matchSearch
  })

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-12">
          <div className="mb-12">
            <h1 className="text-4xl font-bold text-foreground mb-4">Catalogue Complet</h1>
            <p className="text-muted-foreground text-lg">Découvrez toutes nos plantes et produits naturels</p>
          </div>

          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <div className="md:col-span-1">
              <div className="sticky top-20">
                <h3 className="font-semibold text-foreground mb-4">Catégories</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => setSelectedCategory(null)}
                    className={`block w-full text-left px-4 py-2 rounded-md transition-colors ${
                      selectedCategory === null
                        ? "bg-primary text-primary-foreground"
                        : "text-foreground hover:bg-muted"
                    }`}
                  >
                    Tous les produits
                  </button>
                  {categories.map((cat) => (
                    <button
                      key={cat.value}
                      onClick={() => setSelectedCategory(cat.value)}
                      className={`block w-full text-left px-4 py-2 rounded-md transition-colors ${
                        selectedCategory === cat.value
                          ? "bg-primary text-primary-foreground"
                          : "text-foreground hover:bg-muted"
                      }`}
                    >
                      {cat.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="md:col-span-3">
              <div className="mb-8">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Rechercher une plante..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredPlants.length > 0 ? (
                  filteredPlants.map((plant) => (
                    <Link key={plant.id} href={`/catalog/${plant.id}`}>
                      <Card className="h-full flex flex-col hover:shadow-lg transition-shadow cursor-pointer overflow-hidden">
                        <div className="relative w-full h-48 bg-muted">
                          <img
                            src={plant.image || "/placeholder.svg"}
                            alt={plant.name}
                            className="w-full h-full object-cover"
                          />
                          {!plant.availability && (
                            <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                              <span className="text-white font-semibold">Indisponible</span>
                            </div>
                          )}
                        </div>
                        <div className="p-4 flex flex-col flex-1">
                          <h3 className="font-semibold text-foreground mb-2">{plant.name}</h3>
                          <p className="text-sm text-muted-foreground mb-4 flex-1">{plant.description}</p>
                          <div className="flex items-center justify-between">
                            <span className="text-lg font-bold text-primary">
                              {plant.price.toLocaleString("fr-BJ")} FCFA
                            </span>
                            <Button
                              size="sm"
                              disabled={!plant.availability}
                              onClick={(e) => {
                                e.preventDefault()
                                // Will redirect to login if not authenticated
                              }}
                            >
                              Commander
                            </Button>
                          </div>
                        </div>
                      </Card>
                    </Link>
                  ))
                ) : (
                  <div className="col-span-full text-center py-12">
                    <p className="text-muted-foreground">Aucun produit ne correspond à votre recherche</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
