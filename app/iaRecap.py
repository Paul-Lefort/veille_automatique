import json
from typing import List, Optional
from models import Article, ArticleRaw, ResumeEtCategorie, SelectionArticles
from ollama import chat
import trafilatura


def trier_articles_ia(articles: List[ArticleRaw]) -> List[ArticleRaw]:
    if not articles:
        return []

    payload_llm = [{"id": a.id, "title": a.title} for a in articles]

    prompt = (
        "Sélectionne les 3 articles les plus pertinents de la liste suivante.\n"
        f"Articles disponibles : {json.dumps(payload_llm, ensure_ascii=False)}"
    )

    try:
        response = chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}],
            format=SelectionArticles.model_json_schema(),
            options={"temperature": 0},
        )

        res = SelectionArticles.model_validate_json(response.message.content)
        return [a for a in articles if a.id in res.selected_ids]

    except Exception as e:
        print(f"Erreur lors du tri IA : {e}")
        return []


def scraper_contenu_article(url: str) -> Optional[str]:
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            return trafilatura.extract(downloaded)
    except Exception as e:
        print(f"Erreur scraping {url} : {e}")
    return None


def resumer_et_categoriser_article(article: ArticleRaw) -> Optional[Article]:
    texte_article = scraper_contenu_article(article.link)

    if not texte_article:
        print(f"Impossible de récupérer le contenu de {article.link}")
        return None

    prompt = (
        "Fais un résumé synthétique (environ 200-300 mots) en français du texte suivant "
        "et classe-le dans la catégorie la plus adaptée.\n\n"
        f"Texte :\n{texte_article[:4000]}"
    )

    try:
        response = chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}],
            format=ResumeEtCategorie.model_json_schema(),
            options={"temperature": 0},
        )

        res = ResumeEtCategorie.model_validate_json(response.message.content)

        return Article(
            title=article.title,
            link=article.link,
            summary=res.summary,
            category=res.category,
            timestamp=article.date,
        )

    except Exception as e:
        print(f"Erreur génération résumé/catégorie pour {article.title} : {e}")
        return None