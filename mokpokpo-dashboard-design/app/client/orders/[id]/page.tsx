"use client"

import Link from "next/link"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ArrowLeft, CheckCircle, Clock, Truck, Package } from "lucide-react"

interface OrderDetailPageProps {
  params: {
    id: string
  }
}

// Mock order data - in real app this would come from API
const mockOrders: Record<string, any> = {
  "12345": {
    id: "12345",
    date: "15 Janvier 2024",
    status: "livrée",
    statusLabel: "Livrée",
    total: 9450,
    items: [
      {
        id: 1,
        name: "Menthe Poivrée",
        quantity: 2,
        price: 2500,
        image: "/menthe-poivr-e-plante.jpg",
      },
      {
        id: 3,
        name: "Basilic Sacré",
        quantity: 1,
        price: 2000,
        image: "/basilic-sacr--tulsi.jpg",
      },
    ],
    subtotal: 7000,
    shipping: 2000,
    tax: 450,
    customer: {
      name: "Jean Dupont",
      email: "jean.dupont@example.com",
      phone: "+229 95 XXX XXX",
      address: "123 Rue de la Paix, Cotonou, 00000, Bénin",
    },
    timeline: [
      { status: "Commande confirmée", date: "15 Janvier 2024", icon: "check" },
      { status: "Commande expédiée", date: "16 Janvier 2024", icon: "truck" },
      { status: "En livraison", date: "17 Janvier 2024", icon: "package" },
      { status: "Livrée", date: "18 Janvier 2024", icon: "check" },
    ],
  },
  "12346": {
    id: "12346",
    date: "12 Janvier 2024",
    status: "en-attente",
    statusLabel: "En attente",
    total: 5250,
    items: [
      {
        id: 2,
        name: "Gingembre Bio",
        quantity: 1,
        price: 3500,
        image: "/gingembre-bio-racine.jpg",
      },
    ],
    subtotal: 3500,
    shipping: 2000,
    tax: 175,
    customer: {
      name: "Jean Dupont",
      email: "jean.dupont@example.com",
      phone: "+229 95 XXX XXX",
      address: "123 Rue de la Paix, Cotonou, 00000, Bénin",
    },
    timeline: [
      { status: "Commande confirmée", date: "12 Janvier 2024", icon: "check" },
      { status: "Préparation", date: "À venir", icon: "clock" },
      { status: "Expédition", date: "À venir", icon: "truck" },
      { status: "Livraison", date: "À venir", icon: "package" },
    ],
  },
}

const statusColors: Record<string, any> = {
  livrée: { bg: "bg-green-50", border: "border-green-200", text: "text-green-700", badge: "bg-green-100" },
  "en-attente": {
    bg: "bg-yellow-50",
    border: "border-yellow-200",
    text: "text-yellow-700",
    badge: "bg-yellow-100",
  },
  "en-cours": { bg: "bg-blue-50", border: "border-blue-200", text: "text-blue-700", badge: "bg-blue-100" },
  refusée: { bg: "bg-red-50", border: "border-red-200", text: "text-red-700", badge: "bg-red-100" },
}

export default function OrderDetailPage({ params }: OrderDetailPageProps) {
  const order = mockOrders[params.id] || mockOrders["12345"]
  const statusColor = statusColors[order.status] || statusColors["en-attente"]

  const getStatusIcon = (iconType: string) => {
    switch (iconType) {
      case "check":
        return <CheckCircle className="w-6 h-6 text-green-600" />
      case "truck":
        return <Truck className="w-6 h-6 text-blue-600" />
      case "package":
        return <Package className="w-6 h-6 text-blue-600" />
      case "clock":
        return <Clock className="w-6 h-6 text-yellow-600" />
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-8">
          <Link href="/client" className="flex items-center gap-2 text-primary hover:text-primary/80 mb-8">
            <ArrowLeft className="w-4 h-4" />
            Retour à mes commandes
          </Link>

          <div className="mb-8">
            <h1 className="text-4xl font-bold text-foreground mb-2">Commande #{order.id}</h1>
            <p className="text-muted-foreground">Passée le {order.date}</p>
          </div>

          <div className={`border rounded-lg p-6 mb-8 ${statusColor.border} ${statusColor.bg}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Statut de la commande</p>
                <p className={`text-2xl font-bold ${statusColor.text}`}>{order.statusLabel}</p>
              </div>
              <span className={`px-4 py-2 rounded-full font-semibold text-sm ${statusColor.badge} ${statusColor.text}`}>
                {order.statusLabel}
              </span>
            </div>
          </div>

          <div className="grid lg:grid-cols-3 gap-8 mb-8">
            <div className="lg:col-span-2">
              <Card className="p-6 mb-8">
                <h2 className="text-2xl font-bold text-foreground mb-6">Articles</h2>
                <div className="space-y-4">
                  {order.items.map((item: any, index: number) => (
                    <div key={index} className="flex gap-4 pb-4 border-b border-border last:border-b-0">
                      <img
                        src={item.image || "/placeholder.svg"}
                        alt={item.name}
                        className="w-20 h-20 rounded-lg object-cover"
                      />
                      <div className="flex-1">
                        <h3 className="font-semibold text-foreground">{item.name}</h3>
                        <p className="text-sm text-muted-foreground">Quantité: {item.quantity}</p>
                        <p className="text-primary font-bold">{item.price.toLocaleString("fr-BJ")} FCFA</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-foreground">
                          {(item.price * item.quantity).toLocaleString("fr-BJ")} FCFA
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              <Card className="p-6">
                <h2 className="text-2xl font-bold text-foreground mb-6">Suivi de la commande</h2>
                <div className="space-y-6">
                  {order.timeline.map((step: any, index: number) => (
                    <div key={index} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        {getStatusIcon(step.icon)}
                        {index < order.timeline.length - 1 && <div className="w-1 h-8 bg-border mt-2"></div>}
                      </div>
                      <div className="pb-4">
                        <p className="font-semibold text-foreground">{step.status}</p>
                        <p className="text-sm text-muted-foreground">{step.date}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            <div>
              <Card className="p-6 mb-6 sticky top-24">
                <h3 className="text-xl font-bold text-foreground mb-6">Résumé</h3>

                <div className="space-y-3 mb-6 pb-6 border-b border-border">
                  <div className="flex justify-between text-foreground">
                    <span>Sous-total</span>
                    <span>{order.subtotal.toLocaleString("fr-BJ")} FCFA</span>
                  </div>
                  <div className="flex justify-between text-foreground">
                    <span>Livraison</span>
                    <span>{order.shipping.toLocaleString("fr-BJ")} FCFA</span>
                  </div>
                  <div className="flex justify-between text-foreground">
                    <span>Taxes</span>
                    <span>{order.tax.toLocaleString("fr-BJ")} FCFA</span>
                  </div>
                </div>

                <div className="flex justify-between text-lg font-bold text-foreground mb-6">
                  <span>Total</span>
                  <span className="text-primary">{order.total.toLocaleString("fr-BJ")} FCFA</span>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="font-bold text-foreground mb-4">Adresse de livraison</h3>
                <p className="text-sm text-muted-foreground mb-4">{order.customer.address}</p>
                <p className="text-sm text-muted-foreground mb-1">
                  <span className="font-semibold text-foreground">{order.customer.name}</span>
                </p>
                <p className="text-sm text-muted-foreground mb-1">{order.customer.phone}</p>
                <p className="text-sm text-muted-foreground">{order.customer.email}</p>

                <div className="space-y-3 mt-6 pt-6 border-t border-border">
                  <Button
                    className="w-full bg-transparent"
                    variant="outline"
                    size="sm"
                    disabled={order.status !== "livrée"}
                  >
                    Retourner/Échanger
                  </Button>
                  <Button className="w-full bg-transparent" variant="outline" size="sm">
                    Contacter le support
                  </Button>
                  <Link href="/catalog" className="block">
                    <Button className="w-full" size="sm">
                      Commander à nouveau
                    </Button>
                  </Link>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
