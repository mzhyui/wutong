# Enhanced User Profile Generation System

## Overview
This system generates realistic user profiles and movement patterns for a campus environment, integrating:
- **Campus zones** and base station positions
- **User personas** with distinct behavioral characteristics
- **Seasonal patterns** covering 6 months (summer to winter)
- **Location-aware preferences** based on campus geography

## Key Features

### 1. Campus Zones (Based on base_station_pos.txt)

Four functional zones with specific base station coverage:

| Zone | Chinese Name | Base Stations | POI Types | User Types |
|------|-------------|---------------|-----------|------------|
| **north_commercial** | 北门商业区 | BS106, BS208, BS215, BS216, BS209, BS217 | 奶茶店, 快餐店, 咖啡店, 便利店 | social_student, foodie, shopaholic |
| **east_transport** | 东门交通枢纽区 | BS107, BS108, BS210, BS301 | 交通站点, 快餐店 | commuter, traveler |
| **teaching_core** | 教学与核心设施区 | BS103-105, BS201-207, BS211-214 (14 stations) | 教学楼, 图书馆, 宿舍, 食堂 | academic, dormitory_resident, student_athlete |
| **south_residential** | 南门及西区生活区 | BS101, BS102, BS109, BS110, BS302 | 宿舍, 体育馆, 食堂 | dormitory_resident, student_athlete |

### 2. User Personas

Eight distinct user personas with realistic behaviors:

#### Academic (25% of users)
- **ARPU**: <20 (40%), 20-50 (40%), 30-50 (20%)
- **Apps**: learning, productivity, news, finance
- **Seasonal**: summer (travel, outdoor), fall (educational content), winter (online courses)
- **Primary zones**: teaching_core
- **Roaming**: 80% local

#### Social Student (20% of users)
- **ARPU**: 20-50 (30%), 30-50 (40%), 50-100 (30%)
- **Apps**: social, messaging, shotvideo, music
- **Seasonal**: summer (dating, travel), fall (campus events), winter (streaming)
- **Primary zones**: north_commercial, teaching_core
- **Roaming**: 50% local/remote

#### Foodie (15% of users)
- **ARPU**: 30-50 (30%), 50-100 (50%), >100 (20%)
- **Apps**: take-away, food_delivery, food_reviews, navigation
- **Seasonal**: summer (cold drinks), fall (restaurant discovery), winter (hot pot, delivery)
- **Primary zones**: north_commercial
- **Roaming**: 70% local

#### Dormitory Resident (20% of users)
- **ARPU**: <20 (50%), 20-50 (30%), 30-50 (20%)
- **Apps**: gaming, streaming, social, utility
- **Seasonal**: summer (outdoor activities), fall (study apps), winter (indoor gaming, streaming)
- **Primary zones**: teaching_core, south_residential
- **Roaming**: 90% local

#### Student Athlete (10% of users)
- **ARPU**: 20-50 (40%), 30-50 (40%), 50-100 (20%)
- **Apps**: fitness, sports, health, social
- **Seasonal**: summer (outdoor sports, running), fall (team sports), winter (indoor sports, gym)
- **Primary zones**: south_residential
- **Roaming**: 85% local

#### Commuter (5% of users)
- **ARPU**: 50-100 (60%), >100 (40%)
- **Apps**: navigation, news, music, productivity
- **Seasonal**: summer (travel, bike sharing), fall (commute planning), winter (weather, transport apps)
- **Primary zones**: east_transport
- **Roaming**: 30% local (70% remote)

#### Shopaholic (3% of users)
- **ARPU**: 50-100 (40%), >100 (60%)
- **Apps**: shopping, fashion, lifestyle, social
- **Seasonal**: summer (summer fashion), fall (fall collection), winter (winter sales, luxury)
- **Primary zones**: north_commercial
- **Roaming**: 40% local

#### Traveler (2% of users)
- **ARPU**: >100 (100%)
- **Apps**: travel, navigation, booking, photography
- **Seasonal**: summer (beach, adventure), fall (cultural travel), winter (winter destinations)
- **Primary zones**: east_transport
- **Roaming**: 20% local (80% remote)

### 3. Seasonal Patterns (6 Months: June - November 2024)

**Seasons**:
- **Summer** (June, July, August): More outdoor activity, higher travel, increased data usage for travelers/athletes
- **Fall** (September, October): Campus life returns to normal, balanced activity
- **Winter** (November): More indoor activity, increased delivery/streaming, reduced movement

**Seasonal Modifiers**:
- Travelers & Athletes in summer: +20% data usage
- Academics & Dormitory residents in winter: -20% data usage

### 4. Generated Data

#### user_activities.csv
Contains user static profiles:
- `user_id`: U001-U050
- `arpu_level`: <20, 20-50, 30-50, 50-100, >100
- `app_preference`: Semicolon-separated list of apps (3-7 apps)
- `roaming_type`: local/remote
- `persona_type`: One of 8 personas

#### user_movements_6months.csv
Contains monthly movement patterns (300 records = 50 users × 6 months):
- `user_id`: User identifier
- `persona_type`: User persona
- `month`: YYYY-MM format (2024-06 to 2024-11)
- `season`: summer/fall/winter
- `primary_zone`: Main campus zone frequented
- `primary_base_station`: Most used base station
- `zone_visits_percent`: 60-80% (primary zone visit proportion)
- `data_usage_mb`: Monthly data consumption (500-15000 MB based on ARPU)
- `call_minutes`: Monthly call duration (50-500 min based on ARPU)

## Usage

### Generate New Data
```bash
python generate_user_profile.py
```

This will:
1. Generate 50 user profiles in `user_activities.csv`
2. Generate 6-month movement patterns in `user_movements_6months.csv`
3. Display analysis summaries

### Customize Generation
Edit `generate_user_profile.py`:
```python
# Change number of users
generate_user_entries(n=100)

# Change time period
generate_seasonal_movements(
    start_month=9,  # Start from September
    start_year=2024
)
```

## Data Statistics (Current Run)

### User Profiles
- Total users: 50
- ARPU distribution: 44% (20-50), 22% (30-50), 14% (<20), 12% (50-100), 8% (>100)
- Roaming: 76% local, 24% remote
- Top personas: Academic (34%), Dormitory resident (20%), Social student (16%)

### Movement Patterns
- Total records: 300 (50 users × 6 months)
- Season distribution: 50% summer, 33.3% fall, 16.7% winter
- Zone activity: Teaching core (51.7%), South residential (22.3%), North commercial (22%)
- Top base stations: BS204 (6.3%), BS104 (5.3%), BS209 (5.3%)
- Average data usage: 3804 MB/month
- Average call minutes: 169 min/month

## Integration with Base Stations

The system ensures realistic mapping:
- Each persona has primary zones matching their behavior
- Base stations are selected from the appropriate zone's coverage area
- Movement patterns reflect zone connectivity (primary vs secondary zones)
- Data usage correlates with ARPU levels and seasonal activity

## Future Enhancements

Potential additions:
- Hourly movement patterns (fine-grained)
- Inter-zone transition probabilities
- Event-driven behaviors (exams, holidays)
- Social network effects between users
- App-specific data usage patterns
