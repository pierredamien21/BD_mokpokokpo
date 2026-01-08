"use client"

import { useState } from "react"
import { useAuth } from "@/lib/auth-context"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  Package,
  ShoppingBag,
  Clock,
  CheckCircle2,
  XCircle,
  TrendingUp,
  Heart,
  User,
  Settings,
  LogOut,
  Bell,
  Home,
} from "lucide-react"
import Link from "next/link"

const mockOrders = [
  {
    id: "CMD-2025-001",
    date: "2025-01-03",
    items: 3,
    total: "12500 FCFA",
    status: "delivered",
    products: ["Basilic Sacré (x2)", "Moringa (x1)"],
  },
  {
    id: "CMD-2025-002",
    date: "2025-01-04",
    items: 2,
    total: "7000 FCFA",
    status: "in-transit",
    products: ["Aloe Vera (x2)"],
  },
  {
    id: "CMD-2025-003",
    date: "2025-01-05",
    items: 4,
    total: "15800 FCFA",
    status: "processing",
    products: ["Citronnelle (x2)", "Gingembre (x2)"],
  },
]

const mockFavorites = [
  { id: 1, name: "Basilic Sacré", price: "2500 FCFA", image: "/holy-basil-plant-in-pot.jpg" },
  { id: 2, name: "Moringa", price: "3500 FCFA", image: "/moringa-tree-seedling-in-pot.jpg" },
  { id: 3, name: "Aloe Vera", price: "2000 FCFA", image: "/aloe-vera-succulent-plant.jpg" },
]

export function ClientDashboard() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [activeTab, setActiveTab] = useState("overview")

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "delivered":
        return (
          <Badge className="bg-primary/10 text-primary hover:bg-primary/20">
            <CheckCircle2 className="w-3 h-3 mr-1" />
            Livrée
          </Badge>
        )
      case "in-transit":
        return (
          <Badge className="bg-secondary/10 text-secondary-foreground hover:bg-secondary/20">
            <Package className="w-3 h-3 mr-1" />
            En transit
          </Badge>
        )
      case "processing":
        return (
          <Badge className="bg-accent/10 text-accent-foreground hover:bg-accent/20">
            <Clock className="w-3 h-3 mr-1" />
            En préparation
          </Badge>
        )
      case "cancelled":
        return (
          <Badge variant="destructive" className="bg-destructive/10 text-destructive hover:bg-destructive/20">
            <XCircle className="w-3 h-3 mr-1" />
            Annulée
          </Badge>
        )
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2">
            <Home className="w-5 h-5 text-primary" />
            <span className="text-sm font-medium text-muted-foreground">Retour à l'accueil</span>
          </Link>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon">
              <Bell className="w-5 h-5" />
            </Button>
            <Avatar className="w-9 h-9">
              <AvatarImage src="/placeholder.svg" />
              <AvatarFallback className="bg-primary text-primary-foreground">
                {user?.email?.[0].toUpperCase()}
              </AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid gap-6 lg:grid-cols-[240px_1fr]">
          {/* Sidebar */}
          <aside className="space-y-2">
            <nav className="flex flex-col gap-1">
              <Button
                variant={activeTab === "overview" ? "secondary" : "ghost"}
                className="justify-start"
                onClick={() => setActiveTab("overview")}
              >
                <TrendingUp className="w-4 h-4 mr-2" />
                Vue d'ensemble
              </Button>
              <Button
                variant={activeTab === "orders" ? "secondary" : "ghost"}
                className="justify-start"
                onClick={() => setActiveTab("orders")}
              >
                <ShoppingBag className="w-4 h-4 mr-2" />
                Mes commandes
              </Button>
              <Button
                variant={activeTab === "favorites" ? "secondary" : "ghost"}
                className="justify-start"
                onClick={() => setActiveTab("favorites")}
              >
                <Heart className="w-4 h-4 mr-2" />
                Favoris
              </Button>
              <Button
                variant={activeTab === "profile" ? "secondary" : "ghost"}
                className="justify-start"
                onClick={() => setActiveTab("profile")}
              >
                <User className="w-4 h-4 mr-2" />
                Mon profil
              </Button>
              <Button
                variant={activeTab === "settings" ? "secondary" : "ghost"}
                className="justify-start"
                onClick={() => setActiveTab("settings")}
              >
                <Settings className="w-4 h-4 mr-2" />
                Paramètres
              </Button>
            </nav>

            <div className="pt-4 border-t border-border">
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-destructive hover:bg-destructive/10 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Déconnexion
              </button>
            </div>
          </aside>

          {/* Main Content */}
          <main>
            {activeTab === "overview" && (
              <div className="space-y-6">
                <div>
                  <h1 className="text-3xl font-bold text-foreground">Bienvenue, {user?.email?.split("@")[0]}!</h1>
                  <p className="text-muted-foreground mt-1">Voici un aperçu de votre compte</p>
                </div>

                {/* Stats Cards */}
                <div className="grid gap-4 md:grid-cols-3">
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Commandes totales</CardTitle>
                      <ShoppingBag className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">12</div>
                      <p className="text-xs text-muted-foreground">+3 ce mois</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">En cours</CardTitle>
                      <Clock className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">2</div>
                      <p className="text-xs text-muted-foreground">En préparation</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Montant dépensé</CardTitle>
                      <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">125,400 FCFA</div>
                      <p className="text-xs text-muted-foreground">Total cumulé</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Recent Orders */}
                <Card>
                  <CardHeader>
                    <CardTitle>Commandes récentes</CardTitle>
                    <CardDescription>Vos 3 dernières commandes</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {mockOrders.map((order) => (
                        <div
                          key={order.id}
                          className="flex items-center justify-between p-4 border border-border rounded-lg"
                        >
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <p className="font-medium">{order.id}</p>
                              {getStatusBadge(order.status)}
                            </div>
                            <p className="text-sm text-muted-foreground">{order.products.join(", ")}</p>
                            <p className="text-xs text-muted-foreground">{order.date}</p>
                          </div>
                          <div className="text-right">
                            <p className="font-bold text-primary">{order.total}</p>
                            <p className="text-xs text-muted-foreground">{order.items} articles</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {activeTab === "orders" && (
              <div className="space-y-6">
                <div>
                  <h1 className="text-3xl font-bold text-foreground">Mes commandes</h1>
                  <p className="text-muted-foreground mt-1">Suivez l'état de toutes vos commandes</p>
                </div>

                <Tabs defaultValue="all" className="w-full">
                  <TabsList>
                    <TabsTrigger value="all">Toutes</TabsTrigger>
                    <TabsTrigger value="processing">En cours</TabsTrigger>
                    <TabsTrigger value="delivered">Livrées</TabsTrigger>
                    <TabsTrigger value="cancelled">Annulées</TabsTrigger>
                  </TabsList>

                  <TabsContent value="all" className="space-y-4 mt-6">
                    {mockOrders.map((order) => (
                      <Card key={order.id}>
                        <CardHeader>
                          <div className="flex items-start justify-between">
                            <div className="space-y-1">
                              <CardTitle className="text-lg">{order.id}</CardTitle>
                              <CardDescription>Commandé le {order.date}</CardDescription>
                            </div>
                            {getStatusBadge(order.status)}
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            <div>
                              <p className="text-sm font-medium mb-2">Produits:</p>
                              <ul className="text-sm text-muted-foreground space-y-1">
                                {order.products.map((product, idx) => (
                                  <li key={idx}>• {product}</li>
                                ))}
                              </ul>
                            </div>
                            <div className="flex items-center justify-between pt-4 border-t border-border">
                              <p className="text-sm text-muted-foreground">{order.items} articles</p>
                              <div className="text-right">
                                <p className="text-sm text-muted-foreground">Total</p>
                                <p className="text-xl font-bold text-primary">{order.total}</p>
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Button variant="outline" className="flex-1 bg-transparent">
                                Voir les détails
                              </Button>
                              {order.status === "delivered" && <Button className="flex-1">Commander à nouveau</Button>}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </TabsContent>
                </Tabs>
              </div>
            )}

            {activeTab === "favorites" && (
              <div className="space-y-6">
                <div>
                  <h1 className="text-3xl font-bold text-foreground">Mes favoris</h1>
                  <p className="text-muted-foreground mt-1">Vos plantes préférées</p>
                </div>

                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                  {mockFavorites.map((plant) => (
                    <Card key={plant.id}>
                      <CardContent className="p-0">
                        <div className="relative aspect-square overflow-hidden bg-muted rounded-t-lg">
                          <img
                            src={plant.image || "/placeholder.svg"}
                            alt={plant.name}
                            className="w-full h-full object-cover"
                          />
                          <Button size="icon" variant="secondary" className="absolute top-3 right-3">
                            <Heart className="w-4 h-4 fill-current" />
                          </Button>
                        </div>
                        <div className="p-4 space-y-3">
                          <div>
                            <h3 className="font-semibold text-lg">{plant.name}</h3>
                            <p className="text-xl font-bold text-primary mt-1">{plant.price}</p>
                          </div>
                          <Button className="w-full">Ajouter au panier</Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {activeTab === "profile" && (
              <div className="space-y-6">
                <div>
                  <h1 className="text-3xl font-bold text-foreground">Mon profil</h1>
                  <p className="text-muted-foreground mt-1">Gérez vos informations personnelles</p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>Informations personnelles</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center gap-4">
                      <Avatar className="w-20 h-20">
                        <AvatarImage src="/placeholder.svg" />
                        <AvatarFallback className="bg-primary text-primary-foreground text-2xl">
                          {user?.email?.[0].toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <Button variant="outline">Changer la photo</Button>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Nom complet</label>
                        <div className="p-3 bg-muted rounded-lg">
                          <p className="text-sm">{user?.email?.split("@")[0]}</p>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Email</label>
                        <div className="p-3 bg-muted rounded-lg">
                          <p className="text-sm">{user?.email}</p>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Téléphone</label>
                        <div className="p-3 bg-muted rounded-lg">
                          <p className="text-sm">+229 XX XX XX XX</p>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Adresse</label>
                        <div className="p-3 bg-muted rounded-lg">
                          <p className="text-sm">Cotonou, Bénin</p>
                        </div>
                      </div>
                    </div>

                    <div className="pt-4">
                      <Button>Modifier mes informations</Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {activeTab === "settings" && (
              <div className="space-y-6">
                <div>
                  <h1 className="text-3xl font-bold text-foreground">Paramètres</h1>
                  <p className="text-muted-foreground mt-1">Gérez vos préférences</p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>Notifications</CardTitle>
                    <CardDescription>Configurez vos préférences de notification</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Notifications par email</p>
                        <p className="text-sm text-muted-foreground">Recevoir les mises à jour par email</p>
                      </div>
                      <Button variant="outline" size="sm">
                        Activé
                      </Button>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Notifications de commande</p>
                        <p className="text-sm text-muted-foreground">Alertes sur l'état de vos commandes</p>
                      </div>
                      <Button variant="outline" size="sm">
                        Activé
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Sécurité</CardTitle>
                    <CardDescription>Gérez la sécurité de votre compte</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Button variant="outline">Changer le mot de passe</Button>
                  </CardContent>
                </Card>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}
