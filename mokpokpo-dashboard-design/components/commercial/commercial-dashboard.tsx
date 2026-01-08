"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import Link from "next/link"
import {
  TrendingUp,
  Users,
  ShoppingCart,
  DollarSign,
  Search,
  Filter,
  MoreVertical,
  Phone,
  Mail,
  MapPin,
  Package,
  BarChart3,
  Home,
  LogOut,
} from "lucide-react"

const mockCustomers = [
  {
    id: 1,
    name: "Amina Coulibaly",
    email: "amina.c@email.com",
    phone: "+229 XX XX XX 01",
    location: "Cotonou",
    orders: 12,
    totalSpent: "125,400 FCFA",
    lastOrder: "2025-01-05",
    status: "active",
  },
  {
    id: 2,
    name: "Kofi Mensah",
    email: "kofi.m@email.com",
    phone: "+229 XX XX XX 02",
    location: "Porto-Novo",
    orders: 8,
    totalSpent: "87,600 FCFA",
    lastOrder: "2025-01-04",
    status: "active",
  },
  {
    id: 3,
    name: "Fatou Diallo",
    email: "fatou.d@email.com",
    phone: "+229 XX XX XX 03",
    location: "Parakou",
    orders: 15,
    totalSpent: "156,200 FCFA",
    lastOrder: "2025-01-03",
    status: "vip",
  },
  {
    id: 4,
    name: "Ibrahim Touré",
    email: "ibrahim.t@email.com",
    phone: "+229 XX XX XX 04",
    location: "Cotonou",
    orders: 5,
    totalSpent: "52,300 FCFA",
    lastOrder: "2024-12-28",
    status: "inactive",
  },
]

const mockOrders = [
  {
    id: "CMD-2025-003",
    customer: "Fatou Diallo",
    date: "2025-01-05",
    items: 4,
    total: "15,800 FCFA",
    status: "pending",
  },
  {
    id: "CMD-2025-002",
    customer: "Kofi Mensah",
    date: "2025-01-04",
    items: 2,
    total: "7,000 FCFA",
    status: "confirmed",
  },
  {
    id: "CMD-2025-001",
    customer: "Amina Coulibaly",
    date: "2025-01-03",
    items: 3,
    total: "12,500 FCFA",
    status: "completed",
  },
]

export function CommercialDashboard() {
  const [activeTab, setActiveTab] = useState("overview")

  const getCustomerStatusBadge = (status: string) => {
    switch (status) {
      case "vip":
        return <Badge className="bg-secondary text-secondary-foreground">VIP</Badge>
      case "active":
        return <Badge className="bg-primary/10 text-primary hover:bg-primary/20">Actif</Badge>
      case "inactive":
        return <Badge variant="secondary">Inactif</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  const getOrderStatusBadge = (status: string) => {
    switch (status) {
      case "pending":
        return <Badge className="bg-accent/10 text-accent-foreground hover:bg-accent/20">En attente</Badge>
      case "confirmed":
        return <Badge className="bg-primary/10 text-primary hover:bg-primary/20">Confirmée</Badge>
      case "completed":
        return <Badge className="bg-primary text-primary-foreground">Complétée</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2">
              <Home className="w-5 h-5 text-primary" />
            </Link>
            <div className="h-6 w-px bg-border" />
            <h1 className="text-lg font-semibold">Dashboard Commercial</h1>
          </div>

          <div className="flex items-center gap-2">
            <Avatar className="w-9 h-9">
              <AvatarFallback className="bg-primary text-primary-foreground">YK</AvatarFallback>
            </Avatar>
            <Link href="/logout">
              <Button variant="ghost" size="icon" title="Déconnexion">
                <LogOut className="w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="mb-8">
            <TabsTrigger value="overview">Vue d'ensemble</TabsTrigger>
            <TabsTrigger value="customers">Clients</TabsTrigger>
            <TabsTrigger value="orders">Commandes</TabsTrigger>
            <TabsTrigger value="analytics">Analyses</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-foreground">Vue d'ensemble</h2>
                <p className="text-muted-foreground">Performances commerciales du mois</p>
              </div>
              <Button>
                <BarChart3 className="w-4 h-4 mr-2" />
                Rapport complet
              </Button>
            </div>

            {/* Stats Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Ventes du mois</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">458,700 FCFA</div>
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3 text-primary" />
                    <span className="text-primary">+12.5%</span> vs mois dernier
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Nouveaux clients</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">24</div>
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3 text-primary" />
                    <span className="text-primary">+8.2%</span> vs mois dernier
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Commandes totales</CardTitle>
                  <ShoppingCart className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">87</div>
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3 text-primary" />
                    <span className="text-primary">+15.3%</span> vs mois dernier
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Panier moyen</CardTitle>
                  <Package className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">5,273 FCFA</div>
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3 text-primary" />
                    <span className="text-primary">+3.1%</span> vs mois dernier
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <div className="grid gap-6 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Meilleurs clients</CardTitle>
                  <CardDescription>Top 3 clients par montant dépensé</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {mockCustomers
                    .filter((c) => c.status === "vip" || c.status === "active")
                    .slice(0, 3)
                    .map((customer) => (
                      <div key={customer.id} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Avatar>
                            <AvatarFallback className="bg-primary/10 text-primary">
                              {customer.name
                                .split(" ")
                                .map((n) => n[0])
                                .join("")}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium">{customer.name}</p>
                            <p className="text-sm text-muted-foreground">{customer.orders} commandes</p>
                          </div>
                        </div>
                        <p className="font-bold text-primary">{customer.totalSpent}</p>
                      </div>
                    ))}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Commandes récentes</CardTitle>
                  <CardDescription>Dernières commandes reçues</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {mockOrders.map((order) => (
                    <div key={order.id} className="flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{order.id}</p>
                          {getOrderStatusBadge(order.status)}
                        </div>
                        <p className="text-sm text-muted-foreground">{order.customer}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-primary">{order.total}</p>
                        <p className="text-xs text-muted-foreground">{order.date}</p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Customers Tab */}
          <TabsContent value="customers" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-foreground">Gestion des clients</h2>
                <p className="text-muted-foreground">Base de données clients</p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="icon">
                  <Filter className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="icon">
                  <Search className="w-4 h-4" />
                </Button>
                <Button>Ajouter un client</Button>
              </div>
            </div>

            <div className="grid gap-4">
              {mockCustomers.map((customer) => (
                <Card key={customer.id}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <Avatar className="w-12 h-12">
                          <AvatarFallback className="bg-primary/10 text-primary text-lg">
                            {customer.name
                              .split(" ")
                              .map((n) => n[0])
                              .join("")}
                          </AvatarFallback>
                        </Avatar>
                        <div className="space-y-3">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="font-semibold text-lg">{customer.name}</h3>
                              {getCustomerStatusBadge(customer.status)}
                            </div>
                            <div className="flex flex-col gap-1 text-sm text-muted-foreground">
                              <div className="flex items-center gap-2">
                                <Mail className="w-4 h-4" />
                                <span>{customer.email}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Phone className="w-4 h-4" />
                                <span>{customer.phone}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <MapPin className="w-4 h-4" />
                                <span>{customer.location}</span>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center gap-6 pt-2 border-t border-border">
                            <div>
                              <p className="text-xs text-muted-foreground">Commandes</p>
                              <p className="font-semibold">{customer.orders}</p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Total dépensé</p>
                              <p className="font-semibold text-primary">{customer.totalSpent}</p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Dernière commande</p>
                              <p className="font-semibold">{customer.lastOrder}</p>
                            </div>
                          </div>
                        </div>
                      </div>

                      <Button variant="ghost" size="icon">
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Orders Tab */}
          <TabsContent value="orders" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-foreground">Gestion des commandes</h2>
                <p className="text-muted-foreground">Toutes les commandes clients</p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="icon">
                  <Filter className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="icon">
                  <Search className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div className="space-y-4">
              {mockOrders.map((order) => (
                <Card key={order.id}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="space-y-3">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold text-lg">{order.id}</h3>
                            {getOrderStatusBadge(order.status)}
                          </div>
                          <p className="text-sm text-muted-foreground">Client: {order.customer}</p>
                        </div>

                        <div className="flex items-center gap-6">
                          <div>
                            <p className="text-xs text-muted-foreground">Date</p>
                            <p className="font-medium">{order.date}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Articles</p>
                            <p className="font-medium">{order.items}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Montant</p>
                            <p className="font-semibold text-primary">{order.total}</p>
                          </div>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button variant="outline">Voir détails</Button>
                        {order.status === "pending" && <Button>Confirmer</Button>}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-foreground">Analyses commerciales</h2>
              <p className="text-muted-foreground">Statistiques et tendances</p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Taux de conversion</CardTitle>
                  <CardDescription>Visiteurs → Clients</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold text-primary mb-2">18.5%</div>
                  <p className="text-sm text-muted-foreground">+2.3% ce mois</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Taux de rétention</CardTitle>
                  <CardDescription>Clients récurrents</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold text-primary mb-2">76%</div>
                  <p className="text-sm text-muted-foreground">+5.1% ce mois</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Produits populaires</CardTitle>
                  <CardDescription>Top 3 ventes</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Basilic Sacré</span>
                    <span className="font-semibold">145 ventes</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Moringa</span>
                    <span className="font-semibold">132 ventes</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Aloe Vera</span>
                    <span className="font-semibold">118 ventes</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Régions performantes</CardTitle>
                  <CardDescription>Ventes par zone</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Cotonou</span>
                    <span className="font-semibold">45%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Porto-Novo</span>
                    <span className="font-semibold">28%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Parakou</span>
                    <span className="font-semibold">18%</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
