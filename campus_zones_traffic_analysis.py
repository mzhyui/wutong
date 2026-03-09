"""
Campus Zones Traffic Analysis and Visualization

Analyzes traffic patterns across ALL FOUR major campus zones:
1. North Commercial Zone (北门商业区)
2. East Transport Hub (东门交通枢纽区)
3. Teaching Core Zone (教学与核心设施区)
4. South Residential Zone (南门及西区生活区)

Based on:
- Base station positions and coverage
- User signaling data (both coarse and fine-grained)
- Temporal patterns and user personas
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
from collections import defaultdict
import os

# Set Chinese font for matplotlib
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# All four campus zones with their base stations
CAMPUS_ZONES = {
    'north_commercial': {
        'name': '北门商业区',
        'name_en': 'North Commercial',
        'stations': ['BS106', 'BS208', 'BS215', 'BS216', 'BS209', 'BS217'],
        'color': '#E63946',
        'description': 'Shopping, dining, entertainment'
    },
    'east_transport': {
        'name': '东门交通枢纽区',
        'name_en': 'East Transport Hub',
        'stations': ['BS107', 'BS108', 'BS210', 'BS301'],
        'color': '#F4A261',
        'description': 'Transit station, fast food'
    },
    'teaching_core': {
        'name': '教学与核心设施区',
        'name_en': 'Teaching Core',
        'stations': ['BS103', 'BS104', 'BS105', 'BS201', 'BS202', 'BS203',
                    'BS204', 'BS205', 'BS206', 'BS207', 'BS211', 'BS212',
                    'BS213', 'BS214'],
        'color': '#2A9D8F',
        'description': 'Classrooms, library, cafeteria'
    },
    'south_residential': {
        'name': '南门及西区生活区',
        'name_en': 'South Residential',
        'stations': ['BS101', 'BS102', 'BS109', 'BS110', 'BS302'],
        'color': '#457B9D',
        'description': 'Dormitories, gym, dining'
    }
}

def load_data():
    """Load all required data files"""
    print("Loading data files...")

    # Load base stations
    base_stations = pd.read_csv('base_station.csv')
    print(f"  ✓ Loaded {len(base_stations)} base stations")

    # Load coarse-grained signaling (2025-12-01 to 2025-12-07)
    signaling_coarse = pd.read_csv('user_signaling_generated.csv')
    signaling_coarse['timestamp'] = pd.to_datetime(signaling_coarse['timestamp'])
    print(f"  ✓ Loaded {len(signaling_coarse)} coarse-grained signaling records")

    # Load fine-grained signaling (2024-06-01 to 2024-06-07)
    signaling_fine = pd.read_csv('user_signaling_fine_grained.csv')
    signaling_fine['timestamp'] = pd.to_datetime(signaling_fine['timestamp'])
    print(f"  ✓ Loaded {len(signaling_fine)} fine-grained signaling records")

    # Load user activities for persona information
    user_activities = pd.read_csv('user_activities.csv')
    print(f"  ✓ Loaded {len(user_activities)} user profiles")

    return base_stations, signaling_coarse, signaling_fine, user_activities

def filter_zone_traffic(signaling_df, station_list):
    """Filter signaling data for specific zone base stations"""
    zone_traffic = signaling_df[
        signaling_df['base_station_id'].isin(station_list)
    ].copy()
    return zone_traffic

def analyze_all_zones(signaling_fine):
    """Analyze traffic patterns for all four zones"""
    print("\nAnalyzing traffic for all four zones...")

    zone_data = {}

    for zone_id, zone_info in CAMPUS_ZONES.items():
        print(f"  Processing {zone_info['name']}...")

        # Filter data for this zone
        zone_df = filter_zone_traffic(signaling_fine, zone_info['stations'])

        # Extract temporal features
        zone_df['hour'] = zone_df['timestamp'].dt.hour
        zone_df['date'] = zone_df['timestamp'].dt.date
        zone_df['day_of_week'] = zone_df['timestamp'].dt.dayofweek
        zone_df['is_weekend'] = zone_df['day_of_week'] >= 5

        # Calculate statistics
        hourly_traffic = zone_df.groupby('hour').size()
        weekday_traffic = zone_df[~zone_df['is_weekend']].groupby('hour').size()
        weekend_traffic = zone_df[zone_df['is_weekend']].groupby('hour').size()
        bs_traffic = zone_df.groupby('base_station_id').size().sort_values(ascending=False)

        # Persona distribution
        persona_traffic = None
        if 'persona_type' in zone_df.columns:
            persona_traffic = zone_df.groupby('persona_type').size().sort_values(ascending=False)

        # Peak hours
        peak_hours = hourly_traffic.nlargest(5)
        off_peak_hours = hourly_traffic.nsmallest(5)

        zone_data[zone_id] = {
            'df': zone_df,
            'hourly': hourly_traffic,
            'weekday': weekday_traffic,
            'weekend': weekend_traffic,
            'bs_traffic': bs_traffic,
            'persona': persona_traffic,
            'peak_hours': peak_hours,
            'off_peak_hours': off_peak_hours
        }

    return zone_data

def plot_zones_comparison_hourly(zone_data):
    """Compare hourly traffic patterns across all four zones"""
    fig, ax = plt.subplots(figsize=(16, 8))

    hours = range(24)
    for zone_id, data in zone_data.items():
        zone_info = CAMPUS_ZONES[zone_id]
        ax.plot(hours, data['hourly'], marker='o', linewidth=2.5, markersize=6,
               label=f"{zone_info['name']} ({zone_info['name_en']})",
               color=zone_info['color'])

    ax.set_xlabel('Hour of Day', fontsize=13, fontweight='bold')
    ax.set_ylabel('Number of Connections', fontsize=13, fontweight='bold')
    ax.set_title('Hourly Traffic Comparison Across Four Campus Zones',
                fontsize=15, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks(hours)
    ax.legend(loc='best', fontsize=11, framealpha=0.9)

    # Highlight key time periods
    ax.axvspan(8, 10, alpha=0.1, color='yellow', label='Morning Classes')
    ax.axvspan(11, 13, alpha=0.1, color='orange', label='Lunch Time')
    ax.axvspan(17, 20, alpha=0.1, color='red', label='Evening Peak')

    plt.tight_layout()
    plt.savefig('zones_hourly_comparison.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: zones_hourly_comparison.png")
    plt.close()

def plot_zones_traffic_share(zone_data):
    """Plot traffic share pie chart and bar chart"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    zone_totals = {}
    colors = []
    labels = []

    for zone_id, data in zone_data.items():
        zone_info = CAMPUS_ZONES[zone_id]
        total = len(data['df'])
        zone_totals[zone_id] = total
        colors.append(zone_info['color'])
        labels.append(f"{zone_info['name']}\n{zone_info['name_en']}")

    # Pie chart
    ax1 = axes[0]
    wedges, texts, autotexts = ax1.pie(zone_totals.values(), labels=labels,
                                         autopct='%1.1f%%', startangle=90,
                                         colors=colors, textprops={'fontsize': 10})
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(11)
    ax1.set_title('Traffic Distribution Across Campus Zones',
                  fontsize=14, fontweight='bold', pad=20)

    # Bar chart
    ax2 = axes[1]
    zone_names = [CAMPUS_ZONES[zid]['name_en'] for zid in zone_totals.keys()]
    bars = ax2.bar(zone_names, zone_totals.values(), color=colors, edgecolor='black', linewidth=1.5)
    ax2.set_xlabel('Campus Zone', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Total Connections', fontsize=12, fontweight='bold')
    ax2.set_title('Total Traffic by Zone (7-Day Period)',
                  fontsize=14, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.xticks(rotation=15, ha='right')
    plt.tight_layout()
    plt.savefig('zones_traffic_share.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: zones_traffic_share.png")
    plt.close()

def plot_individual_zone_patterns(zone_id, data, zone_info):
    """Create detailed analysis for individual zone"""
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    zone_df = data['df']

    # 1. Hourly pattern with weekday/weekend
    ax1 = fig.add_subplot(gs[0, :])
    hours = range(24)
    ax1.plot(hours, data['weekday'], marker='o', linewidth=2.5, markersize=6,
            label='Weekday', color='#A23B72')
    ax1.plot(hours, data['weekend'], marker='s', linewidth=2.5, markersize=6,
            label='Weekend', color='#F18F01')
    ax1.fill_between(hours, data['weekday'], alpha=0.2, color='#A23B72')
    ax1.fill_between(hours, data['weekend'], alpha=0.2, color='#F18F01')
    ax1.set_xlabel('Hour of Day', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Connections', fontsize=11, fontweight='bold')
    ax1.set_title(f'{zone_info["name"]} - Weekday vs Weekend Pattern',
                 fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xticks(hours)
    ax1.legend(loc='best', fontsize=10)

    # 2. Base station heatmap
    ax2 = fig.add_subplot(gs[1, :])
    heatmap_data = zone_df.pivot_table(
        index='base_station_id',
        columns='hour',
        values='user_id',
        aggfunc='count',
        fill_value=0
    )
    heatmap_data = heatmap_data.reindex(zone_info['stations'], fill_value=0)
    sns.heatmap(heatmap_data, annot=True, fmt='g', cmap='YlOrRd',
               cbar_kws={'label': 'Connections'}, ax=ax2)
    ax2.set_xlabel('Hour of Day', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Base Station', fontsize=11, fontweight='bold')
    ax2.set_title('Base Station Traffic Heatmap (Hourly)', fontsize=13, fontweight='bold')

    # 3. Base station load distribution
    ax3 = fig.add_subplot(gs[2, 0])
    bs_colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(data['bs_traffic'])))
    bars = ax3.bar(range(len(data['bs_traffic'])), data['bs_traffic'].values, color=bs_colors)
    ax3.set_xticks(range(len(data['bs_traffic'])))
    ax3.set_xticklabels(data['bs_traffic'].index, rotation=45, ha='right', fontsize=9)
    ax3.set_xlabel('Base Station', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Connections', fontsize=11, fontweight='bold')
    ax3.set_title('Base Station Load Distribution', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y', linestyle='--')

    # 4. Persona distribution (if available)
    ax4 = fig.add_subplot(gs[2, 1])
    if data['persona'] is not None and len(data['persona']) > 0:
        persona_colors = plt.cm.Paired(np.linspace(0, 1, len(data['persona'])))
        wedges, texts, autotexts = ax4.pie(data['persona'].values,
                                            labels=data['persona'].index,
                                            autopct='%1.1f%%', startangle=45,
                                            colors=persona_colors,
                                            textprops={'fontsize': 9})
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(8)
        ax4.set_title('User Persona Distribution', fontsize=13, fontweight='bold')
    else:
        ax4.text(0.5, 0.5, 'No Persona Data', ha='center', va='center',
                fontsize=12, transform=ax4.transAxes)
        ax4.axis('off')

    plt.suptitle(f'{zone_info["name"]} - Comprehensive Traffic Analysis',
                fontsize=16, fontweight='bold', y=0.995)

    plt.savefig(f'zone_{zone_id}_analysis.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: zone_{zone_id}_analysis.png")
    plt.close()

def plot_base_station_coverage_map(zone_data, base_stations_df):
    """Plot all base stations colored by zone"""
    fig, ax = plt.subplots(figsize=(14, 10))

    # Plot all base stations with zone colors
    for zone_id, zone_info in CAMPUS_ZONES.items():
        zone_stations = base_stations_df[
            base_stations_df['base_station_id'].isin(zone_info['stations'])
        ]

        ax.scatter(zone_stations['longitude'], zone_stations['latitude'],
                  s=200, c=zone_info['color'], label=zone_info['name'],
                  alpha=0.7, edgecolors='black', linewidths=2)

        # Add labels
        for _, bs in zone_stations.iterrows():
            ax.annotate(bs['base_station_id'],
                       (bs['longitude'], bs['latitude']),
                       fontsize=8, ha='center', va='center',
                       fontweight='bold', color='white')

    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
    ax.set_title('Campus Base Station Distribution by Zone',
                fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='best', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig('zones_base_station_map.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: zones_base_station_map.png")
    plt.close()

def generate_comprehensive_report(zone_data):
    """Generate comprehensive statistics report for all zones"""
    report = []
    report.append("=" * 90)
    report.append("CAMPUS ZONES COMPREHENSIVE TRAFFIC ANALYSIS REPORT")
    report.append("=" * 90)
    report.append("")

    # Overall summary
    total_connections = sum(len(data['df']) for data in zone_data.values())
    report.append("EXECUTIVE SUMMARY")
    report.append("-" * 90)
    report.append(f"Total Campus Connections: {total_connections:,}")
    report.append(f"Number of Zones: {len(CAMPUS_ZONES)}")
    report.append("")

    # Zone-by-zone analysis
    for zone_id, data in zone_data.items():
        zone_info = CAMPUS_ZONES[zone_id]
        zone_df = data['df']

        report.append("=" * 90)
        report.append(f"{zone_info['name']} ({zone_info['name_en']})")
        report.append("=" * 90)
        report.append(f"Description: {zone_info['description']}")
        report.append("")

        # 1. Overall Statistics
        report.append("1. OVERALL STATISTICS")
        report.append("-" * 90)
        report.append(f"   Total Connections: {len(zone_df):,} ({len(zone_df)/total_connections*100:.2f}% of campus)")
        report.append(f"   Unique Users: {zone_df['user_id'].nunique():,}")
        report.append(f"   Base Stations: {len(zone_info['stations'])} ({', '.join(zone_info['stations'])})")
        report.append(f"   Avg Connections per Station: {len(zone_df)/len(zone_info['stations']):.1f}")
        report.append("")

        # 2. Peak Hours
        report.append("2. PEAK HOURS ANALYSIS")
        report.append("-" * 90)
        report.append("   Top 5 Peak Hours:")
        for hour, count in data['peak_hours'].items():
            report.append(f"      {hour:02d}:00 - {count:,} connections")
        report.append("")
        report.append("   Bottom 5 Off-Peak Hours:")
        for hour, count in data['off_peak_hours'].items():
            report.append(f"      {hour:02d}:00 - {count:,} connections")
        report.append("")

        # 3. Base Station Load
        report.append("3. BASE STATION LOAD DISTRIBUTION")
        report.append("-" * 90)
        for bs, count in data['bs_traffic'].items():
            percentage = (count / len(zone_df)) * 100
            report.append(f"   {bs}: {count:,} ({percentage:.2f}%)")
        if len(data['bs_traffic']) > 0:
            load_balance = data['bs_traffic'].max() / data['bs_traffic'].min()
            report.append(f"   Load Balance Ratio: {load_balance:.2f}x (max/min)")
        report.append("")

        # 4. Weekday vs Weekend
        zone_df['is_weekend'] = zone_df['timestamp'].dt.dayofweek >= 5
        weekday_count = len(zone_df[~zone_df['is_weekend']])
        weekend_count = len(zone_df[zone_df['is_weekend']])

        report.append("4. WEEKDAY vs WEEKEND PATTERNS")
        report.append("-" * 90)
        report.append(f"   Weekday Traffic: {weekday_count:,} connections")
        report.append(f"   Weekend Traffic: {weekend_count:,} connections")
        if weekday_count > 0:
            report.append(f"   Weekend/Weekday Ratio: {weekend_count/weekday_count:.2f}x")
        report.append("")

        # 5. Persona Distribution
        if data['persona'] is not None and len(data['persona']) > 0:
            report.append("5. USER PERSONA DISTRIBUTION")
            report.append("-" * 90)
            for persona, count in data['persona'].items():
                percentage = (count / len(zone_df)) * 100
                report.append(f"   {persona}: {count:,} ({percentage:.2f}%)")
            report.append("")

            # Top persona
            top_persona = data['persona'].index[0]
            top_pct = (data['persona'].iloc[0] / len(zone_df)) * 100
            report.append(f"   Dominant User Type: {top_persona} ({top_pct:.1f}%)")
            report.append("")

        # 6. Zone-specific insights
        report.append("6. ZONE-SPECIFIC INSIGHTS")
        report.append("-" * 90)

        hourly_avg = data['hourly'].mean()
        hourly_peak = data['hourly'].max()
        peak_hour = data['hourly'].idxmax()

        report.append(f"   Average Hourly Traffic: {hourly_avg:.1f} connections")
        report.append(f"   Peak Hour: {peak_hour:02d}:00 with {hourly_peak:,} connections")
        report.append(f"   Peak/Average Ratio: {hourly_peak/hourly_avg:.2f}x")

        # Zone-specific characteristics
        if zone_id == 'north_commercial':
            lunch_traffic = zone_df[zone_df['hour'].isin([11, 12, 13])].shape[0]
            dinner_traffic = zone_df[zone_df['hour'].isin([17, 18, 19, 20])].shape[0]
            report.append(f"   Lunch Hours (11-13): {lunch_traffic:,} ({lunch_traffic/len(zone_df)*100:.1f}%)")
            report.append(f"   Dinner Hours (17-20): {dinner_traffic:,} ({dinner_traffic/len(zone_df)*100:.1f}%)")
        elif zone_id == 'east_transport':
            morning_rush = zone_df[zone_df['hour'].isin([7, 8])].shape[0]
            evening_rush = zone_df[zone_df['hour'].isin([17, 18])].shape[0]
            report.append(f"   Morning Rush (7-8): {morning_rush:,} ({morning_rush/len(zone_df)*100:.1f}%)")
            report.append(f"   Evening Rush (17-18): {evening_rush:,} ({evening_rush/len(zone_df)*100:.1f}%)")
        elif zone_id == 'teaching_core':
            class_hours = zone_df[zone_df['hour'].isin([8, 9, 10, 14, 15, 16])].shape[0]
            report.append(f"   Class Hours (8-10, 14-16): {class_hours:,} ({class_hours/len(zone_df)*100:.1f}%)")
        elif zone_id == 'south_residential':
            night_hours = zone_df[zone_df['hour'].isin([22, 23, 0, 1, 2, 3, 4, 5, 6])].shape[0]
            report.append(f"   Night/Early Morning (22-6): {night_hours:,} ({night_hours/len(zone_df)*100:.1f}%)")

        report.append("")
        report.append("")

    # Cross-zone comparison
    report.append("=" * 90)
    report.append("CROSS-ZONE COMPARISON")
    report.append("=" * 90)
    report.append("")

    # Traffic volume ranking
    zone_volumes = {zid: len(data['df']) for zid, data in zone_data.items()}
    sorted_zones = sorted(zone_volumes.items(), key=lambda x: x[1], reverse=True)

    report.append("Traffic Volume Ranking:")
    report.append("-" * 90)
    for i, (zone_id, volume) in enumerate(sorted_zones, 1):
        zone_info = CAMPUS_ZONES[zone_id]
        pct = (volume / total_connections) * 100
        report.append(f"   {i}. {zone_info['name']}: {volume:,} ({pct:.1f}%)")
    report.append("")

    # Peak hour comparison
    report.append("Peak Hour Comparison:")
    report.append("-" * 90)
    for zone_id in CAMPUS_ZONES.keys():
        zone_info = CAMPUS_ZONES[zone_id]
        peak_hour = zone_data[zone_id]['hourly'].idxmax()
        peak_count = zone_data[zone_id]['hourly'].max()
        report.append(f"   {zone_info['name']}: {peak_hour:02d}:00 ({peak_count:,} connections)")
    report.append("")

    report.append("=" * 90)

    # Save report
    report_text = "\n".join(report)
    with open('campus_zones_traffic_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)

    print("\n" + report_text)
    print("\nReport saved to: campus_zones_traffic_report.txt")

def main():
    """Main analysis workflow"""
    print("=" * 90)
    print("CAMPUS ZONES COMPREHENSIVE TRAFFIC ANALYSIS")
    print("=" * 90)
    print()

    # Load data
    base_stations, signaling_coarse, signaling_fine, user_activities = load_data()
    print()

    # Analyze all zones
    zone_data = analyze_all_zones(signaling_fine)
    print()

    # Generate visualizations
    print("Generating visualizations...")
    plot_zones_comparison_hourly(zone_data)
    plot_zones_traffic_share(zone_data)
    plot_base_station_coverage_map(zone_data, base_stations)

    # Individual zone analysis
    for zone_id, data in zone_data.items():
        zone_info = CAMPUS_ZONES[zone_id]
        plot_individual_zone_patterns(zone_id, data, zone_info)

    print()

    # Generate comprehensive report
    print("Generating comprehensive report...")
    generate_comprehensive_report(zone_data)

    print()
    print("=" * 90)
    print("ANALYSIS COMPLETE!")
    print("=" * 90)
    print()
    print("Generated Files:")
    print("  Comparison Charts:")
    print("    • zones_hourly_comparison.png - Hourly pattern across all zones")
    print("    • zones_traffic_share.png - Traffic distribution")
    print("    • zones_base_station_map.png - Geographic distribution")
    print()
    print("  Individual Zone Analysis:")
    for zone_id in CAMPUS_ZONES.keys():
        zone_name = CAMPUS_ZONES[zone_id]['name_en']
        print(f"    • zone_{zone_id}_analysis.png - {zone_name} detailed analysis")
    print()
    print("  Report:")
    print("    • campus_zones_traffic_report.txt - Comprehensive statistics")
    print()

if __name__ == '__main__':
    main()
