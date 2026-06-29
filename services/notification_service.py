"""
Notification generator
-----------------------
This is what actually produces real notifications, by scanning your
fleet data for things that matter (insurance about to expire, license
about to expire, etc.) and writing rows into the `notifications` table.

Run this on a schedule — e.g. APScheduler, Celery beat, or a plain cron
job hitting `python notification_generator.py` every hour. It does NOT
need to run inside the FastAPI request/response cycle.

Add `notification_type` and `link` columns to Notifications first —
see the migration note at the top of notifications_api.py.
"""

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from database import SessionLocal  # 🔧 swap for however you create a Session
import models


def get_admin_user_ids(db: Session) -> list[int]:
    """Recipients for fleet-wide alerts — adjust the role filter to taste."""
    rows = (
        db.execute(
            select(models.Users.id)
            .join(models.MasterRoles, models.Users.role_id == models.MasterRoles.id)
            .where(models.MasterRoles.role_name.in_(["Admin", "Manager"]))
            .where(models.Users.is_active.is_(True))
        )
        .scalars()
        .all()
    )
    return list(rows)


def already_notified(db: Session, link: str, notification_type: str, within_days: int = 1) -> bool:
    """Avoid spamming the same alert every time the job runs."""
    cutoff = date.today() - timedelta(days=within_days)
    existing = db.execute(
        select(models.Notifications.id)
        .where(models.Notifications.link == link)
        .where(models.Notifications.notification_type == notification_type)
        .where(models.Notifications.created_at >= cutoff)
    ).first()
    return existing is not None


def notify(db: Session, user_ids: list[int], title: str, message: str, notification_type: str, link: str):
    for uid in user_ids:
        db.add(
            models.Notifications(
                user_id=uid,
                title=title,
                message=message,
                notification_type=notification_type,
                link=link,
                is_read=False,
            )
        )


def check_vehicle_insurance_expiry(db: Session, days_ahead: int = 30):
    soon = date.today() + timedelta(days=days_ahead)
    vehicles = db.execute(
        select(models.Vehicles)
        .where(models.Vehicles.insurance_expiry_date.is_not(None))
        .where(models.Vehicles.insurance_expiry_date <= soon)
        .where(models.Vehicles.insurance_expiry_date >= date.today())
    ).scalars().all()

    recipients = get_admin_user_ids(db)
    for v in vehicles:
        link = f"/vehicles/{v.id}"
        if already_notified(db, link, "vehicle_insurance"):
            continue
        notify(
            db,
            recipients,
            title="Insurance expiring",
            message=f"Vehicle {v.vehicle_registration_number} insurance expires on {v.insurance_expiry_date}",
            notification_type="vehicle",
            link=link,
        )


def check_driver_license_expiry(db: Session, days_ahead: int = 15):
    soon = date.today() + timedelta(days=days_ahead)
    drivers = db.execute(
        select(models.Drivers)
        .where(models.Drivers.license_expiry.is_not(None))
        .where(models.Drivers.license_expiry <= soon)
        .where(models.Drivers.license_expiry >= date.today())
    ).scalars().all()

    recipients = get_admin_user_ids(db)
    for d in drivers:
        link = f"/drivers/{d.id}"
        if already_notified(db, link, "driver_license"):
            continue
        notify(
            db,
            recipients,
            title="License expiring",
            message=f"Driver license for {d.full_name} expires on {d.license_expiry}",
            notification_type="driver",
            link=link,
        )


def run():
    db = SessionLocal()
    try:
        check_vehicle_insurance_expiry(db)
        check_driver_license_expiry(db)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()