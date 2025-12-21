# backend/app/routers/articles.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas
from ..crud import articles
from ...database import get_db

router = APIRouter(prefix="/articles", tags=["Articles"])

@router.get("/", response_model=list[schemas.Article])
def read_articles(db: Session = Depends(get_db)):
    return articles.get_articles(db)

@router.get("/{code}", response_model=schemas.Article)
def read_article(code: str, db: Session = Depends(get_db)):
    article = articles.get_article(db, code)
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    return article

@router.post("/", response_model=schemas.Article)
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    return articles.create_article(db, article)

@router.patch("/{code}", response_model=schemas.Article)
def update_article(code: str, article: schemas.ArticleUpdate, db: Session = Depends(get_db)):
    db_article = articles.update_article(db, code, article)
    if not db_article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    return db_article

@router.delete("/{code}")
def delete_article(code: str, db: Session = Depends(get_db)):
    success = articles.delete_article(db, code)
    if not success:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    return {"message": "Article supprimé"}
