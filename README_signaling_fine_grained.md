# Fine-Grained User Signaling Generation

## Overview
This system generates realistic hourly signaling records for campus users based on:
- **User personas** with distinct daily routines
- **Campus zone geography** and base station coverage
- **Temporal patterns** (weekday/weekend, hourly variations)
- **Movement continuity** (users tend to stay in zones for multiple hours)

## Key Features

### 1. Hourly Granularity
- Generates one signaling record per user per hour
- 7-day sample period by default (configurable)
- Total: 50 users × 24 hours × 7 days = **8,400 records**

### 2. Campus Zone Integration
Uses 4 functional zones from `base_station_pos.txt`:

| Zone | Base Stations | POIs | Peak Hours |
|------|---------------|------|------------|
| **Teaching Core** | 14 stations (BS103-BS214) | 教学楼, 图书馆, 宿舍, 食堂 | 8-10, 14-16 (class hours) |
| **South Residential** | 5 stations (BS101, BS102, BS109, BS110, BS302) | 宿舍, 体育馆, 食堂 | 6-7, 22-23 (early/late) |
| **North Commercial** | 6 stations (BS106, BS208, BS215-217, BS209) | 奶茶店, 快餐店, 咖啡店 | 11-13, 17-20 (meals) |
| **East Transport** | 4 stations (BS107, BS108, BS210, BS301) | 交通站点, 快餐店 | 7-8, 17-18 (commute) |

### 3. Persona-Based Daily Schedules

#### Academic (34% of users)
**Weekday pattern:**
- **0-7am**: South Residential (dorm) - 95% → 70% probability
- **8-16pm**: Teaching Core (classes/library) - 85-90% probability
- **17-18pm**: North Commercial (dinner) - 60-70% probability
- **19-21pm**: Teaching Core (study) - 70-80% probability
- **22-23pm**: South Residential (dorm) - 85-90% probability

**Weekend pattern:**
- Later wake-up, more North Commercial activity
- Reduced Teaching Core presence

#### Social Student (16% of users)
**Weekday pattern:**
- **Morning**: South Residential (dorm)
- **11-13pm**: North Commercial (lunch/socializing) - 70-75% probability
- **15-21pm**: North Commercial (peak social hours) - 65-85% probability
- **Late night**: Back to dorm

**Weekend pattern:**
- Extended North Commercial activity (10am-21pm)
- Very high probabilities (80-95%) in commercial zone

#### Foodie (8% of users)
**Key characteristics:**
- **Peak hours**: 11-13pm (lunch), 17-19pm (dinner) in North Commercial - 85-90% probability
- Frequent visits to North Commercial throughout the day
- Lower Teaching Core presence

#### Dormitory Resident (20% of users)
**Key characteristics:**
- **Highest South Residential presence** (90-95% nighttime)
- Minimal movement to other zones
- Weekend: 80-95% stay in residential area

#### Student Athlete (12% of users)
**Key characteristics:**
- **Early morning**: South Residential (training) - 6-7am peak
- **Afternoon/evening**: South Residential (sports) - 15-20pm
- Lower North Commercial activity

#### Commuter (2% of users)
**Key characteristics:**
- **Base**: East Transport zone (60% baseline)
- **Peak commute**: 7-8am, 17-18pm - 85-90% probability
- Moderate Teaching Core presence during day

#### Shopaholic (6% of users)
**Key characteristics:**
- **Consistently high North Commercial presence** (60-95%)
- **Peak shopping hours**: 14-16pm - 90-95% probability
- Weekend shopping even higher (95%)

#### Traveler (2% of users)
**Key characteristics:**
- **Base**: East Transport (50-85%)
- **High mobility**, lower probabilities overall
- Frequent North Commercial visits

### 4. Movement Continuity
The system implements zone persistence:
- **60% probability** to stay in same zone as previous hour
- Prevents unrealistic rapid zone switching
- Models natural human behavior (staying in library for 3+ hours)

### 5. Roaming Type Integration
- **Local users**: Follow persona schedules strictly
- **Remote users**: 30% chance each hour to appear in random zone
- Reflects off-campus activity patterns

## Generated Data

### user_signaling_fine_grained.csv

**Schema:**
```csv
user_id,timestamp,base_station_id,zone,persona_type
U001,2024-06-01 08:30:01,BS204,teaching_core,academic
U001,2024-06-01 09:45:55,BS205,teaching_core,academic
U001,2024-06-01 10:09:57,BS206,teaching_core,academic
```

**Fields:**
- `user_id`: User identifier (U001-U050)
- `timestamp`: YYYY-MM-DD HH:MM:SS format
- `base_station_id`: Connected base station
- `zone`: Campus zone (teaching_core, south_residential, north_commercial, east_transport)
- `persona_type`: User persona

### Sample Statistics (7-day generation)
- **Total records**: 8,400
- **Users**: 50
- **Records per user**: 168 (24 hours × 7 days)
- **Unique base stations**: 29 (all campus stations used)

**Zone Distribution:**
- South Residential: 47.6% (nighttime dominance)
- Teaching Core: 25.2% (academic activities)
- North Commercial: 17.3% (social/food)
- East Transport: 9.9% (commuters/travelers)

**Persona Distribution:**
- Academic: 34.0%
- Dormitory resident: 20.0%
- Social student: 16.0%
- Student athlete: 12.0%
- Foodie: 8.0%
- Shopaholic: 6.0%
- Commuter: 2.0%
- Traveler: 2.0%

## Usage

### Generate Default Data (7 days)
```bash
python generate_user_signaling_fine.py
```

### Customize Generation Period
Edit `generate_user_signaling_fine.py`:
```python
# Change start date
START_DATE = datetime(2024, 9, 1)  # Start from September

# Change duration
DURATION_DAYS = 30  # Generate 1 month of data
```

### Example: Generate 1 month of data
```python
DURATION_DAYS = 30
```
This will produce: 50 users × 24 hours × 30 days = **36,000 records**

## Movement Pattern Examples

### Academic User (U001) - Weekday
```
00:00-07:00  South Residential (BS101, BS102, BS109, BS110, BS302)  [Sleeping]
08:00-10:00  Teaching Core (BS204, BS205, BS206)                     [Morning classes]
11:00-12:00  South Residential (BS109)                               [Lunch at dorm]
13:00-16:00  East Transport (BS107, BS108, BS301)                    [Library/study]
17:00-21:00  North Commercial (BS208, BS209)                         [Dinner & social]
22:00-23:00  South Residential (BS102)                               [Back to dorm]
```

### Social Student (U008) - Weekend
```
00:00-09:00  South Residential (BS110)                               [Late sleep]
10:00-21:00  North Commercial (BS215, BS216, BS217, BS209)          [Shopping & socializing]
22:00-23:00  South Residential (BS302)                               [Return]
```

### Foodie (U016) - Weekday
```
08:00-10:00  Teaching Core (BS203)                                   [Morning class]
11:00-13:00  North Commercial (BS209, BS215)                         [Lunch exploration]
14:00-16:00  Teaching Core (BS204)                                   [Afternoon activity]
17:00-20:00  North Commercial (BS217, BS106, BS216)                 [Dinner tour]
21:00-23:00  South Residential (BS109)                               [Back home]
```

## Technical Implementation

### Schedule Format
```python
PERSONA_SCHEDULES = {
    'academic': {
        'weekday': {
            8: ('teaching_core', 0.85),  # Hour 8: 85% chance in teaching_core
            18: ('north_commercial', 0.60),  # Hour 18: 60% chance in commercial
            ...
        },
        'weekend': { ... }
    }
}
```

### Zone Selection Logic
```python
def select_zone_and_base_station(persona_type, current_time, user_state):
    # 1. Get scheduled zone from persona schedule
    zone_name, prob = schedule[day_type][hour]

    # 2. Apply randomness (user might deviate from schedule)
    if random.random() > prob:
        zone_name = random.choice(alternative_zones)

    # 3. Apply continuity (60% chance to stay in same zone)
    if 'last_zone' in user_state and random.random() < 0.6:
        zone_name = user_state['last_zone']

    # 4. Select base station from zone
    base_station = random.choice(zone_info['base_stations'])

    return zone_name, base_station
```

### Key Differences from Coarse-Grained Version

| Feature | Coarse-Grained | Fine-Grained |
|---------|----------------|--------------|
| **Granularity** | Monthly summaries | Hourly records |
| **Records per user** | 6 (6 months) | 168 (7 days × 24 hours) |
| **Movement detail** | Primary zone only | Hour-by-hour transitions |
| **Base station** | One per month | Changes throughout day |
| **Schedules** | Seasonal patterns | Hourly routines |
| **Use case** | Long-term trends | Short-term behavior, real-time simulation |

## Integration with Existing Data

### Requires:
- `user_activities.csv` - User profiles with persona types
- `base_station_pos.txt` - Base station zone associations (for reference)

### Outputs:
- `user_signaling_fine_grained.csv` - Hourly signaling records

### Compatible with:
- Traffic analysis tools
- Real-time simulation systems
- Movement pattern visualization
- Base station load balancing analysis

## Future Enhancements

Potential improvements:
1. **Event-driven patterns**: Exams, holidays, campus events
2. **Weather effects**: Rain → more indoor activity
3. **Inter-zone transitions**: Explicit transition probabilities
4. **Social clustering**: Friend groups moving together
5. **App-specific location patterns**: Gaming in dorm, studying in library
6. **Handover modeling**: Base station handovers during movement
7. **Signal strength variation**: RSSI values based on distance

## Performance Notes

- **Memory**: ~850KB for 8,400 records (7 days)
- **Generation time**: ~1-2 seconds for 7 days on modern CPU
- **Scalability**:
  - 30 days: ~36,000 records (~3.7MB)
  - 6 months (180 days): ~216,000 records (~22MB)
  - Linear scaling with duration and user count
