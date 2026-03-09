import csv
import random
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

# Campus zone definitions based on base_station_pos.txt
CAMPUS_ZONES = {
    'north_commercial': {
        'name': '北门商业区',
        'lat_range': (32.0484, 32.0487),
        'lon_range': (118.7918, 118.7926),
        'base_stations': ['BS106', 'BS208', 'BS215', 'BS216', 'BS209', 'BS217'],
        'pois': ['奶茶店', '快餐店', '咖啡店', '便利店'],
        'user_types': ['social_student', 'foodie', 'shopaholic']
    },
    'east_transport': {
        'name': '东门交通枢纽区',
        'lat_range': (32.0489, 32.0491),
        'lon_range': (118.7928, 118.7932),
        'base_stations': ['BS107', 'BS108', 'BS210', 'BS301'],
        'pois': ['交通站点', '快餐店'],
        'user_types': ['commuter', 'traveler']
    },
    'teaching_core': {
        'name': '教学与核心设施区',
        'lat_range': (32.0468, 32.0484),
        'lon_range': (118.7888, 118.7919),
        'base_stations': ['BS103', 'BS104', 'BS105', 'BS201', 'BS202', 'BS203',
                         'BS204', 'BS205', 'BS206', 'BS207', 'BS211', 'BS212',
                         'BS213', 'BS214'],
        'pois': ['教学楼', '图书馆', '宿舍', '食堂'],
        'user_types': ['academic', 'dormitory_resident', 'student_athlete']
    },
    'south_residential': {
        'name': '南门及西区生活区',
        'lat_range': (32.0439, 32.0458),
        'lon_range': (118.7868, 118.7878),
        'base_stations': ['BS101', 'BS102', 'BS109', 'BS110', 'BS302'],
        'pois': ['宿舍', '体育馆', '食堂'],
        'user_types': ['dormitory_resident', 'student_athlete', 'local_resident']
    }
}

# User persona definitions with zone preferences and seasonal behaviors
USER_PERSONAS = {
    'academic': {
        'arpu_levels': ['<20', '20-50', '30-50'],
        'weights': [0.4, 0.4, 0.2],
        'base_apps': ['learning', 'productivity', 'news', 'finance'],
        'seasonal_apps': {
            'summer': ['travel', 'outdoor_activities'],
            'fall': ['educational_content', 'library_apps'],
            'winter': ['indoor_study', 'online_courses']
        },
        'primary_zones': ['teaching_core'],
        'secondary_zones': ['north_commercial', 'south_residential'],
        'roaming_type': 'local',
        'roaming_prob': 0.8
    },
    'social_student': {
        'arpu_levels': ['20-50', '30-50', '50-100'],
        'weights': [0.3, 0.4, 0.3],
        'base_apps': ['social', 'messaging', 'shotvideo', 'music'],
        'seasonal_apps': {
            'summer': ['dating', 'travel', 'outdoor_events'],
            'fall': ['social', 'campus_events'],
            'winter': ['streaming', 'indoor_entertainment']
        },
        'primary_zones': ['north_commercial', 'teaching_core'],
        'secondary_zones': ['east_transport'],
        'roaming_type': 'mixed',
        'roaming_prob': 0.5
    },
    'foodie': {
        'arpu_levels': ['30-50', '50-100', '>100'],
        'weights': [0.3, 0.5, 0.2],
        'base_apps': ['take-away', 'food_delivery', 'food_reviews', 'navigation'],
        'seasonal_apps': {
            'summer': ['ice_cream', 'cold_drinks', 'outdoor_dining'],
            'fall': ['restaurant_discovery'],
            'winter': ['hot_pot', 'delivery', 'indoor_dining']
        },
        'primary_zones': ['north_commercial'],
        'secondary_zones': ['teaching_core', 'south_residential'],
        'roaming_type': 'local',
        'roaming_prob': 0.7
    },
    'dormitory_resident': {
        'arpu_levels': ['<20', '20-50', '30-50'],
        'weights': [0.5, 0.3, 0.2],
        'base_apps': ['gaming', 'streaming', 'social', 'utility'],
        'seasonal_apps': {
            'summer': ['outdoor_activities', 'sports'],
            'fall': ['study_apps', 'campus_life'],
            'winter': ['indoor_gaming', 'streaming', 'delivery']
        },
        'primary_zones': ['teaching_core', 'south_residential'],
        'secondary_zones': ['north_commercial'],
        'roaming_type': 'local',
        'roaming_prob': 0.9
    },
    'student_athlete': {
        'arpu_levels': ['20-50', '30-50', '50-100'],
        'weights': [0.4, 0.4, 0.2],
        'base_apps': ['fitness', 'sports', 'health', 'social'],
        'seasonal_apps': {
            'summer': ['outdoor_sports', 'running', 'cycling'],
            'fall': ['team_sports', 'training'],
            'winter': ['indoor_sports', 'gym']
        },
        'primary_zones': ['south_residential'],
        'secondary_zones': ['teaching_core', 'north_commercial'],
        'roaming_type': 'local',
        'roaming_prob': 0.85
    },
    'commuter': {
        'arpu_levels': ['50-100', '>100'],
        'weights': [0.6, 0.4],
        'base_apps': ['navigation', 'news', 'music', 'productivity'],
        'seasonal_apps': {
            'summer': ['travel', 'bike_sharing'],
            'fall': ['commute_planning'],
            'winter': ['indoor_nav', 'weather', 'transport_apps']
        },
        'primary_zones': ['east_transport'],
        'secondary_zones': ['teaching_core', 'north_commercial'],
        'roaming_type': 'remote',
        'roaming_prob': 0.3
    },
    'shopaholic': {
        'arpu_levels': ['50-100', '>100'],
        'weights': [0.4, 0.6],
        'base_apps': ['shopping', 'fashion', 'lifestyle', 'social'],
        'seasonal_apps': {
            'summer': ['summer_fashion', 'online_shopping'],
            'fall': ['fall_collection', 'retail'],
            'winter': ['winter_sales', 'luxury_shopping']
        },
        'primary_zones': ['north_commercial'],
        'secondary_zones': ['east_transport'],
        'roaming_type': 'remote',
        'roaming_prob': 0.4
    },
    'traveler': {
        'arpu_levels': ['>100'],
        'weights': [1.0],
        'base_apps': ['travel', 'navigation', 'booking', 'photography'],
        'seasonal_apps': {
            'summer': ['summer_travel', 'beach', 'adventure'],
            'fall': ['autumn_tours', 'cultural_travel'],
            'winter': ['winter_destinations', 'indoor_attractions']
        },
        'primary_zones': ['east_transport'],
        'secondary_zones': ['north_commercial'],
        'roaming_type': 'remote',
        'roaming_prob': 0.2
    }
}

def get_season(month: int) -> str:
    """Determine season from month (6-11: summer to winter)"""
    if month in [6, 7, 8]:
        return 'summer'
    elif month in [9, 10]:
        return 'fall'
    else:  # 11, 12
        return 'winter'

def generate_user_entries(n: int = 10, output_file: str = "user_activities.csv") -> None:
    """
    Generate user activity entries based on campus zones, personas, and seasons.
    Args:
        n: Number of users to generate
        output_file: Output CSV file name
    """
    entries = []

    # Distribute users across personas
    persona_names = list(USER_PERSONAS.keys())
    persona_distribution = [
        0.25,  # academic
        0.20,  # social_student
        0.15,  # foodie
        0.20,  # dormitory_resident
        0.10,  # student_athlete
        0.05,  # commuter
        0.03,  # shopaholic
        0.02   # traveler
    ]

    for i in range(1, n + 1):
        user_id = f"U{str(i).zfill(3)}"

        # Select persona
        persona_type = random.choices(persona_names, weights=persona_distribution)[0]
        persona = USER_PERSONAS[persona_type]

        # Select ARPU level based on persona
        arpu_level = random.choices(persona['arpu_levels'], weights=persona['weights'])[0]

        # Generate app preferences (base + seasonal variety)
        base_apps = list(persona['base_apps'])

        # Add seasonal apps from all seasons for variety
        seasonal_apps = []
        for season_apps in persona['seasonal_apps'].values():
            seasonal_apps.extend(season_apps)

        # Select 3-7 apps total
        num_apps = random.randint(3, 7)
        num_base = min(len(base_apps), random.randint(2, 4))
        num_seasonal = max(0, min(num_apps - num_base, len(seasonal_apps)))

        selected_base = random.sample(base_apps, num_base)
        selected_seasonal = random.sample(seasonal_apps, num_seasonal) if num_seasonal > 0 else []

        app_preference = ';'.join(selected_base + selected_seasonal)

        # Determine roaming type
        if persona['roaming_type'] == 'mixed':
            roaming_type = random.choice(['local', 'remote'])
        else:
            roaming_type = 'local' if random.random() < persona['roaming_prob'] else 'remote'

        entries.append([user_id, arpu_level, app_preference, roaming_type, persona_type])

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['user_id', 'arpu_level', 'app_preference', 'roaming_type', 'persona_type'])
        writer.writerows(entries)

    print(f"Generated {n} user profiles in '{output_file}'")

    # Display sample
    print("\nSample of generated data:")
    for entry in entries[:5]:
        print(f"{entry[0]}, {entry[1]}, {entry[4]}, '{entry[2][:50]}...', {entry[3]}")

def generate_seasonal_movements(
    user_profile_file: str = "user_activities.csv",
    output_file: str = "user_movements_6months.csv",
    start_month: int = 6,
    start_year: int = 2024
) -> None:
    """
    Generate 6-month coarse-grained movement patterns for users.

    Args:
        user_profile_file: User profile CSV file
        output_file: Output file for movement data
        start_month: Starting month (default 6 for June)
        start_year: Starting year
    """
    # Read user profiles
    with open(user_profile_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        users = list(reader)

    movements = []

    # Generate monthly summaries (coarse-grained)
    for month_offset in range(6):  # 6 months
        current_month = (start_month + month_offset - 1) % 12 + 1
        current_year = start_year + (start_month + month_offset - 1) // 12
        season = get_season(current_month)

        for user in users:
            user_id = user['user_id']
            persona_type = user['persona_type']
            persona = USER_PERSONAS[persona_type]

            # Determine primary zone activity
            primary_zone = random.choice(persona['primary_zones'])
            zone_info = CAMPUS_ZONES[primary_zone]

            # Select base station from primary zone
            primary_bs = random.choice(zone_info['base_stations'])

            # Calculate zone visit distribution (coarse-grained: monthly summary)
            # Primary zone: 60-80% of time
            # Secondary zones: 20-40% of time
            primary_visits = random.randint(60, 80)

            # Seasonal behavior adjustments
            seasonal_modifier = 1.0
            if season == 'summer':
                # More outdoor activity, more travel
                if persona_type in ['traveler', 'student_athlete']:
                    seasonal_modifier = 1.2
            elif season == 'winter':
                # More indoor activity, less movement
                if persona_type in ['dormitory_resident', 'academic']:
                    seasonal_modifier = 0.8

            # App usage intensity (based on ARPU and season)
            arpu_level = user['arpu_level']
            if arpu_level == '>100':
                data_usage_mb = random.randint(8000, 15000)
            elif arpu_level in ['50-100']:
                data_usage_mb = random.randint(4000, 8000)
            elif arpu_level in ['30-50', '20-50']:
                data_usage_mb = random.randint(2000, 4000)
            else:  # <20
                data_usage_mb = random.randint(500, 2000)

            # Seasonal adjustment to data usage
            data_usage_mb = int(data_usage_mb * seasonal_modifier)

            # Call activity
            if arpu_level in ['>100', '50-100']:
                call_minutes = random.randint(200, 500)
            else:
                call_minutes = random.randint(50, 200)

            movements.append([
                user_id,
                persona_type,
                f"{current_year}-{current_month:02d}",
                season,
                primary_zone,
                primary_bs,
                primary_visits,
                data_usage_mb,
                call_minutes
            ])

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'user_id', 'persona_type', 'month', 'season', 'primary_zone',
            'primary_base_station', 'zone_visits_percent', 'data_usage_mb', 'call_minutes'
        ])
        writer.writerows(movements)

    print(f"\nGenerated 6-month movement patterns in '{output_file}'")
    print(f"Period: {start_year}-{start_month:02d} to {start_year + 6//12}-{(start_month + 5) % 12 + 1:02d}")
    print(f"Total records: {len(movements)} ({len(users)} users × 6 months)")

def analyze_data(filename: str = "user_activities.csv") -> None:
    """
    Analyze the generated user profile data.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)

        print(f"\nAnalysis of '{filename}':")
        print(f"Total users: {len(data)}")

        # Count distributions
        arpu_counts = {}
        roaming_counts = {}
        persona_counts = {}

        for row in data:
            arpu = row['arpu_level']
            roaming = row['roaming_type']
            persona = row.get('persona_type', 'unknown')

            arpu_counts[arpu] = arpu_counts.get(arpu, 0) + 1
            roaming_counts[roaming] = roaming_counts.get(roaming, 0) + 1
            persona_counts[persona] = persona_counts.get(persona, 0) + 1

        print("\nARPU Distribution:")
        for level, count in sorted(arpu_counts.items()):
            percentage = (count / len(data)) * 100
            print(f"  {level}: {count} ({percentage:.1f}%)")

        print("\nRoaming Distribution:")
        for rtype, count in roaming_counts.items():
            percentage = (count / len(data)) * 100
            print(f"  {rtype}: {count} ({percentage:.1f}%)")

        print("\nPersona Distribution:")
        for persona, count in sorted(persona_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(data)) * 100
            print(f"  {persona}: {count} ({percentage:.1f}%)")

    except FileNotFoundError:
        print(f"File '{filename}' not found.")

def analyze_movements(filename: str = "user_movements_6months.csv") -> None:
    """
    Analyze the generated movement data.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)

        print(f"\nAnalysis of '{filename}':")
        print(f"Total records: {len(data)}")

        # Season distribution
        season_counts = {}
        zone_counts = {}
        bs_counts = {}

        total_data_usage = 0
        total_call_minutes = 0

        for row in data:
            season = row['season']
            zone = row['primary_zone']
            bs = row['primary_base_station']

            season_counts[season] = season_counts.get(season, 0) + 1
            zone_counts[zone] = zone_counts.get(zone, 0) + 1
            bs_counts[bs] = bs_counts.get(bs, 0) + 1

            total_data_usage += int(row['data_usage_mb'])
            total_call_minutes += int(row['call_minutes'])

        print("\nSeasonal Distribution:")
        for season, count in sorted(season_counts.items()):
            percentage = (count / len(data)) * 100
            print(f"  {season}: {count} records ({percentage:.1f}%)")

        print("\nZone Activity (Top 4):")
        for zone, count in sorted(zone_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(data)) * 100
            zone_name = CAMPUS_ZONES[zone]['name']
            print(f"  {zone_name}: {count} ({percentage:.1f}%)")

        print("\nTop 10 Base Stations:")
        for bs, count in sorted(bs_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / len(data)) * 100
            print(f"  {bs}: {count} ({percentage:.1f}%)")

        print(f"\nAverage data usage: {total_data_usage / len(data):.0f} MB/month")
        print(f"Average call minutes: {total_call_minutes / len(data):.0f} min/month")

    except FileNotFoundError:
        print(f"File '{filename}' not found.")

if __name__ == "__main__":
    # Generate 50 user profiles
    print("=" * 60)
    print("Generating User Profiles")
    print("=" * 60)
    generate_user_entries(n=50)

    # Analyze user profiles
    analyze_data("user_activities.csv")

    print("\n" + "=" * 60)
    print("Generating 6-Month Movement Patterns (June - November 2024)")
    print("=" * 60)

    # Generate 6-month movement patterns
    generate_seasonal_movements(
        user_profile_file="user_activities.csv",
        output_file="user_movements_6months.csv",
        start_month=6,
        start_year=2024
    )

    # Analyze movement patterns
    analyze_movements("user_movements_6months.csv")