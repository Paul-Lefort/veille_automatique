import os
from dotenv import load_dotenv
from models import Article
from sqlmodel import Session, SQLModel, create_engine, select

load_dotenv()

DATABASE_URL = (
    f"postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}"
    f"@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}"
)

engine = create_engine(DATABASE_URL, echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)


def save_article_db(article: Article) -> bool:
    with Session(engine, expire_on_commit=False) as session:
        statement = select(Article).where(Article.title == article.title)
        existing = session.exec(statement).first()

        if not existing:
            session.add(article)
            session.commit()
            return True
        return False