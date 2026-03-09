"""Generate fine-grained user signaling data based on user profiles and base station positions.

This script generates hourly signaling records that:
- Respect campus zone geography and base station coverage
- Implement realistic persona-based daily routines
- Model zone-to-zone transitions with transition probabilities
- Apply seasonal behavior patterns
"""
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict

# Configuration
OUTPUT_FILE = 'user_signaling_fine_grained.csv'
START_DATE = datetime(2024, 6, 1)  # June 2024 (summer)
DURATION_DAYS = 7  # One week sample
RECORDS_PER_HOUR = 1  # One signaling record per hour per user

# Campus zone definitions from base_station_pos.txt
CAMPUS_ZONES = {
    'north_commercial': {
        'name': '北门商业区',
        'base_stations': ['BS106', 'BS208', 'BS215', 'BS216', 'BS209', 'BS217'],
        'pois': ['奶茶店', '快餐店', '咖啡店', '便利店'],
        'peak_hours': [11, 12, 13, 17, 18, 19, 20]  # Meal times and evening
    },
    'east_transport': {
        'name': '东门交通枢纽区',
        'base_stations': ['BS107', 'BS108', 'BS210', 'BS301'],
        'pois': ['交通站点', '快餐店'],
        'peak_hours': [7, 8, 17, 18]  # Morning/evening commute
    },
    'teaching_core': {
        'name': '教学与核心设施区',
        'base_stations': ['BS103', 'BS104', 'BS105', 'BS201', 'BS202', 'BS203',
                         'BS204', 'BS205', 'BS206', 'BS207', 'BS211', 'BS212',
                         'BS213', 'BS214'],
        'pois': ['教学楼', '图书馆', '宿舍', '食堂'],
        'peak_hours': [8, 9, 10, 14, 15, 16]  # Class hours
    },
    'south_residential': {
        'name': '南门及西区生活区',
        'base_stations': ['BS101', 'BS102', 'BS109', 'BS110', 'BS302'],
        'pois': ['宿舍', '体育馆', '食堂'],
        'peak_hours': [6, 7, 22, 23]  # Early morning and late night
    }
}

# Hourly schedules by persona type (probability of being in primary zone by hour)
PERSONA_SCHEDULES = {
    'academic': {
        'weekday': {
            0: ('south_residential', 0.95), 1: ('south_residential', 0.95), 2: ('south_residential', 0.95),
            3: ('south_residential', 0.95), 4: ('south_residential', 0.95), 5: ('south_residential', 0.90),
            6: ('south_residential', 0.85), 7: ('south_residential', 0.70), 8: ('teaching_core', 0.85),
            9: ('teaching_core', 0.90), 10: ('teaching_core', 0.90), 11: ('teaching_core', 0.80),
            12: ('teaching_core', 0.75), 13: ('teaching_core', 0.85), 14: ('teaching_core', 0.90),
            15: ('teaching_core', 0.85), 16: ('teaching_core', 0.80), 17: ('teaching_core', 0.70),
            18: ('north_commercial', 0.60), 19: ('teaching_core', 0.70), 20: ('teaching_core', 0.75),
            21: ('teaching_core', 0.80), 22: ('south_residential', 0.85), 23: ('south_residential', 0.90)
        },
        'weekend': {
            0: ('south_residential', 0.95), 1: ('south_residential', 0.95), 2: ('south_residential', 0.95),
            3: ('south_residential', 0.95), 4: ('south_residential', 0.95), 5: ('south_residential', 0.95),
            6: ('south_residential', 0.90), 7: ('south_residential', 0.90), 8: ('south_residential', 0.85),
            9: ('teaching_core', 0.70), 10: ('teaching_core', 0.75), 11: ('north_commercial', 0.60),
            12: ('north_commercial', 0.65), 13: ('teaching_core', 0.60), 14: ('teaching_core', 0.70),
            15: ('teaching_core', 0.65), 16: ('north_commercial', 0.60), 17: ('north_commercial', 0.65),
            18: ('north_commercial', 0.70), 19: ('teaching_core', 0.60), 20: ('teaching_core', 0.65),
            21: ('south_residential', 0.75), 22: ('south_residential', 0.85), 23: ('south_residential', 0.90)
        }
    },
    'social_student': {
        'weekday': {
            0: ('south_residential', 0.90), 1: ('south_residential', 0.95), 2: ('south_residential', 0.95),
            3: ('south_residential', 0.95), 4: ('south_residential', 0.95), 5: ('south_residential', 0.95),
            6: ('south_residential', 0.90), 7: ('south_residential', 0.80), 8: ('teaching_core', 0.75),
            9: ('teaching_core', 0.80), 10: ('teaching_core', 0.75), 11: ('north_commercial', 0.70),
            12: ('north_commercial', 0.75), 13: ('teaching_core', 0.70), 14: ('teaching_core', 0.75),
            15: ('north_commercial', 0.65), 16: ('north_commercial', 0.70), 17: ('north_commercial', 0.75),
            18: ('north_commercial', 0.80), 19: ('north_commercial', 0.85), 20: ('north_commercial', 0.80),
            21: ('north_commercial', 0.75), 22: ('south_residential', 0.80), 23: ('south_residential', 0.85)
        },
        'weekend': {
            0: ('south_residential', 0.85), 1: ('south_residential', 0.90), 2: ('south_residential', 0.95),
            3: ('south_residential', 0.95), 4: ('south_residential', 0.95), 5: ('south_residential', 0.95),
            6: ('south_residential', 0.95), 7: ('south_residential', 0.90), 8: ('south_residential', 0.85),
            9: ('south_residential', 0.80), 10: ('north_commercial', 0.70), 11: ('north_commercial', 0.75),
            12: ('north_commercial', 0.80), 13: ('north_commercial', 0.80), 14: ('north_commercial', 0.75),
            15: ('north_commercial', 0.80), 16: ('north_commercial', 0.85), 17: ('north_commercial', 0.85),
            18: ('north_commercial', 0.90), 19: ('north_commercial', 0.90), 20: ('north_commercial', 0.85),
            21: ('north_commercial', 0.80), 22: ('south_residential', 0.75), 23: ('south_residential', 0.80)
        }
    },
    'foodie': {
        'weekday': {
            0: ('south_residential', 0.95), 1: ('south_residential', 0.95), 2: ('south_residential', 0.95),
            3: ('south_residential', 0.95), 4: ('south_residential', 0.95), 5: ('south_residential', 0.90),
            6: ('south_residential', 0.85), 7: ('south_residential', 0.75), 8: ('teaching_core', 0.70),
            9: ('teaching_core', 0.75), 10: ('teaching_core', 0.70), 11: ('north_commercial', 0.85),
            12: ('north_commercial', 0.90), 13: ('north_commercial', 0.85), 14: ('teaching_core', 0.70),
            15: ('north_commercial', 0.75), 16: ('north_commercial', 0.80), 17: ('north_commercial', 0.85),
            18: ('north_commercial', 0.90), 19: ('north_commercial', 0.85), 20: ('north_commercial', 0.80),
            21: ('south_residential', 0.75), 22: ('south_residential', 0.85), 23: ('south_residential', 0.90)
        },
        'weekend': {
            0: ('south_residential', 0.95), 1: ('south_residential', 0.95), 2: ('south_residential', 0.95),
            3: ('south_residential', 0.95), 4: ('south_residential', 0.95), 5: ('south_residential', 0.95),
            6: ('south_residential', 0.90), 7: ('south_residential', 0.85), 8: ('south_residential', 0.80),
            9: ('north_commercial', 0.75), 10: ('north_commercial', 0.80), 11: ('north_commercial', 0.85),
            12: ('north_commercial', 0.90), 13: ('north_commercial', 0.85), 14: ('north_commercial', 0.80),
            15: ('north_commercial', 0.85), 16: ('north_commercial', 0.85), 17: ('north_commercial', 0.90),
            18: ('north_commercial', 0.90), 19: ('north_commercial', 0.85), 20: ('north_commercial', 0.80),
            21: ('south_residential', 0.75), 22: ('south_residential', 0.85), 23: ('south_residential', 0.90)
        }
    },
    'dormitory_resident': {
        'weekday': {
            0: ('south_residential', 0.95), 1: ('south_residential', 0.95), 2: ('south_residential', 0.95),
            3: ('south_residential', 0.95), 4: ('south_residential', 0.95), 5: ('south_residential', 0.95),
            6: ('south_residential', 0.90), 7: ('south_residential', 0.85), 8: ('teaching_core', 0.80),
            9: ('teaching_core', 0.85), 10: ('teaching_core', 0.80), 11: ('teaching_core', 0.75),
            12: ('south_residential', 0.70), 13: ('teaching_core', 0.75), 14: ('teaching_core', 0.80),
            15: ('teaching_core', 0.75), 16: ('teaching_core', 0.70), 17: ('south_residential', 0.75),
            18: ('south_residential', 0.80), 19: ('south_residential', 0.85), 20: ('south_residential', 0.90),
            21: ('south_residential', 0.90), 22: ('south_residential', 0.95), 23: ('south_residential', 0.95)
        },
        'weekend': {
            0: ('south_residential', 0.95), 1: ('south_residential', 0.95), 2: ('south_residential', 0.95),
            3: ('south_residential', 0.95), 4: ('south_residential', 0.95), 5: ('south_residential', 0.95),
            6: ('south_residential', 0.95), 7: ('south_residential', 0.95), 8: ('south_residential', 0.90),
            9: ('south_residential', 0.90), 10: ('south_residential', 0.85), 11: ('south_residential', 0.80),
            12: ('north_commercial', 0.65), 13: ('south_residential', 0.75), 14: ('south_residential', 0.80),
            15: ('south_residential', 0.80), 16: ('north_commercial', 0.60), 17: ('south_residential', 0.75),
            18: ('south_residential', 0.80), 19: ('south_residential', 0.85), 20: ('south_residential', 0.90),
            21: ('south_residential', 0.90), 22: ('south_residential', 0.95), 23: ('south_residential', 0.95)
        }
    },
    'student_athlete': {
        'weekday': {
            0: ('south_residential', 0.95), 1: ('south_residential', 0.95), 2: ('south_residential', 0.95),
            3: ('south_residential', 0.95), 4: ('south_residential', 0.95), 5: ('south_residential', 0.85),
            6: ('south_residential', 0.75), 7: ('south_residential', 0.70), 8: ('teaching_core', 0.75),
            9: ('teaching_core', 0.80), 10: ('teaching_core', 0.75), 11: ('teaching_core', 0.70),
            12: ('teaching_core', 0.65), 13: ('teaching_core', 0.70), 14: ('teaching_core', 0.75),
            15: ('south_residential', 0.75), 16: ('south_residential', 0.80), 17: ('south_residential', 0.85),
            18: ('south_residential', 0.80), 19: ('south_residential', 0.85), 20: ('south_residential', 0.90),
            21: ('south_residential', 0.90), 22: ('south_residential', 0.95), 23: ('south_residential', 0.95)
        },
        'weekend': {
            0: ('south_residential', 0.95), 1: ('south_residential', 0.95), 2: ('south_residential', 0.95),
            3: ('south_residential', 0.95), 4: ('south_residential', 0.95), 5: ('south_residential', 0.95),
            6: ('south_residential', 0.90), 7: ('south_residential', 0.85), 8: ('south_residential', 0.80),
            9: ('south_residential', 0.85), 10: ('south_residential', 0.85), 11: ('south_residential', 0.80),
            12: ('teaching_core', 0.70), 13: ('south_residential', 0.80), 14: ('south_residential', 0.85),
            15: ('south_residential', 0.85), 16: ('south_residential', 0.85), 17: ('south_residential', 0.85),
            18: ('south_residential', 0.80), 19: ('south_residential', 0.85), 20: ('south_residential', 0.90),
            21: ('south_residential', 0.90), 22: ('south_residential', 0.95), 23: ('south_residential', 0.95)
        }
    },
    'commuter': {
        'weekday': {
            0: ('east_transport', 0.60), 1: ('east_transport', 0.60), 2: ('east_transport', 0.60),
            3: ('east_transport', 0.60), 4: ('east_transport', 0.60), 5: ('east_transport', 0.60),
            6: ('east_transport', 0.70), 7: ('east_transport', 0.85), 8: ('east_transport', 0.90),
            9: ('teaching_core', 0.75), 10: ('teaching_core', 0.80), 11: ('teaching_core', 0.75),
            12: ('north_commercial', 0.65), 13: ('teaching_core', 0.70), 14: ('teaching_core', 0.75),
            15: ('teaching_core', 0.70), 16: ('east_transport', 0.75), 17: ('east_transport', 0.90),
            18: ('east_transport', 0.85), 19: ('east_transport', 0.70), 20: ('east_transport', 0.65),
            21: ('east_transport', 0.65), 22: ('east_transport', 0.60), 23: ('east_transport', 0.60)
        },
        'weekend': {
            0: ('east_transport', 0.60), 1: ('east_transport', 0.60), 2: ('east_transport', 0.60),
            3: ('east_transport', 0.60), 4: ('east_transport', 0.60), 5: ('east_transport', 0.60),
            6: ('east_transport', 0.60), 7: ('east_transport', 0.65), 8: ('east_transport', 0.70),
            9: ('east_transport', 0.70), 10: ('north_commercial', 0.65), 11: ('north_commercial', 0.70),
            12: ('north_commercial', 0.70), 13: ('north_commercial', 0.65), 14: ('north_commercial', 0.65),
            15: ('north_commercial', 0.70), 16: ('north_commercial', 0.70), 17: ('east_transport', 0.75),
            18: ('east_transport', 0.75), 19: ('east_transport', 0.70), 20: ('east_transport', 0.65),
            21: ('east_transport', 0.65), 22: ('east_transport', 0.60), 23: ('east_transport', 0.60)
        }
    },
    'shopaholic': {
        'weekday': {
            0: ('north_commercial', 0.60), 1: ('north_commercial', 0.60), 2: ('north_commercial', 0.60),
            3: ('north_commercial', 0.60), 4: ('north_commercial', 0.60), 5: ('north_commercial', 0.60),
            6: ('north_commercial', 0.60), 7: ('north_commercial', 0.65), 8: ('north_commercial', 0.70),
            9: ('north_commercial', 0.75), 10: ('north_commercial', 0.80), 11: ('north_commercial', 0.85),
            12: ('north_commercial', 0.85), 13: ('north_commercial', 0.85), 14: ('north_commercial', 0.90),
            15: ('north_commercial', 0.90), 16: ('north_commercial', 0.90), 17: ('north_commercial', 0.85),
            18: ('north_commercial', 0.85), 19: ('north_commercial', 0.85), 20: ('north_commercial', 0.80),
            21: ('north_commercial', 0.75), 22: ('north_commercial', 0.70), 23: ('north_commercial', 0.65)
        },
        'weekend': {
            0: ('north_commercial', 0.60), 1: ('north_commercial', 0.60), 2: ('north_commercial', 0.60),
            3: ('north_commercial', 0.60), 4: ('north_commercial', 0.60), 5: ('north_commercial', 0.60),
            6: ('north_commercial', 0.65), 7: ('north_commercial', 0.70), 8: ('north_commercial', 0.75),
            9: ('north_commercial', 0.80), 10: ('north_commercial', 0.85), 11: ('north_commercial', 0.90),
            12: ('north_commercial', 0.90), 13: ('north_commercial', 0.90), 14: ('north_commercial', 0.95),
            15: ('north_commercial', 0.95), 16: ('north_commercial', 0.95), 17: ('north_commercial', 0.90),
            18: ('north_commercial', 0.90), 19: ('north_commercial', 0.85), 20: ('north_commercial', 0.85),
            21: ('north_commercial', 0.80), 22: ('north_commercial', 0.75), 23: ('north_commercial', 0.70)
        }
    },
    'traveler': {
        'weekday': {
            0: ('east_transport', 0.50), 1: ('east_transport', 0.50), 2: ('east_transport', 0.50),
            3: ('east_transport', 0.50), 4: ('east_transport', 0.50), 5: ('east_transport', 0.55),
            6: ('east_transport', 0.65), 7: ('east_transport', 0.80), 8: ('east_transport', 0.85),
            9: ('east_transport', 0.70), 10: ('north_commercial', 0.65), 11: ('north_commercial', 0.70),
            12: ('north_commercial', 0.70), 13: ('north_commercial', 0.65), 14: ('north_commercial', 0.65),
            15: ('north_commercial', 0.70), 16: ('east_transport', 0.75), 17: ('east_transport', 0.85),
            18: ('east_transport', 0.80), 19: ('east_transport', 0.70), 20: ('east_transport', 0.60),
            21: ('east_transport', 0.55), 22: ('east_transport', 0.55), 23: ('east_transport', 0.50)
        },
        'weekend': {
            0: ('east_transport', 0.50), 1: ('east_transport', 0.50), 2: ('east_transport', 0.50),
            3: ('east_transport', 0.50), 4: ('east_transport', 0.50), 5: ('east_transport', 0.50),
            6: ('east_transport', 0.60), 7: ('east_transport', 0.75), 8: ('east_transport', 0.80),
            9: ('east_transport', 0.75), 10: ('east_transport', 0.70), 11: ('north_commercial', 0.70),
            12: ('north_commercial', 0.70), 13: ('north_commercial', 0.70), 14: ('north_commercial', 0.70),
            15: ('north_commercial', 0.75), 16: ('north_commercial', 0.75), 17: ('east_transport', 0.80),
            18: ('east_transport', 0.85), 19: ('east_transport', 0.75), 20: ('east_transport', 0.65),
            21: ('east_transport', 0.60), 22: ('east_transport', 0.55), 23: ('east_transport', 0.50)
        }
    }
}

# Default schedule for personas not defined above
DEFAULT_SCHEDULE = {
    'weekday': {hour: ('teaching_core', 0.70) for hour in range(24)},
    'weekend': {hour: ('south_residential', 0.75) for hour in range(24)}
}

def get_season(month: int) -> str:
    """Determine season from month"""
    if month in [6, 7, 8]:
        return 'summer'
    elif month in [9, 10]:
        return 'fall'
    else:
        return 'winter'

def read_user_profiles(filename: str = 'user_activities.csv') -> List[Dict]:
    """Read user profile data"""
    users = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append(row)
    return users

def select_zone_and_base_station(
    persona_type: str,
    current_time: datetime,
    user_state: Dict
) -> Tuple[str, str]:
    """
    Select zone and base station based on persona schedule and time.

    Args:
        persona_type: User persona type
        current_time: Current timestamp
        user_state: User's current state (for continuity)

    Returns:
        (zone_name, base_station_id)
    """
    hour = current_time.hour
    is_weekend = current_time.weekday() >= 5

    # Get schedule for this persona
    schedule = PERSONA_SCHEDULES.get(persona_type, DEFAULT_SCHEDULE)
    day_type = 'weekend' if is_weekend else 'weekday'

    zone_name, prob = schedule[day_type][hour]

    # Apply some randomness - user might be in different zone
    if random.random() > prob:
        # Select a random alternative zone
        all_zones = list(CAMPUS_ZONES.keys())
        all_zones.remove(zone_name)
        zone_name = random.choice(all_zones)

    # Add some continuity - prefer staying in same zone for consecutive hours
    if 'last_zone' in user_state and random.random() < 0.6:
        zone_name = user_state['last_zone']

    # Select base station from zone
    zone_info = CAMPUS_ZONES[zone_name]
    base_station = random.choice(zone_info['base_stations'])

    # Update user state
    user_state['last_zone'] = zone_name
    user_state['last_bs'] = base_station

    return zone_name, base_station

def generate_signaling_records(
    users: List[Dict],
    start_date: datetime,
    duration_days: int
) -> List[Dict]:
    """
    Generate fine-grained signaling records.

    Args:
        users: List of user profile dictionaries
        start_date: Start date for signaling data
        duration_days: Number of days to generate

    Returns:
        List of signaling record dictionaries
    """
    print(f"\nGenerating fine-grained signaling records...")
    print(f"Period: {start_date.date()} to {(start_date + timedelta(days=duration_days-1)).date()}")
    print(f"Duration: {duration_days} days")

    signaling_records = []
    user_states = {}  # Track user state for continuity

    # Generate hourly records
    for day_offset in range(duration_days):
        current_date = start_date + timedelta(days=day_offset)
        season = get_season(current_date.month)

        for hour in range(24):
            current_time = current_date.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))

            for user in users:
                user_id = user['user_id']
                persona_type = user['persona_type']
                roaming_type = user['roaming_type']

                # Initialize user state if needed
                if user_id not in user_states:
                    user_states[user_id] = {}

                # Remote users have more random patterns
                if roaming_type == 'remote' and random.random() < 0.3:
                    # 30% chance to be in random zone
                    zone_name = random.choice(list(CAMPUS_ZONES.keys()))
                    base_station = random.choice(CAMPUS_ZONES[zone_name]['base_stations'])
                else:
                    # Select zone and base station based on schedule
                    zone_name, base_station = select_zone_and_base_station(
                        persona_type,
                        current_time,
                        user_states[user_id]
                    )

                signaling_records.append({
                    'user_id': user_id,
                    'timestamp': current_time,
                    'base_station_id': base_station,
                    'zone': zone_name,
                    'persona_type': persona_type
                })

        # Progress indicator
        if (day_offset + 1) % 1 == 0:
            print(f"  Processed day {day_offset + 1}/{duration_days} ({current_date.date()})...")

    print(f"\nGenerated {len(signaling_records)} signaling records")
    print(f"  Users: {len(users)}")
    print(f"  Average records per user: {len(signaling_records) / len(users):.1f}")

    return signaling_records

def save_signaling_data(signaling_records: List[Dict], output_file: str):
    """Save signaling records to CSV"""
    print(f"\nSaving data to {output_file}...")

    # Sort by timestamp and user_id
    signaling_records.sort(key=lambda x: (x['timestamp'], x['user_id']))

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['user_id', 'timestamp', 'base_station_id', 'zone', 'persona_type']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for record in signaling_records:
            # Format timestamp
            record['timestamp'] = record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow(record)

    print(f"Successfully saved {len(signaling_records)} records")

    # Statistics
    unique_users = len(set(r['user_id'] for r in signaling_records))
    unique_stations = len(set(r['base_station_id'] for r in signaling_records))
    zone_counts = defaultdict(int)
    persona_counts = defaultdict(int)

    for record in signaling_records:
        zone_counts[record['zone']] += 1
        persona_counts[record['persona_type']] += 1

    print("\n=== Statistics ===")
    print(f"Total records: {len(signaling_records)}")
    print(f"Unique users: {unique_users}")
    print(f"Unique base stations: {unique_stations}")

    print("\nZone Distribution:")
    for zone, count in sorted(zone_counts.items(), key=lambda x: x[1], reverse=True):
        zone_name = CAMPUS_ZONES[zone]['name']
        percentage = (count / len(signaling_records)) * 100
        print(f"  {zone_name} ({zone}): {count} ({percentage:.1f}%)")

    print("\nPersona Distribution:")
    for persona, count in sorted(persona_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(signaling_records)) * 100
        print(f"  {persona}: {count} ({percentage:.1f}%)")

def main():
    """Main execution function"""
    print("=" * 70)
    print("Fine-Grained User Signaling Data Generator")
    print("=" * 70)

    # Read user profiles
    print("\nReading user profiles...")
    users = read_user_profiles('user_activities.csv')
    print(f"Loaded {len(users)} users")

    # Generate signaling records
    signaling_records = generate_signaling_records(
        users,
        START_DATE,
        DURATION_DAYS
    )

    # Save to file
    save_signaling_data(signaling_records, OUTPUT_FILE)

    print("\n" + "=" * 70)
    print("Generation complete!")
    print(f"Output file: {OUTPUT_FILE}")
    print("=" * 70)

if __name__ == '__main__':
    main()
