"use client"

import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Card } from "@/components/ui/card"
import { Leaf, Target, Heart, Sprout } from "lucide-react"

export default function AboutPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-12">
          <div className="mb-16">
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">À propos de Mokpokpo</h1>
            <p className="text-xl text-muted-foreground max-w-2xl">
              Découvrez l'histoire et la mission de notre ferme spécialisée dans les plantes et produits naturels au
              Bénin
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 mb-16">
            <div>
              <img
                src="/ferme-mokpokpo-plantation.jpg"
                alt="Ferme Mokpokpo"
                className="w-full rounded-lg object-cover h-96"
              />
            </div>
            <div className="flex flex-col justify-center">
              <h2 className="text-3xl font-bold text-foreground mb-4">Notre Histoire</h2>
              <p className="text-muted-foreground mb-4 leading-relaxed">
                Mokpokpo est née en 2015 de la passion de cultiver des plantes naturelles de qualité supérieure dans le
                respect de l'environnement. Basée au Bénin, notre ferme s'est développée en proposant des plantes
                médicinales, aromatiques et des superaliments cultivés avec soin.
              </p>
              <p className="text-muted-foreground mb-4 leading-relaxed">
                Nous croyons fermement aux vertus des plantes naturelles et à leur capacité à améliorer la santé et le
                bien-être. Notre engagement envers la qualité, la durabilité et l'innovation nous guide dans chaque
                décision.
              </p>
              <p className="text-muted-foreground leading-relaxed">
                Aujourd'hui, nous servons des clients à travers le Bénin, en partageant notre passion pour les produits
                naturels authentiques et leurs bienfaits.
              </p>
            </div>
          </div>

          <div className="mb-16">
            <h2 className="text-3xl font-bold text-foreground mb-8">Nos Valeurs</h2>
            <div className="grid md:grid-cols-4 gap-6">
              <Card className="p-6 text-center hover:shadow-lg transition-shadow">
                <Leaf className="w-12 h-12 text-primary mx-auto mb-4" />
                <h3 className="font-bold text-foreground mb-2">Qualité</h3>
                <p className="text-sm text-muted-foreground">
                  Nous sélectionnons les meilleures plantes pour garantir votre satisfaction
                </p>
              </Card>
              <Card className="p-6 text-center hover:shadow-lg transition-shadow">
                <Sprout className="w-12 h-12 text-primary mx-auto mb-4" />
                <h3 className="font-bold text-foreground mb-2">Durabilité</h3>
                <p className="text-sm text-muted-foreground">
                  Notre engagement envers l'environnement guide nos pratiques agricoles
                </p>
              </Card>
              <Card className="p-6 text-center hover:shadow-lg transition-shadow">
                <Target className="w-12 h-12 text-primary mx-auto mb-4" />
                <h3 className="font-bold text-foreground mb-2">Innovation</h3>
                <p className="text-sm text-muted-foreground">
                  Nous explorons continuellement de nouvelles méthodes de culture et de transformation
                </p>
              </Card>
              <Card className="p-6 text-center hover:shadow-lg transition-shadow">
                <Heart className="w-12 h-12 text-primary mx-auto mb-4" />
                <h3 className="font-bold text-foreground mb-2">Bien-être</h3>
                <p className="text-sm text-muted-foreground">
                  Votre santé et votre satisfaction sont notre priorité absolue
                </p>
              </Card>
            </div>
          </div>

          <div className="mb-16">
            <h2 className="text-3xl font-bold text-foreground mb-8">Nos Activités</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <Card className="p-8 border-l-4 border-primary">
                <h3 className="text-xl font-bold text-foreground mb-3">Cultivation</h3>
                <p className="text-muted-foreground">
                  Nous cultivons plus de 20 espèces de plantes médicinales, aromatiques et de superaliments à la ferme
                  Mokpokpo en utilisant des méthodes biologiques durables.
                </p>
              </Card>
              <Card className="p-8 border-l-4 border-primary">
                <h3 className="text-xl font-bold text-foreground mb-3">Transformation</h3>
                <p className="text-muted-foreground">
                  Nos produits sont transformés avec soin pour préserver leurs propriétés naturelles. Nous proposons des
                  formats variés : frais, séché, poudre et infusions.
                </p>
              </Card>
              <Card className="p-8 border-l-4 border-primary">
                <h3 className="text-xl font-bold text-foreground mb-3">Commercialisation</h3>
                <p className="text-muted-foreground">
                  Nous commercialisons nos produits directement aux consommateurs et aux professionnels de la santé,
                  garantissant traçabilité et qualité.
                </p>
              </Card>
            </div>
          </div>

          <Card className="p-8 bg-muted/50 mb-12">
            <h2 className="text-2xl font-bold text-foreground mb-4">Nos Engagements</h2>
            <ul className="space-y-3">
              <li className="flex gap-3">
                <span className="text-primary font-bold">✓</span>
                <span className="text-muted-foreground">Cultiver sans pesticides ni engrais chimiques</span>
              </li>
              <li className="flex gap-3">
                <span className="text-primary font-bold">✓</span>
                <span className="text-muted-foreground">Assurer une traçabilité complète de nos produits</span>
              </li>
              <li className="flex gap-3">
                <span className="text-primary font-bold">✓</span>
                <span className="text-muted-foreground">Soutenir les agriculteurs locaux et justes rémunérations</span>
              </li>
              <li className="flex gap-3">
                <span className="text-primary font-bold">✓</span>
                <span className="text-muted-foreground">Préserver et restaurer les ressources naturelles</span>
              </li>
              <li className="flex gap-3">
                <span className="text-primary font-bold">✓</span>
                <span className="text-muted-foreground">
                  Éduquer nos clients sur les bienfaits des plantes naturelles
                </span>
              </li>
            </ul>
          </Card>
        </div>
      </main>
      <Footer />
    </div>
  )
}
