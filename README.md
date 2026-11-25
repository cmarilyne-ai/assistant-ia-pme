# 🤖 Assistant IA — Productivité Chantier & PME

Prototype d'application web développé avec **Python**, **Streamlit** et l'API **Google Gemini** dans le cadre de ma candidature au poste de **Cheffe de projet IA (Alternance)** chez **AXEM IA** et de mon entrée dans le parcours **AI Engineer (OpenClassrooms)**.

## 🎯 Problématique métier
Les dirigeants de PME et chefs de chantier perdent un temps précieux sur deux tâches répétitives :
1. **Synthèse terrain :** transformer des notes brutes prises sur le vif en comptes rendus structurés et e-mails de suivi clients.
2. **Recherche documentaire :** retrouver rapidement une information fiable dans des documents internes (devis, cahiers des charges, procédures) sans risque d'hallucination.

## 🛠️ Architecture technique & Résilience
- **Interface utilisateur :** Streamlit (prise en main immédiate, déployée en ligne).
- **Moteur IA multi-modèles (Fallback automatique) :** Utilisation du SDK officiel `google-genai` (API Interactions) avec bascule automatique entre **`gemini-3.8-flash`**, **`gemini-3.6-flash`** et **`gemini-3.5-flash-lite`** en cas de pic de charge serveur (`503`), garantissant la continuité de service pour l'utilisateur final.
- **Extraction documentaire :** `pypdf` pour le traitement et l'analyse directe de fichiers PDF métiers.

## 🚀 Accès à la démonstration en ligne
- **Application interactive :** [Insérez votre lien Streamlit Cloud ici]
