"""
Admin Dashboard API Endpoints

Provides platform-wide statistics and management actions for admin users.
Routes:
  GET  /api/v1/admin/dashboard-summary  — KPI stats for admin overview
  GET  /api/v1/admin/drivers             — List all driver accounts
  POST /api/v1/admin/drivers/{id}/suspend — Suspend a driver
  POST /api/v1/admin/drivers/{id}/reactivate — Reactivate a driver
  GET  /api/v1/admin/guarantee-overview  — System-wide guarantee stats
  GET  /api/v1/admin/shifts-overview     — Platform shift breakdown
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from src.database import get_db
from src.models.user import User, UserRole
from src.models.shift import Shift
from src.models.committed_shift import CommittedShift, GuaranteeLog, ShiftStatus
from src.models.eligibility_metrics import WorkerSurvey, PredictionAccuracy

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/dashboard-summary")
def admin_dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns key platform KPIs for the admin dashboard overview.
    Real data from all tables.
    """

    # --- Driver stats ---
    total_drivers = db.query(func.count(User.id)).filter(
        User.role == UserRole.DRIVER
    ).scalar() or 0

    active_drivers = db.query(func.count(User.id)).filter(
        User.role == UserRole.DRIVER, User.is_active == True
    ).scalar() or 0

    suspended_drivers = total_drivers - active_drivers

    # --- Shift stats ---
    total_shifts = db.query(func.count(Shift.id)).scalar() or 0

    # --- Committed shift stats ---
    committed_total = db.query(func.count(CommittedShift.id)).scalar() or 0
    committed_completed = db.query(func.count(CommittedShift.id)).filter(
        CommittedShift.status == ShiftStatus.COMPLETED
    ).scalar() or 0
    committed_pending = db.query(func.count(CommittedShift.id)).filter(
        CommittedShift.status.in_([ShiftStatus.COMMITTED, ShiftStatus.IN_PROGRESS])
    ).scalar() or 0

    # --- Guarantee stats ---
    guarantee_activated = db.query(func.count(CommittedShift.id)).filter(
        CommittedShift.guarantee_activated == True
    ).scalar() or 0
    total_topups = db.query(func.coalesce(func.sum(CommittedShift.topup_amount), 0)).scalar()
    total_predicted = db.query(
        func.coalesce(func.sum(CommittedShift.predicted_earnings), 0)
    ).filter(CommittedShift.status == ShiftStatus.COMPLETED).scalar()
    total_actual = db.query(
        func.coalesce(func.sum(CommittedShift.actual_earnings), 0)
    ).filter(CommittedShift.status == ShiftStatus.COMPLETED).scalar()

    activation_rate = (
        round(guarantee_activated / committed_completed * 100, 1)
        if committed_completed > 0 else 0
    )

    # --- Prediction accuracy ---
    accuracy_rows = db.query(PredictionAccuracy).all()
    avg_mape = None
    if accuracy_rows:
        mapes = [r.mape for r in accuracy_rows if r.mape is not None]
        avg_mape = round(sum(mapes) / len(mapes), 1) if mapes else None

    # --- Survey stats ---
    survey_count = db.query(func.count(WorkerSurvey.id)).scalar() or 0
    avg_satisfaction = db.query(
        func.avg(WorkerSurvey.app_usefulness)
    ).scalar()
    avg_satisfaction = round(float(avg_satisfaction), 1) if avg_satisfaction else None

    # --- Audit log count ---
    audit_count = db.query(func.count(GuaranteeLog.id)).scalar() or 0

    return {
        "drivers": {
            "total": total_drivers,
            "active": active_drivers,
            "suspended": suspended_drivers,
        },
        "shifts": {
            "total_recorded": total_shifts,
            "committed_total": committed_total,
            "committed_completed": committed_completed,
            "committed_pending": committed_pending,
        },
        "guarantee": {
            "activations": guarantee_activated,
            "activation_rate": activation_rate,
            "total_topups_paid": round(float(total_topups), 2),
            "total_predicted": round(float(total_predicted), 2),
            "total_actual": round(float(total_actual), 2),
        },
        "accuracy": {
            "avg_mape": avg_mape,
            "records": len(accuracy_rows),
        },
        "surveys": {
            "total_responses": survey_count,
            "avg_satisfaction": avg_satisfaction,
        },
        "audit_log_entries": audit_count,
    }


@router.get("/drivers")
def list_drivers(db: Session = Depends(get_db)):
    """
    List all driver-role users with account status.
    Admin can see all drivers for management (FR9).
    """
    drivers = db.query(User).filter(User.role == UserRole.DRIVER).all()
    return [
        {
            "id": d.id,
            "email": d.email,
            "full_name": d.full_name,
            "phone": d.phone,
            "is_active": d.is_active,
            "is_verified": d.is_verified,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "last_login": d.last_login.isoformat() if d.last_login else None,
        }
        for d in drivers
    ]


@router.post("/drivers/{driver_id}/suspend")
def suspend_driver(driver_id: int, db: Session = Depends(get_db)):
    """Suspend a driver account (FR9 - admin eligibility management)."""
    driver = db.query(User).filter(User.id == driver_id, User.role == UserRole.DRIVER).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.is_active = False
    db.commit()
    return {"status": "suspended", "driver_id": driver_id, "full_name": driver.full_name}


@router.post("/drivers/{driver_id}/reactivate")
def reactivate_driver(driver_id: int, db: Session = Depends(get_db)):
    """Reactivate a suspended driver account (FR9 - admin eligibility management)."""
    driver = db.query(User).filter(User.id == driver_id, User.role == UserRole.DRIVER).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.is_active = True
    db.commit()
    return {"status": "active", "driver_id": driver_id, "full_name": driver.full_name}


@router.get("/guarantee-overview")
def guarantee_overview(db: Session = Depends(get_db)):
    """
    System-wide guarantee statistics for admin oversight.
    Shows guarantee usage across ALL drivers.
    """
    shifts = db.query(CommittedShift).filter(
        CommittedShift.status == ShiftStatus.COMPLETED
    ).all()

    if not shifts:
        return {
            "total_completed": 0,
            "guarantee_triggered": 0,
            "total_topups": 0.0,
            "avg_topup": 0.0,
            "drivers_with_guarantees": 0,
            "per_driver": [],
        }

    triggered = [s for s in shifts if s.guarantee_activated]
    driver_ids = set(s.driver_id for s in shifts)

    per_driver = []
    for did in driver_ids:
        d_shifts = [s for s in shifts if s.driver_id == did]
        d_triggered = [s for s in d_shifts if s.guarantee_activated]
        d_topup = sum(s.topup_amount or 0 for s in d_shifts)
        d_user = db.query(User).filter(User.id == did).first()
        per_driver.append({
            "driver_id": did,
            "driver_name": d_user.full_name if d_user else f"Driver #{did}",
            "completed_shifts": len(d_shifts),
            "guarantees_triggered": len(d_triggered),
            "total_topup": round(d_topup, 2),
        })

    return {
        "total_completed": len(shifts),
        "guarantee_triggered": len(triggered),
        "total_topups": round(sum(s.topup_amount or 0 for s in shifts), 2),
        "avg_topup": round(
            sum(s.topup_amount or 0 for s in triggered) / len(triggered), 2
        ) if triggered else 0.0,
        "drivers_with_guarantees": len([d for d in per_driver if d["guarantees_triggered"] > 0]),
        "per_driver": per_driver,
    }


@router.get("/shifts-overview")
def shifts_overview(db: Session = Depends(get_db)):
    """
    Platform-wide shift breakdown for admin dashboard.
    Real stats from committed_shifts table.
    """
    all_committed = db.query(CommittedShift).all()

    # Group by shift_type
    by_type: dict = {}
    for s in all_committed:
        t = s.shift_type or "Unknown"
        if t not in by_type:
            by_type[t] = {"count": 0, "total_predicted": 0.0, "total_actual": 0.0}
        by_type[t]["count"] += 1
        by_type[t]["total_predicted"] += float(s.predicted_earnings or 0)
        if s.actual_earnings:
            by_type[t]["total_actual"] += float(s.actual_earnings)

    # Group by location
    by_location: dict = {}
    for s in all_committed:
        loc = s.location_name or "Unknown"
        if loc not in by_location:
            by_location[loc] = {"count": 0, "total_predicted": 0.0}
        by_location[loc]["count"] += 1
        by_location[loc]["total_predicted"] += float(s.predicted_earnings or 0)

    # Group by status
    by_status: dict = {}
    for s in all_committed:
        st = s.status.value if hasattr(s.status, 'value') else str(s.status)
        by_status[st] = by_status.get(st, 0) + 1

    return {
        "total_committed": len(all_committed),
        "by_status": by_status,
        "by_type": [
            {"shift_type": k, **v} for k, v in sorted(by_type.items(), key=lambda x: x[1]["count"], reverse=True)
        ],
        "by_location": [
            {"location": k, **v} for k, v in sorted(by_location.items(), key=lambda x: x[1]["count"], reverse=True)
        ],
    }
