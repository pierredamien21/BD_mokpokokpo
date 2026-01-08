"use client"

import type React from "react"

import { useState } from "react"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Mail, Phone, MapPin, Send, CheckCircle } from "lucide-react"

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500))

    setIsSubmitted(true)
    setFormData({
      name: "",
      email: "",
      subject: "",
      message: "",
    })

    // Reset after 5 seconds
    setTimeout(() => setIsSubmitted(false), 5000)
    setIsSubmitting(false)
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-12">
          <div className="mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">Nous contacter</h1>
            <p className="text-xl text-muted-foreground max-w-2xl">
              Avez des questions? Nous serions ravis d'entendre parler de vous. Contactez-nous via ce formulaire ou l'un
              de nos coordonnées ci-dessous.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <Card className="p-6">
              <Mail className="w-8 h-8 text-primary mb-4" />
              <h3 className="font-bold text-foreground mb-2">Email</h3>
              <p className="text-muted-foreground">contact@mokpokpo.com</p>
              <p className="text-sm text-muted-foreground mt-2">Réponse en 24h</p>
            </Card>
            <Card className="p-6">
              <Phone className="w-8 h-8 text-primary mb-4" />
              <h3 className="font-bold text-foreground mb-2">Téléphone</h3>
              <p className="text-muted-foreground">+229 95 XXX XXX</p>
              <p className="text-sm text-muted-foreground mt-2">Lun-Ven: 8h-17h</p>
            </Card>
            <Card className="p-6">
              <MapPin className="w-8 h-8 text-primary mb-4" />
              <h3 className="font-bold text-foreground mb-2">Adresse</h3>
              <p className="text-muted-foreground">
                Ferme Mokpokpo
                <br />
                Cotonou, Bénin
              </p>
              <p className="text-sm text-muted-foreground mt-2">Visite sur rendez-vous</p>
            </Card>
          </div>

          <div className="grid md:grid-cols-2 gap-12">
            <Card className="p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6">Envoyez-nous un message</h2>

              {isSubmitted && (
                <div className="flex gap-3 p-4 bg-green-50 border border-green-200 rounded-lg mb-6">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-green-900">Message envoyé avec succès!</p>
                    <p className="text-sm text-green-700">
                      Merci de nous avoir contacté. Nous vous répondrons bientôt.
                    </p>
                  </div>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-foreground mb-2">
                    Nom complet
                  </label>
                  <input
                    id="name"
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    placeholder="Jean Dupont"
                    className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-foreground mb-2">
                    Email
                  </label>
                  <input
                    id="email"
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    placeholder="vous@exemple.com"
                    className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label htmlFor="subject" className="block text-sm font-medium text-foreground mb-2">
                    Sujet
                  </label>
                  <input
                    id="subject"
                    type="text"
                    name="subject"
                    value={formData.subject}
                    onChange={handleInputChange}
                    required
                    placeholder="Objet de votre message"
                    className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label htmlFor="message" className="block text-sm font-medium text-foreground mb-2">
                    Message
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleInputChange}
                    required
                    placeholder="Votre message..."
                    rows={5}
                    className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                  />
                </div>

                <Button type="submit" className="w-full" disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>Envoi en cours...</>
                  ) : (
                    <>
                      <Send className="w-4 h-4 mr-2" />
                      Envoyer le message
                    </>
                  )}
                </Button>
              </form>
            </Card>

            <Card className="p-8 bg-muted/50">
              <h2 className="text-2xl font-bold text-foreground mb-6">Informations</h2>
              <div className="space-y-6">
                <div>
                  <h3 className="font-bold text-foreground mb-2">Horaires d'ouverture</h3>
                  <ul className="space-y-1 text-muted-foreground">
                    <li>Lundi - Vendredi: 8h00 - 17h00</li>
                    <li>Samedi: 9h00 - 13h00</li>
                    <li>Dimanche: Fermé</li>
                  </ul>
                </div>

                <div>
                  <h3 className="font-bold text-foreground mb-2">Questions fréquentes</h3>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li>
                      <p className="font-semibold text-foreground">Livraison gratuite?</p>
                      <p>Livraison gratuite pour les commandes supérieures à 20000 FCFA</p>
                    </li>
                    <li>
                      <p className="font-semibold text-foreground">Délai de livraison?</p>
                      <p>2-3 jours ouvrables en Cotonou, 3-5 jours pour l'intérieur</p>
                    </li>
                    <li>
                      <p className="font-semibold text-foreground">Retours et échanges?</p>
                      <p>30 jours pour retourner ou échanger vos produits</p>
                    </li>
                  </ul>
                </div>

                <div>
                  <h3 className="font-bold text-foreground mb-2">Suivez-nous</h3>
                  <div className="flex gap-4">
                    <a
                      href="#"
                      className="text-muted-foreground hover:text-primary transition-colors"
                      aria-label="Facebook"
                    >
                      Facebook
                    </a>
                    <a
                      href="#"
                      className="text-muted-foreground hover:text-primary transition-colors"
                      aria-label="Instagram"
                    >
                      Instagram
                    </a>
                    <a
                      href="#"
                      className="text-muted-foreground hover:text-primary transition-colors"
                      aria-label="WhatsApp"
                    >
                      WhatsApp
                    </a>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
