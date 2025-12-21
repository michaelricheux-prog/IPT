from fastapi import APIRouter, Depends, UploadFile, File, Response, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import excel_service

router = APIRouter(prefix="/excel", tags=["Import/Export"])

@router.get("/export")
def export_excel(db: Session = Depends(get_db)):
    content = excel_service.export_blocs_to_excel(db)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=export_blocs.xlsx"}
    )

@router.post("/import")
async def import_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    count = excel_service.import_blocs_from_excel(db, content)
    return {"message": f"{count} blocs importés avec succès"}

@router.get("/export-csv")
def export_csv(db: Session = Depends(get_db)):
    content = excel_service.export_blocs_to_csv(db)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=export_blocs.csv"}
    )

@router.post("/import-csv")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        count = excel_service.import_blocs_from_csv(db, content)
        return {"message": f"{count} blocs importés depuis le CSV avec succès"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de la lecture du CSV: {str(e)}")