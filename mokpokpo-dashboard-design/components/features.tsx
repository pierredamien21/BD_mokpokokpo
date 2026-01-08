import { Card, CardContent } from "@/components/ui/card"
import { Leaf, Truck, Shield, Users } from "lucide-react"

const features = [
  {
    icon: Leaf,
    title: "100% Naturel",
    description: "Toutes nos plantes sont cultivées sans pesticides ni produits chimiques",
  },
  {
    icon: Truck,
    title: "Livraison Rapide",
    description: "Livraison dans tout le Bénin sous 24-48h",
  },
  {
    icon: Shield,
    title: "Qualité Garantie",
    description: "Garantie de satisfaction ou remboursement",
  },
  {
    icon: Users,
    title: "Support Expert",
    description: "Conseils personnalisés par nos experts en agriculture",
  },
]

export function Features() {
  return (
    <section className="py-16 md:py-24 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card key={index} className="border-0 shadow-none bg-card">
                <CardContent className="p-6 flex flex-col items-center text-center gap-4">
                  <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center">
                    <Icon className="w-7 h-7 text-primary" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="font-semibold text-lg text-foreground">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </section>
  )
}
