"use client"

import { useState } from "react"
import Link from "next/link"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ArrowLeft, Trash2 } from "lucide-react"

interface CartItem {
  id: number
  name: string
  price: number
  quantity: number
  image: string
}

const initialCartItems: CartItem[] = [
  {
    id: 1,
    name: "Menthe Poivrée",
    price: 2500,
    quantity: 2,
    image: "/menthe-poivr-e-plante.jpg",
  },
  {
    id: 3,
    name: "Basilic Sacré",
    price: 2000,
    quantity: 1,
    image: "/basilic-sacr--tulsi.jpg",
  },
]

export default function CartPage() {
  const [cartItems, setCartItems] = useState<CartItem[]>(initialCartItems)

  const updateQuantity = (id: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeItem(id)
    } else {
      setCartItems(cartItems.map((item) => (item.id === id ? { ...item, quantity: newQuantity } : item)))
    }
  }

  const removeItem = (id: number) => {
    setCartItems(cartItems.filter((item) => item.id !== id))
  }

  const subtotal = cartItems.reduce((total, item) => total + item.price * item.quantity, 0)
  const shipping = subtotal > 0 ? 2000 : 0
  const tax = subtotal * 0.05
  const total = subtotal + shipping + tax

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-8">
          <Link href="/catalog" className="flex items-center gap-2 text-primary hover:text-primary/80 mb-8">
            <ArrowLeft className="w-4 h-4" />
            Continuer vos achats
          </Link>

          <div className="mb-8">
            <h1 className="text-4xl font-bold text-foreground">Panier</h1>
            <p className="text-muted-foreground">Vous avez {cartItems.length} article(s) dans votre panier</p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              {cartItems.length > 0 ? (
                <div className="space-y-4">
                  {cartItems.map((item) => (
                    <Card key={item.id} className="p-4">
                      <div className="flex gap-4">
                        <img
                          src={item.image || "/placeholder.svg"}
                          alt={item.name}
                          className="w-24 h-24 rounded-lg object-cover"
                        />
                        <div className="flex-1">
                          <h3 className="font-semibold text-foreground">{item.name}</h3>
                          <p className="text-primary font-bold">{item.price.toLocaleString("fr-BJ")} FCFA</p>
                          <div className="flex items-center gap-2 mt-4">
                            <button
                              onClick={() => updateQuantity(item.id, item.quantity - 1)}
                              className="px-3 py-1 border border-border rounded hover:bg-muted"
                            >
                              -
                            </button>
                            <span className="px-4 text-foreground">{item.quantity}</span>
                            <button
                              onClick={() => updateQuantity(item.id, item.quantity + 1)}
                              className="px-3 py-1 border border-border rounded hover:bg-muted"
                            >
                              +
                            </button>
                          </div>
                        </div>
                        <div className="text-right flex flex-col justify-between">
                          <span className="font-bold text-foreground">
                            {(item.price * item.quantity).toLocaleString("fr-BJ")} FCFA
                          </span>
                          <button
                            onClick={() => removeItem(item.id)}
                            className="text-destructive hover:text-destructive/80 flex items-center gap-1"
                          >
                            <Trash2 className="w-4 h-4" />
                            Supprimer
                          </button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card className="p-12 text-center">
                  <p className="text-muted-foreground text-lg mb-4">Votre panier est vide</p>
                  <Link href="/catalog">
                    <Button>Continuer vos achats</Button>
                  </Link>
                </Card>
              )}
            </div>

            <div className="lg:col-span-1">
              <Card className="p-6 sticky top-24">
                <h3 className="text-xl font-bold text-foreground mb-6">Résumé de la commande</h3>

                <div className="space-y-3 mb-6 pb-6 border-b border-border">
                  <div className="flex justify-between text-foreground">
                    <span>Sous-total</span>
                    <span>{subtotal.toLocaleString("fr-BJ")} FCFA</span>
                  </div>
                  <div className="flex justify-between text-foreground">
                    <span>Livraison</span>
                    <span>{shipping.toLocaleString("fr-BJ")} FCFA</span>
                  </div>
                  <div className="flex justify-between text-foreground">
                    <span>Taxes (5%)</span>
                    <span>{Math.round(tax).toLocaleString("fr-BJ")} FCFA</span>
                  </div>
                </div>

                <div className="flex justify-between text-lg font-bold text-foreground mb-6">
                  <span>Total</span>
                  <span className="text-primary">{Math.round(total).toLocaleString("fr-BJ")} FCFA</span>
                </div>

                <Link href="/checkout" className="block w-full">
                  <Button className="w-full" disabled={cartItems.length === 0}>
                    Valider la commande
                  </Button>
                </Link>
              </Card>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
