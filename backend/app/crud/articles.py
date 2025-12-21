# backend/app/crud/articles.py
from sqlalchemy.orm import Session
from .. import models, schemas

def get_articles(db: Session):
    return db.query(models.Article).all()

def get_article(db: Session, code: str):
    return db.query(models.Article).filter(models.Article.ArticleCode == code).first()

def create_article(db: Session, article: schemas.ArticleCreate):
    db_article = models.Article(**article.dict())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def update_article(db: Session, code: str, article: schemas.ArticleUpdate):
    db_article = get_article(db, code)
    if not db_article:
        return None
    if article.ArticleDesignation is not None:
        db_article.ArticleDesignation = article.ArticleDesignation
    db.commit()
    db.refresh(db_article)
    return db_article

def delete_article(db: Session, code: str):
    db_article = get_article(db, code)
    if not db_article:
        return False
    db.delete(db_article)
    db.commit()
    return True
