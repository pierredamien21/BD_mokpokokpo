import { Button } from "@/components/ui/button"
import { ArrowRight, Sprout } from "lucide-react"

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-muted/30">
      <div className="container mx-auto px-4 py-20 md:py-32">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-8 items-center">
          <div className="flex flex-col gap-6">
            <div className="inline-flex items-center gap-2 text-sm font-medium text-primary bg-primary/10 px-3 py-1 rounded-full w-fit">
              <Sprout className="w-4 h-4" />
              <span>100% Naturel & Biologique</span>
            </div>

            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-balance leading-tight">
              Cultivons ensemble un avenir plus vert
            </h1>

            <p className="text-lg text-muted-foreground leading-relaxed max-w-xl">
              Découvrez notre sélection de plantes et produits agricoles naturels, cultivés avec passion au Bénin. De la
              ferme directement à votre porte.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <Button size="lg" className="text-base">
                Parcourir le catalogue
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
              <Button size="lg" variant="outline" className="text-base bg-transparent">
                En savoir plus
              </Button>
            </div>

            <div className="flex items-center gap-8 pt-4">
              <div>
                <div className="text-3xl font-bold text-foreground">500+</div>
                <div className="text-sm text-muted-foreground">Plantes disponibles</div>
              </div>
              <div className="h-12 w-px bg-border" />
              <div>
                <div className="text-3xl font-bold text-foreground">1200+</div>
                <div className="text-sm text-muted-foreground">Clients satisfaits</div>
              </div>
              <div className="h-12 w-px bg-border" />
              <div>
                <div className="text-3xl font-bold text-foreground">98%</div>
                <div className="text-sm text-muted-foreground">Bio & Naturel</div>
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="aspect-square rounded-2xl overflow-hidden bg-muted">
              <img src="/lush-green-plants-in-modern-greenhouse.jpg" alt="Plantes Mokpokpo" className="w-full h-full object-cover" />
            </div>
            <div className="absolute -bottom-6 -left-6 w-48 h-48 bg-secondary/20 rounded-2xl blur-3xl" />
            <div className="absolute -top-6 -right-6 w-48 h-48 bg-primary/20 rounded-2xl blur-3xl" />
          </div>
        </div>
      </div>
    </section>
  )
}
