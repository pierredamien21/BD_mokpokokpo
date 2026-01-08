import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ShoppingCart, Heart } from "lucide-react"

const plants = [
  {
    id: 1,
    name: "Basilic Sacré",
    scientificName: "Ocimum tenuiflorum",
    price: "2500 FCFA",
    category: "Plantes Médicinales",
    stock: 45,
    image: "/holy-basil-plant-in-pot.jpg",
  },
  {
    id: 2,
    name: "Moringa",
    scientificName: "Moringa oleifera",
    price: "3500 FCFA",
    category: "Superaliments",
    stock: 32,
    image: "/moringa-tree-seedling-in-pot.jpg",
  },
  {
    id: 3,
    name: "Aloe Vera",
    scientificName: "Aloe barbadensis",
    price: "2000 FCFA",
    category: "Plantes Médicinales",
    stock: 58,
    image: "/aloe-vera-succulent-plant.jpg",
  },
  {
    id: 4,
    name: "Citronnelle",
    scientificName: "Cymbopogon citratus",
    price: "1500 FCFA",
    category: "Herbes Aromatiques",
    stock: 67,
    image: "/lemongrass-plant-in-garden.jpg",
  },
  {
    id: 5,
    name: "Gingembre",
    scientificName: "Zingiber officinale",
    price: "1800 FCFA",
    category: "Épices",
    stock: 41,
    image: "/ginger-plant-with-rhizome.jpg",
  },
  {
    id: 6,
    name: "Menthe Poivrée",
    scientificName: "Mentha piperita",
    price: "1200 FCFA",
    category: "Herbes Aromatiques",
    stock: 73,
    image: "/peppermint-plant-in-pot.jpg",
  },
]

export function PlantCatalog() {
  return (
    <section className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="flex flex-col gap-4 mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-balance">Notre Catalogue de Plantes</h2>
          <p className="text-lg text-muted-foreground max-w-2xl">
            Des plantes sélectionnées avec soin pour leurs vertus et leur qualité exceptionnelle
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {plants.map((plant) => (
            <Card key={plant.id} className="group overflow-hidden hover:shadow-lg transition-all">
              <CardContent className="p-0">
                <div className="relative aspect-square overflow-hidden bg-muted">
                  <img
                    src={plant.image || "/placeholder.svg"}
                    alt={plant.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <Button
                    size="icon"
                    variant="secondary"
                    className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Heart className="w-4 h-4" />
                  </Button>
                  <Badge className="absolute top-3 left-3 bg-background/90 text-foreground hover:bg-background/90">
                    {plant.category}
                  </Badge>
                </div>

                <div className="p-4 space-y-3">
                  <div>
                    <h3 className="font-semibold text-lg text-foreground">{plant.name}</h3>
                    <p className="text-sm text-muted-foreground italic">{plant.scientificName}</p>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold text-primary">{plant.price}</p>
                      <p className="text-xs text-muted-foreground">Stock: {plant.stock} unités</p>
                    </div>
                  </div>
                </div>
              </CardContent>

              <CardFooter className="p-4 pt-0">
                <Button className="w-full" size="lg">
                  <ShoppingCart className="w-4 h-4 mr-2" />
                  Ajouter au panier
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>

        <div className="mt-12 text-center">
          <Button size="lg" variant="outline">
            Voir tout le catalogue
          </Button>
        </div>
      </div>
    </section>
  )
}
