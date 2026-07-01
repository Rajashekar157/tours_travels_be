from sqlalchemy import text
from sqlalchemy.orm import Session


def generate_driver_code(db: Session) -> str:
    """DRV-01, DRV-02, ... — atomic via Postgres sequence."""
    result = db.execute(text("SELECT nextval('driver_code_seq')")).scalar()
    return f"DRV-{str(result).zfill(6)}"


def generate_supplier_code(db: Session) -> str:
    """SUP-01, SUP-02, ..."""
    result = db.execute(text("SELECT nextval('supplier_code_seq')")).scalar()
    return f"SUP-{str(result).zfill(6)}"


def generate_vehicle_code(db: Session) -> str:
    """VEH-01, VEH-02, ..."""
    result = db.execute(text("SELECT nextval('vehicle_code_seq')")).scalar()
    return f"VEH-{str(result).zfill(6)}"