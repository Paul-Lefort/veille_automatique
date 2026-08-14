from collections import defaultdict
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import engine, init_db
from models import Article
from sqlmodel import Session, select

app = FastAPI(title="Dashboard de Veille Stratégique")

templates = Jinja2Templates(directory="templates")

MOIS_FR = {
    1: "Janvier",
    2: "Février",
    3: "Mars",
    4: "Avril",
    5: "Mai",
    6: "Juin",
    7: "Juillet",
    8: "Août",
    9: "Septembre",
    10: "Octobre",
    11: "Novembre",
    12: "Décembre",
}


def grouper_articles_par_mois(
    articles: list[Article],
) -> dict[str, list[Article]]:
    groupes = defaultdict(list)

    for art in articles:
        cle_mois = "Récents"
        if art.timestamp:
            try:
                dt = datetime.fromisoformat(art.timestamp)
                cle_mois = f"{MOIS_FR[dt.month]} {dt.year}"
            except ValueError:
                pass
        groupes[cle_mois].append(art)

    return dict(groupes)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def read_dashboard(request: Request):
    try:
        with Session(engine) as session:
            statement = select(Article).order_by(Article.id.desc())
            articles = session.exec(statement).all()

        grouped_articles = grouper_articles_par_mois(articles)

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"grouped_articles": grouped_articles, "error": None},
        )
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"grouped_articles": {}, "error": str(e)},
        )