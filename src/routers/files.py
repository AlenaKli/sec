import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, Response
from cryptography.fernet import Fernet
import filetype
from src.database import files_db, file_id_counter
from src.security import get_current_user
from src.logger_config import logger

router = APIRouter(prefix="/files")

STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

_enc_key = os.getenv("ENCRYPTION_KEY")
cipher: Optional[Fernet] = Fernet(_enc_key.encode()) if _enc_key else None


def _check_permissions(file_id: int, user: dict = Depends(get_current_user)) -> dict:
    record = next((f for f in files_db if f["id"] == file_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    if user["role"] != "admin" and record["owner"] != user["username"]:
        logger.warning("IDOR attempt: user '%s' tried to access file %d", user["username"], file_id)
        raise HTTPException(status_code=404, detail="File not found")
    return record


@router.get("/my")
def list_my_files(user: dict = Depends(get_current_user)):
    return [f for f in files_db if f["owner"] == user["username"]]


@router.get("/all")
def list_all_files(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return files_db


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    encrypt: bool = Query(False),
    user: dict = Depends(get_current_user),
):
    head = await file.read(2048)
    kind = filetype.guess(head)
    if kind is None or kind.mime not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Only JPEG and PNG images are allowed")

    await file.seek(0)
    file_data = await file.read()

    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 2 MB)")

    is_encrypted = False
    if encrypt and cipher:
        data_to_save = cipher.encrypt(file_data)
        is_encrypted = True
    else:
        data_to_save = file_data

    physical_name = f"{uuid.uuid4()}.bin"
    file_path = STORAGE_DIR / physical_name
    file_path.write_bytes(data_to_save)

    file_id_counter[0] += 1
    record = {
        "id": file_id_counter[0],
        "filename": file.filename,
        "owner": user["username"],
        "size": len(file_data),
        "path": str(file_path),
        "is_encrypted": is_encrypted,
    }
    files_db.append(record)
    logger.info("File uploaded: '%s' by '%s', encrypted=%s", file.filename, user["username"], is_encrypted)
    return {"msg": "Uploaded", "id": record["id"], "original_name": file.filename}


@router.get("/{file_id}/download")
def download_file(file: dict = Depends(_check_permissions)):
    path = Path(file.get("path", ""))
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    if file.get("is_encrypted") and cipher:
        raw = path.read_bytes()
        decrypted = cipher.decrypt(raw)
        return Response(
            content=decrypted,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{file["filename"]}"'},
        )

    return FileResponse(
        path=str(path),
        filename=file["filename"],
        media_type="application/octet-stream",
    )


@router.get("/{file_id}")
def get_file_info(file: dict = Depends(_check_permissions)):
    return file


@router.delete("/{file_id}")
def delete_file(file: dict = Depends(_check_permissions)):
    files_db.remove(file)
    if file.get("path") and Path(file["path"]).exists():
        Path(file["path"]).unlink()
    return {"msg": "Deleted"}
