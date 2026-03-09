"""Generate random user signaling data based on user activities and base stations."""
import csv
import random
from datetime import datetime, timedelta

# Configuration
OUTPUT_FILE = 'user_signaling_generated.csv'
START_DATE = datetime(2025, 12, 1)
END_DATE = datetime(2025, 12, 7, 23, 59, 59)
MIN_RECORDS_PER_USER = 8
MAX_RECORDS_PER_USER = 15

# Time distribution weights (for realistic daily patterns)
# Hours of day: 0-5 (night), 6-9 (morning peak), 9-17 (business), 17-22 (evening), 22-24 (late)
HOUR_WEIGHTS = [
    0.5, 0.5, 0.3, 0.3, 0.3, 0.5,  # 0-5am (low activity)
    2.0, 3.0, 3.5, 2.5,             # 6-9am (morning peak)
    2.0, 2.5, 3.0, 2.5, 2.0,        # 10-14 (business hours)
    2.5, 2.0, 3.0,                  # 15-17 (afternoon)
    3.5, 3.0, 2.5, 2.0,             # 18-21 (evening peak)
    1.5, 1.0                        # 22-23 (late evening)
]

def read_data():
    """Read user activities and base station data"""
    print("Reading input data...")

    # Read users
    users = []
    with open('user_activities.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append(row)

    # Read base stations
    base_stations = []
    with open('base_station.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            base_stations.append(row)

    print(f"Loaded {len(users)} users")
    print(f"Loaded {len(base_stations)} base stations")

    return users, base_stations

def generate_timestamp(start_date, end_date, hour_weights):
    """Generate a random timestamp with realistic daily patterns"""
    # Random day within range
    total_seconds = int((end_date - start_date).total_seconds())
    random_seconds = random.randint(0, total_seconds)
    random_date = start_date + timedelta(seconds=random_seconds)

    # Apply hour weighting for more realistic patterns
    weighted_hour = random.choices(range(24), weights=hour_weights, k=1)[0]

    # Create timestamp with weighted hour but random minutes/seconds
    timestamp = random_date.replace(
        hour=weighted_hour,
        minute=random.randint(0, 59),
        second=random.randint(0, 59)
    )

    return timestamp

def select_primary_stations(base_stations, count):
    """Select primary base stations for local users"""
    return random.sample(base_stations, min(count, len(base_stations)))

def generate_signaling_records(users, base_stations):
    """Generate signaling records for all users"""
    print("\nGenerating signaling records...")

    all_base_stations = [bs['base_station_id'] for bs in base_stations]
    signaling_records = []

    # Group users by roaming type for statistics
    local_users = [u for u in users if u['roaming_type'] == 'local']
    remote_users = [u for u in users if u['roaming_type'] == 'remote']

    print(f"Local users: {len(local_users)}")
    print(f"Remote users: {len(remote_users)}")

    # Process each user
    for idx, user_row in enumerate(users):
        user_id = user_row['user_id']
        roaming_type = user_row['roaming_type']

        # Determine number of records for this user
        num_records = random.randint(MIN_RECORDS_PER_USER, MAX_RECORDS_PER_USER)

        # Generate base station selection strategy based on roaming type
        if roaming_type == 'local':
            # Local users: select 2-5 primary stations
            num_primary = random.randint(2, 5)
            primary_stations = select_primary_stations(all_base_stations, num_primary)

            # 80% connections to primary, 20% to any station
            for _ in range(num_records):
                if random.random() < 0.8:
                    # Primary station
                    base_station = random.choice(primary_stations)
                else:
                    # Any station
                    base_station = random.choice(all_base_stations)

                timestamp = generate_timestamp(START_DATE, END_DATE, HOUR_WEIGHTS)
                signaling_records.append({
                    'user_id': user_id,
                    'timestamp': timestamp,
                    'base_station_id': base_station
                })
        else:
            # Remote users: random connections across all stations
            for _ in range(num_records):
                base_station = random.choice(all_base_stations)
                timestamp = generate_timestamp(START_DATE, END_DATE, HOUR_WEIGHTS)
                signaling_records.append({
                    'user_id': user_id,
                    'timestamp': timestamp,
                    'base_station_id': base_station
                })

        # Progress indicator
        if (idx + 1) % 100 == 0:
            print(f"Processed {idx + 1}/{len(users)} users...")

    print(f"Generated {len(signaling_records)} total signaling records")
    return signaling_records

def save_signaling_data(signaling_records, output_file):
    """Save signaling records to CSV"""
    print(f"\nSaving data to {output_file}...")

    # Sort by user_id and timestamp for clean output
    signaling_records.sort(key=lambda x: (x['user_id'], x['timestamp']))

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['user_id', 'timestamp', 'base_station_id']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for record in signaling_records:
            # Format timestamp as string
            record['timestamp'] = record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow(record)

    print(f"Successfully saved {len(signaling_records)} records to {output_file}")

    # Calculate statistics
    unique_users = len(set(r['user_id'] for r in signaling_records))
    unique_stations = len(set(r['base_station_id'] for r in signaling_records))
    timestamps = [r['timestamp'] for r in signaling_records]

    # Print statistics
    print("\n=== Statistics ===")
    print(f"Total records: {len(signaling_records)}")
    print(f"Unique users: {unique_users}")
    print(f"Unique base stations used: {unique_stations}")
    print(f"Date range: {min(timestamps)} to {max(timestamps)}")
    print(f"Average records per user: {len(signaling_records) / unique_users:.1f}")

def main():
    """Main execution function"""
    print("=" * 60)
    print("User Signaling Data Generator")
    print("=" * 60)

    # Read input data
    users, base_stations = read_data()

    # Generate signaling records
    signaling_records = generate_signaling_records(users, base_stations)

    # Save to file
    save_signaling_data(signaling_records, OUTPUT_FILE)

    print("\n" + "=" * 60)
    print("Generation complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
