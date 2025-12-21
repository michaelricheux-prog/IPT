from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    ArticleCode = Column(String, unique=True)
    ArticleDesignation = Column(String)
    dts = relationship("DT", back_populates="article")

class cdc(Base):
    __tablename__ = "cdc"
    id = Column(Integer, primary_key=True, index=True)
    cdcCode = Column(String, unique=True)
    cdcName = Column(String)
    Capa = Column(Float)
    opedt = relationship("OpeDT", back_populates="cdc")

class DT(Base):
    __tablename__ = "dt"
    id = Column(Integer, primary_key=True, index=True)
    DTCode = Column(String, unique=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    
    article = relationship("Article", back_populates="dts")
    opedt = relationship("OpeDT", back_populates="dt")
    ofs = relationship("OF", back_populates="dt")

class OpeDT(Base):
    __tablename__ = "opedt"
    id = Column(Integer, primary_key=True, index=True)
    dt_id = Column(Integer, ForeignKey("dt.id"))
    description = Column(String)
    ordre = Column(Integer)
    cdc_id = Column(Integer, ForeignKey("cdc.id"))
    charge = Column(Float)
    duree_semaine = Column(Float)
    
    dt = relationship("DT", back_populates="opedt")
    cdc = relationship("cdc", back_populates="opedt")

class OF(Base):
    __tablename__ = "of"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)
    dt_id = Column(Integer, ForeignKey("dt.id"))
    start_date = Column(String)
    end_date = Column(String)
    mode = Column(String)  # ASAP / RETRO
    
    dt = relationship("DT", back_populates="ofs")

class OPEOF(Base):
    __tablename__ = "opeof"
    id = Column(Integer, primary_key=True, index=True)
    of_id = Column(Integer, ForeignKey("of.id"))
    opedt_id = Column(Integer, ForeignKey("opedt.id"))
    description = Column(String)
    cdc_id = Column(Integer, ForeignKey("cdc.id"))
    ordre = Column(Integer)
    charge = Column(Float)
    duree_semaine = Column(Float)
    start_date = Column(String)
    end_date = Column(String)
    mode = Column(String)  # ASAP / RETRO
