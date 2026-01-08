"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import Link from "next/link"
import {
  AlertTriangle,
  TrendingDown,
  TrendingUp,
  Search,
  Filter,
  Plus,
  Home,
  LogOut,
  PackageCheck,
  Calendar,
} from "lucide-react"

const mockInventory = [
  {
    id: 1,
    name: "Basilic Sacré",
    category: "Plantes Médicinales",
    stock: 45,
    minStock: 20,
    maxStock: 100,
    status: "normal",
    lastRestocked: "2025-01-02",
    location: "Serre A",
  },
  {
    id: 2,
    name: "Moringa",
    category: "Superaliments",
    stock: 12,
    minStock: 20,
    maxStock: 80,
    status: "low",
    lastRestocked: "2024-12-28",
    location: "Serre B",
  },
  {
    id: 3,
    name: "Aloe Vera",
    category: "Plantes Médicinales",
    stock: 5,
    minStock: 15,
    maxStock: 70,
    status: "critical",
    lastRestocked: "2024-12-20",
    location: "Serre A",
  },
  {
    id: 4,
    name: "Citronnelle",
    category: "Herbes Aromatiques",
    stock: 67,
    minStock: 25,
    maxStock: 90,
    status: "normal",
    lastRestocked: "2025-01-04",
    location: "Serre C",
  },
  {
    id: 5,
    name: "Gingembre",
    category: "Épices",
    stock: 18,
    minStock: 20,
    maxStock: 75,
    status: "low",
    lastRestocked: "2024-12-30",
    location: "Serre B",
  },
]

const mockMovements = [
  {
    id: 1,
    product: "Basilic Sacré",
    type: "out",
    quantity: 15,
    date: "2025-01-05",
    reason: "Commande CMD-2025-003",
  },
  {
    id: 2,
    product: "Moringa",
    type: "in",
    quantity: 30,
    date: "2025-01-04",
    reason: "Réapprovisionnement",
  },
  {
    id: 3,
    product: "Aloe Vera",
    type: "out",
    quantity: 8,
    date: "2025-01-03",
    reason: "Commande CMD-2025-001",
  },
]

export function StockDashboard() {
  const [activeTab, setActiveTab] = useState("inventory")

  const getStockStatusBadge = (status: string) => {
    switch (status) {
      case "normal":
        return <Badge className="bg-primary/10 text-primary hover:bg-primary/20">Normal</Badge>
      case "low":
        return (
          <Badge className="bg-accent/10 text-accent-foreground hover:bg-accent/20">
            <TrendingDown className="w-3 h-3 mr-1" />
            Faible
          </Badge>
        )
      case "critical":
        return (
          <Badge variant="destructive">
            <AlertTriangle className="w-3 h-3 mr-1" />
            Critique
          </Badge>
        )
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  const getMovementTypeBadge = (type: string) => {
    return type === "in" ? (
      <Badge className="bg-primary/10 text-primary hover:bg-primary/20">
        <TrendingUp className="w-3 h-3 mr-1" />
        Entrée
      </Badge>
    ) : (
      <Badge className="bg-accent/10 text-accent-foreground hover:bg-accent/20">
        <TrendingDown className="w-3 h-3 mr-1" />
        Sortie
      </Badge>
    )
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
            <h1 className="text-lg font-semibold">Dashboard Stock</h1>
          </div>

          <div className="flex items-center gap-2">
            <Avatar className="w-9 h-9">
              <AvatarFallback className="bg-primary text-primary-foreground">MS</AvatarFallback>
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
            <TabsTrigger value="inventory">Inventaire</TabsTrigger>
            <TabsTrigger value="movements">Mouvements</TabsTrigger>
            <TabsTrigger value="alerts">Alertes</TabsTrigger>
          </TabsList>

          {/* Inventory Tab */}
          <TabsContent value="inventory" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-foreground">Gestion de l'inventaire</h2>
                <p className="text-muted-foreground">État du stock actuel</p>
              </div>
              <Link href="/stock/movement/new">
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Nouveau mouvement
                </Button>
              </Link>
            </div>

            <div className="grid gap-4">
              {mockInventory.map((item) => (
                <Card key={item.id}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-semibold text-lg">{item.name}</h3>
                          {getStockStatusBadge(item.status)}
                        </div>
                        <p className="text-sm text-muted-foreground mb-4">{item.category}</p>

                        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                          <div>
                            <p className="text-xs text-muted-foreground">Stock actuel</p>
                            <p className="font-semibold text-lg">{item.stock}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Minimum</p>
                            <p className="font-medium">{item.minStock}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Maximum</p>
                            <p className="font-medium">{item.maxStock}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Localisation</p>
                            <p className="font-medium">{item.location}</p>
                          </div>
                        </div>

                        <div className="mt-3 pt-3 border-t border-border">
                          <p className="text-xs text-muted-foreground">
                            Dernier réapprovisionnement: {item.lastRestocked}
                          </p>
                        </div>
                      </div>

                      <Button variant="outline" size="sm" className="ml-4 bg-transparent">
                        Modifier
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Movements Tab */}
          <TabsContent value="movements" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-foreground">Historique des mouvements</h2>
                <p className="text-muted-foreground">Toutes les entrées/sorties de stock</p>
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
              {mockMovements.map((movement) => (
                <Card key={movement.id}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-start gap-4">
                        <div className="p-2 rounded-lg bg-primary/10">
                          <PackageCheck className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold">{movement.product}</h3>
                            {getMovementTypeBadge(movement.type)}
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">{movement.reason}</p>
                          <div className="flex items-center gap-4 text-sm">
                            <span className="flex items-center gap-1">
                              <Calendar className="w-3 h-3 text-muted-foreground" />
                              {movement.date}
                            </span>
                            <span>
                              Quantité: <strong>{movement.quantity}</strong>
                            </span>
                          </div>
                        </div>
                      </div>

                      <Button variant="ghost" size="sm">
                        Détails
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Alerts Tab */}
          <TabsContent value="alerts" className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-foreground">Alertes de stock</h2>
              <p className="text-muted-foreground">Stocks faibles et critiques</p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <Card className="border-accent/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-accent" />
                    Stock critique
                  </CardTitle>
                  <CardDescription>Articles nécessitant une action immédiate</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {mockInventory
                    .filter((item) => item.status === "critical")
                    .map((item) => (
                      <div
                        key={item.id}
                        className="flex items-center justify-between p-3 bg-accent/5 rounded-lg border border-accent/20"
                      >
                        <div>
                          <p className="font-medium">{item.name}</p>
                          <p className="text-sm text-muted-foreground">Stock: {item.stock}</p>
                        </div>
                        <Button size="sm">Réapprovisionner</Button>
                      </div>
                    ))}
                </CardContent>
              </Card>

              <Card className="border-accent/30">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingDown className="w-5 h-5 text-muted-foreground" />
                    Stock faible
                  </CardTitle>
                  <CardDescription>Articles approchant du minimum</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {mockInventory
                    .filter((item) => item.status === "low")
                    .map((item) => (
                      <div key={item.id} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <div>
                          <p className="font-medium">{item.name}</p>
                          <p className="text-sm text-muted-foreground">Stock: {item.stock}</p>
                        </div>
                        <Button size="sm" variant="outline">
                          Surveiller
                        </Button>
                      </div>
                    ))}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
