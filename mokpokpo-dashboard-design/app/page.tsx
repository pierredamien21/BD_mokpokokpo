import { Header } from "@/components/header"
import { Hero } from "@/components/hero"
import { PlantCatalog } from "@/components/plant-catalog"
import { Features } from "@/components/features"
import { Footer } from "@/components/footer"

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <Hero />
        <PlantCatalog />
        <Features />
      </main>
      <Footer />
    </div>
  )
}
