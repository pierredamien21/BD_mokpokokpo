"use client"

import { useState } from "react"
import Link from "next/link"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ArrowLeft, Heart, Share2 } from "lucide-react"

interface ProductDetailsPageProps {
  params: {
    id: string
  }
}

const productDetails: Record<string, any> = {
  "1": {
    id: 1,
    name: "Menthe Poivrée",
    category: "Herbes Aromatiques",
    price: 2500,
    image: "/menthe-poivr-e-plante.jpg",
    availability: true,
    description: "Herbe aromatique fraîche et revigorante cultivée biologiquement",
    longDescription:
      "La menthe poivrée est une herbe aromatique polyvalente aux multiples vertus. Fraîche et vivifiante, elle est parfaite pour préparer des tisanes, aromatiser vos plats ou créer des boissons rafraîchissantes.",
    benefits: ["Aide à la digestion", "Rafraîchit l'haleine", "Réduit les migraines", "Propriétés antispasmodiques"],
    usage:
      "Infusion: 1-2 feuilles fraîches par tasse d'eau chaude. Cuisine: À utiliser fraîche ou séchée pour aromatiser plats et boissons.",
    storage:
      "Conservez au frais dans un endroit sombre et sec. Les feuilles fraîches se conservent quelques jours au réfrigérateur.",
    origin: "Cultivée localement à la ferme Mokpokpo",
    quantity: 100,
  },
  "2": {
    id: 2,
    name: "Gingembre Bio",
    category: "Superaliments",
    price: 3500,
    image: "/gingembre-bio-racine.jpg",
    availability: true,
    description: "Gingembre frais cultivé biologiquement sans pesticides",
    longDescription:
      "Le gingembre bio est un superaliment aux propriétés thermogéniques exceptionnelles. Riche en antioxydants et nutriments essentiels, il stimule le métabolisme et renforce l'immunité.",
    benefits: [
      "Anti-inflammatoire puissant",
      "Améliore la circulation sanguine",
      "Soutient la digestion",
      "Riche en antioxydants",
    ],
    usage: "Frais: À râper ou trancher pour infusions, cuisines. Poudre: À utiliser dans les thés et recettes.",
    storage: "Au frais dans un endroit sec. La racine fraîche se conserve plusieurs semaines.",
    origin: "Cultivé biologiquement à la ferme Mokpokpo",
    quantity: 50,
  },
}

export default function ProductDetailsPage({ params }: ProductDetailsPageProps) {
  const [isFavorite, setIsFavorite] = useState(false)
  const [quantity, setQuantity] = useState(1)

  const product = productDetails[params.id] || productDetails["1"]

  const handleAddToCart = () => {
    // Redirect to login if not authenticated
    window.location.href = "/login"
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-8">
          <Link href="/catalog" className="flex items-center gap-2 text-primary hover:text-primary/80 mb-8">
            <ArrowLeft className="w-4 h-4" />
            Retour au catalogue
          </Link>

          <div className="grid md:grid-cols-2 gap-8 mb-12">
            <div>
              <div className="bg-muted rounded-lg overflow-hidden mb-4">
                <img
                  src={product.image || "/placeholder.svg"}
                  alt={product.name}
                  className="w-full h-96 object-cover"
                />
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="icon" onClick={() => setIsFavorite(!isFavorite)}>
                  <Heart className={`w-5 h-5 ${isFavorite ? "fill-destructive text-destructive" : ""}`} />
                </Button>
                <Button variant="outline" size="icon">
                  <Share2 className="w-5 h-5" />
                </Button>
              </div>
            </div>

            <div className="flex flex-col">
              <div className="mb-4">
                <span className="text-sm text-muted-foreground">{product.category}</span>
                <h1 className="text-4xl font-bold text-foreground my-2">{product.name}</h1>
                <p className="text-lg text-muted-foreground">{product.description}</p>
              </div>

              <Card className="p-6 mb-6 bg-muted/50">
                <div className="flex items-baseline gap-2 mb-4">
                  <span className="text-4xl font-bold text-primary">{product.price.toLocaleString("fr-BJ")}</span>
                  <span className="text-muted-foreground">FCFA</span>
                </div>
                <div className="flex items-center gap-4 mb-6">
                  <span className="text-sm font-medium text-foreground">Quantité:</span>
                  <div className="flex items-center border border-border rounded-md">
                    <button
                      onClick={() => setQuantity(Math.max(1, quantity - 1))}
                      className="px-3 py-2 text-foreground hover:bg-muted"
                    >
                      -
                    </button>
                    <span className="px-4 py-2 text-foreground">{quantity}</span>
                    <button
                      onClick={() => setQuantity(quantity + 1)}
                      className="px-3 py-2 text-foreground hover:bg-muted"
                    >
                      +
                    </button>
                  </div>
                </div>
                <Button className="w-full mb-3" size="lg" onClick={handleAddToCart} disabled={!product.availability}>
                  {product.availability ? "Ajouter au panier" : "Indisponible"}
                </Button>
                <Button variant="outline" className="w-full bg-transparent" size="lg">
                  Acheter maintenant
                </Button>
              </Card>

              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-foreground mb-2">Disponibilité</h3>
                  <p className="text-green-600">{product.availability ? "En stock" : "Indisponible"}</p>
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-2">Origine</h3>
                  <p className="text-muted-foreground">{product.origin}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-8 mb-12">
            <Card className="p-6">
              <h2 className="text-2xl font-bold text-foreground mb-4">Description détaillée</h2>
              <p className="text-muted-foreground mb-4">{product.longDescription}</p>

              <h3 className="font-semibold text-foreground mb-2">Bienfaits</h3>
              <ul className="list-disc pl-5 space-y-1 text-muted-foreground mb-4">
                {product.benefits.map((benefit: string, i: number) => (
                  <li key={i}>{benefit}</li>
                ))}
              </ul>
            </Card>

            <Card className="p-6">
              <h2 className="text-2xl font-bold text-foreground mb-4">Utilisation</h2>
              <p className="text-muted-foreground mb-4">{product.usage}</p>

              <h3 className="font-semibold text-foreground mb-2">Conservation</h3>
              <p className="text-muted-foreground">{product.storage}</p>
            </Card>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
