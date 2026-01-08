"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import Link from "next/link"
import {
  Users,
  Package,
  ShoppingCart,
  Settings,
  Shield,
  Database,
  Activity,
  TrendingUp,
  DollarSign,
  UserPlus,
  AlertTriangle,
  CheckCircle2,
  FileText,
  Home,
  LogOut,
  Plus,
  Edit,
  Trash2,
  Search,
  Filter,
} from "lucide-react"

const mockUsers = [
  {
    id: 1,
    name: "Yves Koffi",
    role: "Commercial",
    email: "yves@mokpokpo.bj",
    status: "active",
    lastActive: "Il y a 2h",
  },
  {
    id: 2,
    name: "Marie Sossa",
    role: "Gestionnaire Stock",
    email: "marie@mokpokpo.bj",
    status: "active",
    lastActive: "Il y a 1h",
  },
  {
    id: 3,
    name: "Jean Dossa",
    role: "Commercial",
    email: "jean@mokpokpo.bj",
    status: "inactive",
    lastActive: "Il y a 2j",
  },
]

const mockProducts = [
  { id: 1, name: "Basilic Sacré", category: "Plantes Médicinales", price: "2500 FCFA", status: "active", stock: 45 },
  { id: 2, name: "Moringa", category: "Superaliments", price: "3500 FCFA", status: "active", stock: 12 },
  { id: 3, name: "Aloe Vera", category: "Plantes Médicinales", price: "2000 FCFA", status: "active", stock: 5 },
]

const mockSystemLogs = [
  { id: 1, action: "Nouvelle commande créée", user: "Système", timestamp: "2025-01-05 14:32", type: "info" },
  { id: 2, action: "Stock Aloe Vera critique", user: "Système", timestamp: "2025-01-05 13:15", type: "warning" },
  { id: 3, action: "Utilisateur Jean Dossa modifié", user: "Admin", timestamp: "2025-01-05 11:20", type: "success" },
  {
    id: 4,
    action: "Tentative de connexion échouée",
    user: "unknown@email.com",
    timestamp: "2025-01-05 09:45",
    type: "error",
  },
]

export function AdminDashboard() {
  const [activeTab, setActiveTab] = useState("overview")

  const getRoleBadge = (role: string) => {
    switch (role) {
      case "Commercial":
        return <Badge className="bg-primary/10 text-primary hover:bg-primary/20">Commercial</Badge>
      case "Gestionnaire Stock":
        return <Badge className="bg-secondary/10 text-secondary-foreground hover:bg-secondary/20">Stock</Badge>
      case "Admin":
        return <Badge className="bg-accent text-accent-foreground">Admin</Badge>
      default:
        return <Badge variant="secondary">{role}</Badge>
    }
  }

  const getStatusBadge = (status: string) => {
    return status === "active" ? (
      <Badge className="bg-primary/10 text-primary hover:bg-primary/20">
        <CheckCircle2 className="w-3 h-3 mr-1" />
        Actif
      </Badge>
    ) : (
      <Badge variant="secondary">
        <AlertTriangle className="w-3 h-3 mr-1" />
        Inactif
      </Badge>
    )
  }

  const getLogBadge = (type: string) => {
    switch (type) {
      case "info":
        return <Badge className="bg-blue-500/10 text-blue-700">Info</Badge>
      case "warning":
        return <Badge className="bg-yellow-500/10 text-yellow-700">Alerte</Badge>
      case "success":
        return <Badge className="bg-primary/10 text-primary">Succès</Badge>
      case "error":
        return <Badge variant="destructive">Erreur</Badge>
      default:
        return <Badge variant="secondary">{type}</Badge>
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
            <h1 className="text-lg font-semibold">Panel Administrateur</h1>
          </div>

          <div className="flex items-center gap-2">
            <Avatar className="w-9 h-9">
              <AvatarFallback className="bg-primary text-primary-foreground">AD</AvatarFallback>
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
            <TabsTrigger value="users">Utilisateurs</TabsTrigger>
            <TabsTrigger value="products">Produits</TabsTrigger>
            <TabsTrigger value="system">Système</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-foreground">Vue d'ensemble système</h2>
              <p className="text-muted-foreground">Aperçu général de la plateforme</p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Utilisateurs actifs</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">247</div>
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3 text-primary" />
                    <span className="text-primary">+5 aujourd'hui</span>
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Commandes totales</CardTitle>
                  <ShoppingCart className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">1,243</div>
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3 text-primary" />
                    <span className="text-primary">+32 ce mois</span>
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Produits disponibles</CardTitle>
                  <Package className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">48</div>
                  <p className="text-xs text-muted-foreground">Références actives</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Chiffre d'affaires</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">2.8M FCFA</div>
                  <p className="text-xs text-muted-foreground">Ce mois</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-foreground">Gestion des utilisateurs</h2>
                <p className="text-muted-foreground">Gestionnaire, commerciaux et admins</p>
              </div>
              <Button>
                <UserPlus className="w-4 h-4 mr-2" />
                Ajouter un utilisateur
              </Button>
            </div>

            <div className="grid gap-4">
              {mockUsers.map((user) => (
                <Card key={user.id}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <Avatar>
                          <AvatarFallback className="bg-primary/10 text-primary">
                            {user.name
                              .split(" ")
                              .map((n) => n[0])
                              .join("")}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold">{user.name}</h3>
                            {getRoleBadge(user.role)}
                            {getStatusBadge(user.status)}
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">{user.email}</p>
                          <p className="text-xs text-muted-foreground">Dernière activité: {user.lastActive}</p>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button variant="ghost" size="icon">
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="icon">
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Products Tab */}
          <TabsContent value="products" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-foreground">Gestion des produits</h2>
                <p className="text-muted-foreground">Catalogue de produits Mokpokpo</p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="icon">
                  <Search className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="icon">
                  <Filter className="w-4 h-4" />
                </Button>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Ajouter un produit
                </Button>
              </div>
            </div>

            <div className="grid gap-4">
              {mockProducts.map((product) => (
                <Card key={product.id}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold">{product.name}</h3>
                          <Badge className={product.status === "active" ? "bg-primary/10 text-primary" : "bg-muted"}>
                            {product.status === "active" ? "Actif" : "Inactif"}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">{product.category}</p>
                        <div className="flex items-center gap-6 text-sm">
                          <span>
                            Prix: <strong>{product.price}</strong>
                          </span>
                          <span>
                            Stock: <strong>{product.stock}</strong>
                          </span>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          Modifier
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-destructive hover:text-destructive bg-transparent"
                        >
                          Supprimer
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* System Tab */}
          <TabsContent value="system" className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-foreground">Système et logs</h2>
              <p className="text-muted-foreground">Surveillance du système et historique</p>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="w-5 h-5" />
                    État du système
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Base de données</span>
                    <Badge className="bg-primary/10 text-primary">Opérationnel</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Serveur API</span>
                    <Badge className="bg-primary/10 text-primary">Opérationnel</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Stockage</span>
                    <Badge className="bg-yellow-500/10 text-yellow-700">75% utilisé</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Sauvegarde</span>
                    <Badge className="bg-primary/10 text-primary">À jour</Badge>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Configuration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button variant="outline" className="w-full justify-start bg-transparent">
                    <Settings className="w-4 h-4 mr-2" />
                    Paramètres généraux
                  </Button>
                  <Button variant="outline" className="w-full justify-start bg-transparent">
                    <Shield className="w-4 h-4 mr-2" />
                    Sécurité
                  </Button>
                  <Button variant="outline" className="w-full justify-start bg-transparent">
                    <Database className="w-4 h-4 mr-2" />
                    Sauvegarde et restauration
                  </Button>
                  <Button variant="outline" className="w-full justify-start bg-transparent">
                    <Activity className="w-4 h-4 mr-2" />
                    Monitoring
                  </Button>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Historique des logs
                </CardTitle>
                <CardDescription>Activités système récentes</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {mockSystemLogs.map((log) => (
                  <div key={log.id} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg border border-border">
                    <div className="mt-1">{getLogBadge(log.type)}</div>
                    <div className="flex-1">
                      <p className="font-medium text-sm">{log.action}</p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                        <span>Par: {log.user}</span>
                        <span>•</span>
                        <span>{log.timestamp}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
