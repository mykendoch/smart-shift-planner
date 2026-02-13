"""
Seed Guarantee Demo Data

Creates realistic committed shifts for the demo driver account to demonstrate
the full Income Guarantee Window:
- Mix of completed shifts (with actual earnings - some above/below guarantee)
- Currently committed shifts (pending)
- One cancelled shift

This provides a complete demo of:
- FR7: Shift commitments
- FR8: Guarantee activation (when actual < guaranteed minimum)
- FR10: Real-time earnings tracking
- FR11: Earnings comparison (predicted vs actual)
- FR12: Top-up calculations
- FR13: Guarantee logging (audit trail)
- FR14: Volatility analysis (with/without guarantee)
- FR15: Performance reporting

Run: python scripts/seed_guarantee_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models.committed_shift import CommittedShift, GuaranteeLog, ShiftStatus
from src.models.user import User

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Guarantee threshold
GUARANTEE_THRESHOLD = 0.9


def seed_guarantee_data():
    """Seed realistic committed shifts and guarantee logs for demo."""
    db: Session = SessionLocal()

    try:
        # Find the demo driver (user id=4, driver@example.com)
        driver = db.query(User).filter(User.email == "driver@example.com").first()
        if not driver:
            logger.error("Demo driver (driver@example.com) not found. Run seed_admin.py first.")
            return

        driver_id = driver.id
        logger.info(f"Seeding guarantee data for driver: {driver.full_name} (id={driver_id})")

        # Check if data already exists
        existing = db.query(CommittedShift).filter(
            CommittedShift.driver_id == driver_id
        ).count()
        if existing > 0:
            logger.info(f"Found {existing} existing committed shifts. Clearing and re-seeding...")
            db.query(GuaranteeLog).filter(GuaranteeLog.driver_id == driver_id).delete()
            db.query(CommittedShift).filter(CommittedShift.driver_id == driver_id).delete()
            db.commit()

        now = datetime.utcnow()

        # =====================================================================
        # COMPLETED SHIFTS (with actual earnings)
        # Mix of over/under guarantee to show top-up calculations
        # =====================================================================

        completed_shifts = [
            # Shift 1: Heathrow Morning Rush - Earnings ABOVE guarantee (no top-up)
            {
                "location_name": "London Heathrow Airport",
                "location_key": "london_heathrow",
                "region": "London",
                "zone": "Airport Zone",
                "shift_type": "Morning Rush",
                "day_name": "Monday",
                "start_time": now - timedelta(days=12, hours=5),
                "end_time": now - timedelta(days=12),
                "predicted_earnings": 168.00,
                "actual_earnings": 175.50,    # ABOVE guaranteed min (£151.20)
                "base_hourly_rate": 28.00,
                "demand_score": 92.0,
            },
            # Shift 2: Central London Evening - Earnings BELOW guarantee (TOP-UP!)
            {
                "location_name": "Central London",
                "location_key": "central_london",
                "region": "London",
                "zone": "City Centre",
                "shift_type": "Evening Peak",
                "day_name": "Tuesday",
                "start_time": now - timedelta(days=10, hours=4),
                "end_time": now - timedelta(days=10),
                "predicted_earnings": 135.00,
                "actual_earnings": 102.50,    # BELOW guaranteed min (£121.50) → TOP-UP £19.00
                "base_hourly_rate": 22.50,
                "demand_score": 85.0,
            },
            # Shift 3: Manchester Airport - Earnings slightly below guarantee (small top-up)
            {
                "location_name": "Manchester Airport",
                "location_key": "manchester_airport",
                "region": "North West",
                "zone": "Airport Zone",
                "shift_type": "Mid-Day Steady",
                "day_name": "Wednesday",
                "start_time": now - timedelta(days=8, hours=6),
                "end_time": now - timedelta(days=8),
                "predicted_earnings": 120.00,
                "actual_earnings": 105.00,    # BELOW guaranteed min (£108.00) → TOP-UP £3.00
                "base_hourly_rate": 20.00,
                "demand_score": 72.0,
            },
            # Shift 4: Birmingham City Centre - Earnings well above
            {
                "location_name": "Birmingham City Centre",
                "location_key": "birmingham",
                "region": "West Midlands",
                "zone": "City Centre",
                "shift_type": "Morning Rush",
                "day_name": "Thursday",
                "start_time": now - timedelta(days=7, hours=5),
                "end_time": now - timedelta(days=7),
                "predicted_earnings": 95.00,
                "actual_earnings": 112.00,    # ABOVE guaranteed min (£85.50) — great shift!
                "base_hourly_rate": 19.00,
                "demand_score": 68.0,
            },
            # Shift 5: Heathrow Weekend - Earnings BELOW (weekend surge predicted, actual lower)
            {
                "location_name": "London Heathrow Airport",
                "location_key": "london_heathrow",
                "region": "London",
                "zone": "Airport Zone",
                "shift_type": "Weekend Premium",
                "day_name": "Saturday",
                "start_time": now - timedelta(days=5, hours=5),
                "end_time": now - timedelta(days=5),
                "predicted_earnings": 189.00,
                "actual_earnings": 145.00,    # BELOW guaranteed min (£170.10) → TOP-UP £25.10
                "base_hourly_rate": 28.00,
                "demand_score": 95.0,
            },
            # Shift 6: Edinburgh - Earnings right at the guarantee threshold
            {
                "location_name": "Edinburgh City Centre",
                "location_key": "edinburgh",
                "region": "Scotland",
                "zone": "City Centre",
                "shift_type": "Evening Peak",
                "day_name": "Friday",
                "start_time": now - timedelta(days=4, hours=4),
                "end_time": now - timedelta(days=4),
                "predicted_earnings": 110.00,
                "actual_earnings": 99.00,     # EXACTLY at guaranteed min (£99.00) → no top-up
                "base_hourly_rate": 18.50,
                "demand_score": 74.0,
            },
            # Shift 7: Bristol - Earnings significantly below (bad shift)
            {
                "location_name": "Bristol",
                "location_key": "bristol",
                "region": "South West",
                "zone": "City Centre",
                "shift_type": "Late Night",
                "day_name": "Sunday",
                "start_time": now - timedelta(days=3, hours=5),
                "end_time": now - timedelta(days=3),
                "predicted_earnings": 105.00,
                "actual_earnings": 68.50,     # BELOW guaranteed min (£94.50) → TOP-UP £26.00
                "base_hourly_rate": 17.50,
                "demand_score": 55.0,
            },
            # Shift 8: Central London Morning - Good earnings
            {
                "location_name": "Central London",
                "location_key": "central_london",
                "region": "London",
                "zone": "City Centre",
                "shift_type": "Morning Rush",
                "day_name": "Monday",
                "start_time": now - timedelta(days=2, hours=5),
                "end_time": now - timedelta(days=2),
                "predicted_earnings": 150.00,
                "actual_earnings": 162.00,    # ABOVE guaranteed min (£135.00)
                "base_hourly_rate": 22.50,
                "demand_score": 88.0,
            },
        ]

        # =====================================================================
        # COMMITTED (PENDING) SHIFTS - upcoming
        # =====================================================================

        committed_shifts = [
            {
                "location_name": "London Heathrow Airport",
                "location_key": "london_heathrow",
                "region": "London",
                "zone": "Airport Zone",
                "shift_type": "Morning Rush",
                "day_name": "Wednesday",
                "start_time": now + timedelta(days=1, hours=2),
                "end_time": now + timedelta(days=1, hours=7),
                "predicted_earnings": 168.00,
                "base_hourly_rate": 28.00,
                "demand_score": 91.0,
            },
            {
                "location_name": "Central London",
                "location_key": "central_london",
                "region": "London",
                "zone": "City Centre",
                "shift_type": "Evening Peak",
                "day_name": "Thursday",
                "start_time": now + timedelta(days=2, hours=5),
                "end_time": now + timedelta(days=2, hours=9),
                "predicted_earnings": 135.00,
                "base_hourly_rate": 22.50,
                "demand_score": 84.0,
            },
        ]

        # =====================================================================
        # CANCELLED SHIFT
        # =====================================================================

        cancelled_shift = {
            "location_name": "Leeds Bradford Airport",
            "location_key": "leeds",
            "region": "Yorkshire",
            "zone": "Airport Zone",
            "shift_type": "Mid-Day Steady",
            "day_name": "Sunday",
            "start_time": now - timedelta(days=6, hours=6),
            "end_time": now - timedelta(days=6),
            "predicted_earnings": 85.00,
            "base_hourly_rate": 17.00,
            "demand_score": 48.0,
        }

        # =====================================================================
        # INSERT COMPLETED SHIFTS + GUARANTEE CALCULATIONS
        # =====================================================================

        logger.info("\n=== Seeding COMPLETED shifts ===")
        for i, shift_data in enumerate(completed_shifts, 1):
            cs = CommittedShift(
                driver_id=driver_id,
                location_name=shift_data["location_name"],
                location_key=shift_data["location_key"],
                region=shift_data["region"],
                zone=shift_data["zone"],
                shift_type=shift_data["shift_type"],
                day_name=shift_data["day_name"],
                start_time=shift_data["start_time"],
                end_time=shift_data["end_time"],
                predicted_earnings=shift_data["predicted_earnings"],
                actual_earnings=shift_data["actual_earnings"],
                base_hourly_rate=shift_data["base_hourly_rate"],
                demand_score=shift_data["demand_score"],
                guarantee_eligible=True,
                guarantee_threshold=GUARANTEE_THRESHOLD,
                status=ShiftStatus.COMPLETED.value,
                completed_at=shift_data["end_time"],
                commitment_time=shift_data["start_time"] - timedelta(hours=12),
            )
            cs.calculate_guarantee()
            db.add(cs)
            db.commit()
            db.refresh(cs)

            # Log commitment event
            log_commit = GuaranteeLog(
                committed_shift_id=cs.id,
                driver_id=driver_id,
                event_type="commitment",
                event_description=f"Driver committed to {cs.shift_type} at {cs.location_name}",
                predicted_earnings=cs.predicted_earnings,
                guaranteed_minimum=cs.guaranteed_minimum,
                guarantee_threshold=GUARANTEE_THRESHOLD,
                was_eligible=True,
            )
            db.add(log_commit)

            # Log earnings recorded
            log_earn = GuaranteeLog(
                committed_shift_id=cs.id,
                driver_id=driver_id,
                event_type="earnings_recorded",
                event_description=(
                    f"Actual earnings: £{cs.actual_earnings:.2f}. "
                    f"Predicted: £{cs.predicted_earnings:.2f}. "
                    f"Guaranteed min: £{cs.guaranteed_minimum:.2f}."
                ),
                predicted_earnings=cs.predicted_earnings,
                actual_earnings=cs.actual_earnings,
                guaranteed_minimum=cs.guaranteed_minimum,
                topup_amount=cs.topup_amount,
                guarantee_threshold=GUARANTEE_THRESHOLD,
            )
            db.add(log_earn)

            # If guarantee activated, log that too
            if cs.guarantee_activated:
                log_activate = GuaranteeLog(
                    committed_shift_id=cs.id,
                    driver_id=driver_id,
                    event_type="guarantee_activated",
                    event_description=(
                        f"Income guarantee ACTIVATED. "
                        f"Actual £{cs.actual_earnings:.2f} < "
                        f"Guaranteed £{cs.guaranteed_minimum:.2f}. "
                        f"Top-up: £{cs.topup_amount:.2f}"
                    ),
                    predicted_earnings=cs.predicted_earnings,
                    actual_earnings=cs.actual_earnings,
                    guaranteed_minimum=cs.guaranteed_minimum,
                    topup_amount=cs.topup_amount,
                    guarantee_threshold=GUARANTEE_THRESHOLD,
                    was_eligible=True,
                )
                db.add(log_activate)
                topup_msg = f" → TOP-UP £{cs.topup_amount:.2f}"
            else:
                topup_msg = " → No top-up needed"

            db.commit()

            logger.info(
                f"  [{i}] {cs.location_name} ({cs.shift_type}) — "
                f"Predicted: £{cs.predicted_earnings:.2f}, "
                f"Actual: £{cs.actual_earnings:.2f}, "
                f"Guarantee min: £{cs.guaranteed_minimum:.2f}"
                f"{topup_msg}"
            )

        # =====================================================================
        # INSERT COMMITTED (PENDING) SHIFTS
        # =====================================================================

        logger.info("\n=== Seeding COMMITTED (pending) shifts ===")
        for i, shift_data in enumerate(committed_shifts, 1):
            cs = CommittedShift(
                driver_id=driver_id,
                location_name=shift_data["location_name"],
                location_key=shift_data["location_key"],
                region=shift_data["region"],
                zone=shift_data["zone"],
                shift_type=shift_data["shift_type"],
                day_name=shift_data["day_name"],
                start_time=shift_data["start_time"],
                end_time=shift_data["end_time"],
                predicted_earnings=shift_data["predicted_earnings"],
                base_hourly_rate=shift_data["base_hourly_rate"],
                demand_score=shift_data["demand_score"],
                guarantee_eligible=True,
                guarantee_threshold=GUARANTEE_THRESHOLD,
                guaranteed_minimum=round(shift_data["predicted_earnings"] * GUARANTEE_THRESHOLD, 2),
                status=ShiftStatus.COMMITTED.value,
            )
            db.add(cs)
            db.commit()
            db.refresh(cs)

            # Log commitment
            log = GuaranteeLog(
                committed_shift_id=cs.id,
                driver_id=driver_id,
                event_type="commitment",
                event_description=f"Driver committed to {cs.shift_type} at {cs.location_name}",
                predicted_earnings=cs.predicted_earnings,
                guaranteed_minimum=cs.guaranteed_minimum,
                guarantee_threshold=GUARANTEE_THRESHOLD,
                was_eligible=True,
            )
            db.add(log)
            db.commit()

            logger.info(
                f"  [{i}] {cs.location_name} ({cs.shift_type}) — "
                f"Predicted: £{cs.predicted_earnings:.2f}, "
                f"Guaranteed min: £{cs.guaranteed_minimum:.2f} [PENDING]"
            )

        # =====================================================================
        # INSERT CANCELLED SHIFT
        # =====================================================================

        logger.info("\n=== Seeding CANCELLED shift ===")
        cs_cancel = CommittedShift(
            driver_id=driver_id,
            location_name=cancelled_shift["location_name"],
            location_key=cancelled_shift["location_key"],
            region=cancelled_shift["region"],
            zone=cancelled_shift["zone"],
            shift_type=cancelled_shift["shift_type"],
            day_name=cancelled_shift["day_name"],
            start_time=cancelled_shift["start_time"],
            end_time=cancelled_shift["end_time"],
            predicted_earnings=cancelled_shift["predicted_earnings"],
            base_hourly_rate=cancelled_shift["base_hourly_rate"],
            demand_score=cancelled_shift["demand_score"],
            guarantee_eligible=True,
            guarantee_threshold=GUARANTEE_THRESHOLD,
            guaranteed_minimum=round(cancelled_shift["predicted_earnings"] * GUARANTEE_THRESHOLD, 2),
            status=ShiftStatus.CANCELLED.value,
            cancelled_at=cancelled_shift["start_time"] - timedelta(hours=2),
        )
        db.add(cs_cancel)
        db.commit()
        db.refresh(cs_cancel)

        log_cancel = GuaranteeLog(
            committed_shift_id=cs_cancel.id,
            driver_id=driver_id,
            event_type="cancellation",
            event_description=f"Driver cancelled shift at {cs_cancel.location_name}",
            guarantee_threshold=GUARANTEE_THRESHOLD,
        )
        db.add(log_cancel)
        db.commit()

        logger.info(
            f"  [1] {cs_cancel.location_name} ({cs_cancel.shift_type}) — "
            f"Predicted: £{cs_cancel.predicted_earnings:.2f} [CANCELLED]"
        )

        # =====================================================================
        # SUMMARY
        # =====================================================================

        total = db.query(CommittedShift).filter(
            CommittedShift.driver_id == driver_id
        ).count()
        total_logs = db.query(GuaranteeLog).filter(
            GuaranteeLog.driver_id == driver_id
        ).count()

        completed_list = db.query(CommittedShift).filter(
            CommittedShift.driver_id == driver_id,
            CommittedShift.status == ShiftStatus.COMPLETED.value,
        ).all()

        total_predicted = sum(s.predicted_earnings for s in completed_list)
        total_actual = sum(s.actual_earnings or 0 for s in completed_list)
        total_topup = sum(s.topup_amount or 0 for s in completed_list)
        activations = sum(1 for s in completed_list if s.guarantee_activated)

        logger.info(f"\n{'='*60}")
        logger.info(f"GUARANTEE SEED DATA COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"  Total committed shifts: {total}")
        logger.info(f"  - Completed:  {len(completed_list)}")
        logger.info(f"  - Pending:    {len(committed_shifts)}")
        logger.info(f"  - Cancelled:  1")
        logger.info(f"  Total audit logs: {total_logs}")
        logger.info(f"")
        logger.info(f"  Completed Shifts Summary:")
        logger.info(f"    Total predicted: £{total_predicted:.2f}")
        logger.info(f"    Total actual:    £{total_actual:.2f}")
        logger.info(f"    Total top-ups:   £{total_topup:.2f}")
        logger.info(f"    Guarantees activated: {activations}/{len(completed_list)}")
        logger.info(f"    Activation rate: {activations/len(completed_list)*100:.1f}%")
        logger.info(f"{'='*60}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding guarantee data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_guarantee_data()
