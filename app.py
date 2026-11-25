import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader

# Configuration de la page
st.set_page_config(page_title="Assistant IA - Chantier & PME", page_icon="🤖", layout="wide")

st.title("🤖 Assistant IA — Productivité Chantier & PME")
st.markdown("""
*Prototype développé en Python (Streamlit + API Google Gemini) dans le cadre de ma transition vers le métier de Cheffe de projet IA / AI Engineer.*  
**Objectif métier :** Faire gagner du temps aux équipes opérationnelles en automatisant les comptes rendus et l'exploitation des documents internes.
""")

# Barre latérale : gestion de la clé API
with st.sidebar:
    st.header("⚙️ Configuration")
    try:
        default_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        default_key = ""
    api_key = st.text_input("Clé API Google Gemini", value=default_key, type="password")
    
    st.divider()
    st.markdown("### 💡 Architecture & Résilience")
    st.info(
        "Cet outil illustre deux cas d'usage concrets en entreprise :\n"
        "1. **Synthèse terrain :** transformation de notes brutes en livrable client.\n"
        "2. **Assistant documentaire :** interrogation d'un PDF interne sans hallucination.\n\n"
        "*Intègre une bascule rapide multi-modèles (Gemini 3.5 Flash-Lite → 3.6 Flash → 3.8 Flash) sans blocage en cas de pic serveur.*"
    )

if not api_key:
    st.warning("⚠️ Veuillez renseigner votre clé API Google Gemini dans le menu de gauche pour tester l'application.")
    st.stop()

# Désactive les longues attentes de retry du SDK (1 seule tentative rapide par modèle, timeout 15s)
client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=15000,
        retry_options=types.HttpRetryOptions(attempts=1)
    )
)

# Liste des modèles par ordre de rapidité et disponibilité
MODELES_FALLBACK = ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.8-flash"]

def generer_avec_fallback(prompt_texte):
    derniere_erreur = None
    for modele in MODELES_FALLBACK:
        try:
            # thinking_level="low" accélère fortement la génération sur Gemini 3.x
            config = {} if "lite" in modele else {"thinking_level": "low"}
            interaction = client.interactions.create(
                model=modele,
                input=prompt_texte,
                generation_config=config
            )
            return interaction.output_text, modele
        except Exception as e:
            derniere_erreur = e
            continue
    raise derniere_erreur


# Création des deux onglets métier
onglet1, onglet2 = st.tabs(["📝 1. Notes de chantier / réunion → Compte rendu", "📄 2. Assistant Documentaire (PDF)"])

# --- ONGLET 1 : COMPTE RENDU AUTOMATIQUE ---
with onglet1:
    st.subheader("Transformer des notes brutes en compte rendu structuré")
    
    exemple_notes = (
        "Visite chantier Mme Martin ce matin 9h. La pose du carrelage salon est finie, super rendu. "
        "Par contre problème dans la salle de bain : le receveur de douche commandé est trop grand de 3 cm, "
        "il faut recommander la réf RD-80 chez le fournisseur avant vendredi sinon décalage de la plomberie. "
        "Mme Martin demande aussi un devis pour peindre le couloir en blanc mat. Prévoir prochaine visite mardi 14h."
    )
    
    notes = st.text_area(
        "Collez vos notes brutes ou la transcription d'une note vocale :",
        value=exemple_notes,
        height=150
    )
    
    ton = st.selectbox("Destinataire du livrable :", ["Client (ton professionnel et rassurant)", "Équipe interne (synthétique et orienté action)"])

    if st.button("✨ Générer le compte rendu", type="primary"):
        if notes.strip():
            with st.spinner("Analyse et rédaction en cours avec Gemini..."):
                prompt = f"""
                Tu es un assistant de gestion de projet expert pour les PME et le BTP.
                À partir des notes brutes suivantes, rédige un livrable clair, structuré et directement exploitable.
                Public cible : {ton}.
                
                Structure obligatoire de ta réponse en Markdown :
                ### 📋 Résumé de l'avancement
                ### 🚨 Points bloquants & Alertes
                ### ✅ Plan d'action (Qui fait quoi / Délais)
                ### ✉️ Brouillon d'e-mail prêt à envoyer
                
                Notes brutes :
                {notes}
                """
                try:
                    resultat, modele_utilise = generer_avec_fallback(prompt)
                    st.markdown(resultat)
                    st.caption(f"Généré via `{modele_utilise}`")
                except Exception as e:
                    st.error(f"Tous les modèles sont temporairement saturés : {e}")
        else:
            st.warning("Veuillez saisir des notes avant de lancer la génération.")

# --- ONGLET 2 : ASSISTANT DOCUMENTAIRE PDF ---
with onglet2:
    st.subheader("Poser des questions à un document d'entreprise (PDF)")
    fichier_pdf = st.file_uploader("Importez un document (cahier des charges, procédure interne, devis...)", type=["pdf"])
    
    if fichier_pdf is not None:
        reader = PdfReader(fichier_pdf)
        texte_pdf = ""
        for page in reader.pages:
            texte_pdf += page.extract_text() or ""
            
        st.success(f"✅ Document chargé ({len(reader.pages)} page(s), {len(texte_pdf)} caractères extraits).")
        
        question = st.text_input("Votre question sur ce document :", placeholder="Ex : Quels sont les délais de livraison et les pénalités prévues ?")
        
        if st.button("🔍 Interroger le document", type="primary"):
            if question.strip():
                with st.spinner("Recherche de la réponse dans le document..."):
                    prompt_doc = f"""
                    Tu es un assistant d'entreprise rigoureux. Réponds à la question de l'utilisateur UNIQUEMENT à partir du contenu du document fourni ci-dessous.
                    Si l'information ne figure pas dans le document, dis-le clairement sans inventer. Cite les éléments clés du texte pour justifier ta réponse.
                    
                    Contenu du document :
                    {texte_pdf[:30000]}
                    
                    Question : {question}
                    """
                    try:
                        resultat, modele_utilise = generer_avec_fallback(prompt_doc)
                        st.markdown(resultat)
                        st.caption(f"Généré via `{modele_utilise}`")
                    except Exception as e:
                        st.error(f"Tous les modèles sont temporairement saturés : {e}")
