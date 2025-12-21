from pydantic import BaseModel
from typing import Optional

class ArticleBase(BaseModel):
    ArticleCode: str
    ArticleDesignation: str
class ArticleCreate(ArticleBase): pass
class ArticleUpdate(BaseModel):
    ArticleDesignation: Optional[str] = None
class Article(ArticleBase):
    id: int
    class Config:
        from_attributes = True

class cdcBase(BaseModel):
    cdcCode: str
    cdcName: str
    Capa: float
class cdcCreate(cdcBase): pass
class cdcUpdate(BaseModel):
    cdcName: Optional[str] = None
    Capa: Optional[float] = None
class cdc(cdcBase):
    id: int
    class Config:
        from_attributes = True

class DTBase(BaseModel):
    DTCode: str
    article_id: int
class DTCreate(DTBase): pass
class DTUpdate(BaseModel):
    article_id: Optional[int] = None

class DT(DTBase):
    id: int
    class Config:
        from_attributes = True

class DT(BaseModel):
    id: int
    DTCode: str
    article_id: int
    article: Optional[Article]  # inclure la désignation

    class Config:
        orm_mode = True

class OpeDTBase(BaseModel):
    dt_id: int
    description: str
    ordre: int
    cdc_id: int
    charge: float
    duree_semaine: float
class OpeDTCreate(OpeDTBase): pass
class OpeDTUpdate(BaseModel):
    description: Optional[str] = None
    ordre: Optional[int] = None
    cdc_id: Optional[int] = None
    charge: Optional[float] = None
    duree_semaine: Optional[float] = None
class OpeDT(OpeDTBase):
    id: int
    class Config:
        from_attributes = True
