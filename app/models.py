from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class CategorieEnum(str, Enum):
    CYBERSECURITE = "Cybersécurité"
    DEVOPS_CLOUD = "DevOps & Cloud"
    IA_DATA = "IA & Data"
    SYSTEME_RESEAU = "Système & Réseau"
    DEVELOPPEMENT = "Développement Software"
    AUTRE = "Autre"


class ArticleRaw(BaseModel):
    id: int
    title: str
    link: str
    date: Optional[str] = None


class SelectionArticles(BaseModel):
    selected_ids: List[int]


class ResumeEtCategorie(BaseModel):
    summary: str
    category: CategorieEnum


class Article(SQLModel, table=True):
    __tablename__ = "articles"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(unique=True, index=True)
    link: str
    summary: str
    category: CategorieEnum
    timestamp: Optional[str] = None