"""
Dataset Expansion Script

Generates 500+ simulated shifts with realistic patterns for research analysis.

Features:
- Creates shifts across multiple workers
- Realistic earnings patterns (location, time, demand variations)
- Seasonal and temporal patterns
- Income guarantee top-ups
- Ready for statistical analysis
"""
import os
import sys
from datetime import datetime, timedelta
import random
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database import SessionLocal, Base, engine
from src.models import Worker, Shift
from src.core.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

# Database parameters
DB_RANGE_DAYS = 60  # Generate 60 days of data
NUM_WORKERS = 15    # Create 15 workers
SHIFTS_PER_WORKER = 40  # ~40 shifts per worker = 600 total shifts


class DatasetGenerator:
    """Generate realistic shift data for research."""
    
    def __init__(self):
        self.db = SessionLocal()
        self.locations = ["downtown", "airport", "residential", "highway"]
        self.workers = []
        
    def create_workers(self):
        """Create test workers if they don't exist."""
        logger.info(f"Creating {NUM_WORKERS} test workers...")
        
        existing = self.db.query(Worker).count()
        logger.info(f"Existing workers: {existing}")
        
        first_names = [
            "John", "Jane", "Michael", "Sarah", "David", "Emma",
            "Robert", "Lisa", "James", "Mary", "William", "Patricia",
            "Richard", "Jennifer", "Joseph", "Linda"
        ]
        
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
            "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez",
            "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas"
        ]
        
        created = 0
        for i in range(NUM_WORKERS):
            # Check if worker already exists
            existing_worker = self.db.query(Worker).filter(
                Worker.email == f"worker{i}@gig.local"
            ).first()
            
            if not existing_worker:
                worker = Worker(
                    name=f"{first_names[i % len(first_names)]} {last_names[i]}",
                    email=f"worker{i}@gig.local"
                )
                self.db.add(worker)
                self.workers.append(worker)
                created += 1
            else:
                self.workers.append(existing_worker)
        
        if created > 0:
            self.db.commit()
            logger.info(f"Created {created} new workers")
        else:
            logger.info("All workers already exist")
    
    def generate_realistic_earnings(self, location: str, hour: int, 
                                   day_of_week: int, demand_multiplier: float) -> float:
        """Generate realistic earnings based on multiple factors."""
        
        # Base earnings by location
        base_earnings = {
            "downtown": 18.0,
            "airport": 22.0,
            "residential": 12.0,
            "highway": 15.0
        }
        base = base_earnings.get(location, 16.0)
        
        # Time multiplier (peak hours earn more)
        if 6 <= hour < 9:  # Morning rush
            time_mult = 1.3
        elif 9 <= hour < 12:  # Morning
            time_mult = 1.0
        elif 12 <= hour < 17:  # Afternoon
            time_mult = 0.9
        elif 17 <= hour < 21:  # Evening peak
            time_mult = 1.4
        elif 21 <= hour < 6:  # Night
            time_mult = 1.1
        else:
            time_mult = 1.0
        
        # Day multiplier
        day_multipliers = [0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.12]
        day_mult = day_multipliers[day_of_week]
        
        # Combine all factors
        base_hourly = base * time_mult * day_mult
        
        # Add some randomness (normal distribution)
        random_factor = random.normalvariate(1.0, 0.15)  # Mean 1.0, std 0.15
        random_factor = max(0.7, min(1.3, random_factor))  # Clamp between 0.7-1.3
        
        # Apply demand multiplier
        hourly_earnings = base_hourly * random_factor * demand_multiplier
        
        return round(hourly_earnings, 2)
    
    def generate_predicted_earnings(self, actual_earnings: float) -> float:
        """Generate predicted earnings (slightly different from actual)."""
        # Predictions are sometimes high, sometimes low
        prediction_accuracy = random.triangular(0.75, 1.25, 1.0)  # Mode=1.0
        predicted = actual_earnings * prediction_accuracy
        
        # Add small variance
        variance = random.normalvariate(0, 0.05)
        predicted = predicted * (1 + variance)
        
        return round(max(0.1, predicted), 2)
    
    def create_shifts(self):
        """Create 500+ realistic shifts."""
        logger.info(f"Generating {SHIFTS_PER_WORKER * len(self.workers)} shifts...")
        
        # Get the earliest time for the data range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=DB_RANGE_DAYS)
        
        created = 0
        
        for worker_idx, worker in enumerate(self.workers):
            logger.info(f"  Generating shifts for worker {worker_idx + 1}/{len(self.workers)}...")
            
            for _ in range(SHIFTS_PER_WORKER):
                # Random date within range
                random_days = random.randint(0, DB_RANGE_DAYS - 1)
                shift_date = start_date + timedelta(days=random_days)
                
                # Random start hour
                start_hour = random.choice([6, 8, 10, 14, 15, 17, 19, 22])
                duration = random.choice([2, 3, 4, 5, 6, 8])  # Hours
                
                start_time = shift_date.replace(hour=start_hour, minute=0, second=0)
                end_hour = (start_hour + duration) % 24
                end_time = start_time.replace(hour=end_hour)
                
                # Handle day transition
                if end_hour < start_hour:
                    end_time = end_time + timedelta(days=1)
                
                # Random location
                location = random.choice(self.locations)
                
                # Demand varies by time and location
                base_demand = 0.5
                if location == "airport":
                    base_demand = 0.6
                elif location == "downtown":
                    base_demand = 0.55
                
                demand_variance = random.normalvariate(0, 0.15)
                demand_multiplier = max(0.3, min(1.0, base_demand + demand_variance))
                
                # Generate earnings
                actual_earnings = self.generate_realistic_earnings(
                    location, start_hour, shift_date.weekday(), demand_multiplier
                ) * duration
                
                predicted_earnings = self.generate_predicted_earnings(actual_earnings)
                
                # Create shift
                shift = Shift(
                    worker_id=worker.id,
                    start_time=start_time,
                    end_time=end_time,
                    earnings=actual_earnings,
                    predicted_earnings=predicted_earnings
                )
                
                self.db.add(shift)
                created += 1
                
                # Commit in batches of 50
                if created % 50 == 0:
                    self.db.commit()
                    logger.debug(f"    Committed {created} shifts...")
        
        # Final commit
        self.db.commit()
        logger.info(f"✓ Created {created} new shifts")
        
        return created
    
    def print_statistics(self):
        """Print statistics about the generated data."""
        logger.info("\n" + "="*70)
        logger.info("DATASET STATISTICS")
        logger.info("="*70)
        
        total_workers = self.db.query(Worker).count()
        total_shifts = self.db.query(Shift).count()
        
        logger.info(f"Total workers: {total_workers}")
        logger.info(f"Total shifts: {total_shifts}")
        
        if total_shifts > 0:
            # Earnings statistics
            total_earnings = sum(s.earnings or 0 for s in self.db.query(Shift).all())
            avg_earnings = total_earnings / total_shifts
            
            logger.info(f"\nEarnings Summary:")
            logger.info(f"  Total earnings across all shifts: ${total_earnings:,.2f}")
            logger.info(f"  Average per shift: ${avg_earnings:.2f}")
            
            # Top-up statistics
            top_up_count = 0
            total_top_ups = 0
            
            for shift in self.db.query(Shift).all():
                actual = shift.earnings or 0
                predicted = shift.predicted_earnings or 0
                expected = predicted * 0.9
                topup = max(0, expected - actual)
                
                if topup > 0:
                    top_up_count += 1
                    total_top_ups += topup
            
            logger.info(f"\nIncome Guarantee Summary:")
            logger.info(f"  Shifts receiving top-up: {top_up_count} ({top_up_count/total_shifts*100:.1f}%)")
            logger.info(f"  Total top-ups paid: ${total_top_ups:,.2f}")
            logger.info(f"  Average top-up: ${total_top_ups/max(1, top_up_count):.2f}")
            
            # Worker statistics
            logger.info(f"\nWorker Statistics:")
            for worker in self.db.query(Worker).limit(5):
                worker_shifts = self.db.query(Shift).filter(
                    Shift.worker_id == worker.id
                ).all()
                worker_earnings = sum(s.earnings or 0 for s in worker_shifts)
                logger.info(f"  {worker.name}: {len(worker_shifts)} shifts, ${worker_earnings:.2f} earned")
        
        logger.info("="*70 + "\n")
    
    def run(self):
        """Execute the full dataset generation."""
        logger.info("Starting dataset expansion...")
        
        try:
            self.create_workers()
            self.create_shifts()
            self.print_statistics()
            logger.info("✓ Dataset expansion complete!")
            
        except Exception as e:
            logger.error(f"Error during dataset generation: {e}", exc_info=True)
            self.db.rollback()
            raise
        finally:
            self.db.close()


if __name__ == "__main__":
    logger.info("="*70)
    logger.info("SMART SHIFT PLANNER - DATASET EXPANSION")
    logger.info("="*70)
    logger.info(f"Configuration:")
    logger.info(f"  Days of data: {DB_RANGE_DAYS}")
    logger.info(f"  Number of workers: {NUM_WORKERS}")
    logger.info(f"  Shifts per worker: {SHIFTS_PER_WORKER}")
    logger.info(f"  Total shifts: ~{NUM_WORKERS * SHIFTS_PER_WORKER}")
    logger.info("="*70)
    
    generator = DatasetGenerator()
    generator.run()
