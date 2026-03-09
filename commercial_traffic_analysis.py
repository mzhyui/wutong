"""
Commercial Block Traffic Analysis and Visualization

Analyzes traffic patterns in the North Commercial Zone (北门商业区) based on:
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

# Set Chinese font for matplotlib
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# North Commercial Zone base stations from base_station_pos.txt
NORTH_COMMERCIAL_STATIONS = ['BS106', 'BS208', 'BS215', 'BS216', 'BS209', 'BS217']

def load_data():
    """Load all required data files"""
    print("Loading data files...")

    # Load base stations
    base_stations = pd.read_csv('base_station.csv')
    print(f"Loaded {len(base_stations)} base stations")

    # Load coarse-grained signaling (2025-12-01 to 2025-12-07)
    signaling_coarse = pd.read_csv('user_signaling_generated.csv')
    signaling_coarse['timestamp'] = pd.to_datetime(signaling_coarse['timestamp'])
    print(f"Loaded {len(signaling_coarse)} coarse-grained signaling records")

    # Load fine-grained signaling (2024-06-01 to 2024-06-07)
    signaling_fine = pd.read_csv('user_signaling_fine_grained.csv')
    signaling_fine['timestamp'] = pd.to_datetime(signaling_fine['timestamp'])
    print(f"Loaded {len(signaling_fine)} fine-grained signaling records")

    # Load user activities for persona information
    user_activities = pd.read_csv('user_activities.csv')
    print(f"Loaded {len(user_activities)} user profiles")

    return base_stations, signaling_coarse, signaling_fine, user_activities

def filter_commercial_traffic(signaling_df, station_list):
    """Filter signaling data for commercial zone base stations"""
    commercial_traffic = signaling_df[
        signaling_df['base_station_id'].isin(station_list)
    ].copy()
    return commercial_traffic

def analyze_hourly_patterns(fine_grained_df):
    """Analyze hourly traffic patterns in commercial zone"""
    commercial_fine = filter_commercial_traffic(fine_grained_df, NORTH_COMMERCIAL_STATIONS)

    # Extract hour from timestamp
    commercial_fine['hour'] = commercial_fine['timestamp'].dt.hour
    commercial_fine['date'] = commercial_fine['timestamp'].dt.date
    commercial_fine['day_of_week'] = commercial_fine['timestamp'].dt.dayofweek
    commercial_fine['is_weekend'] = commercial_fine['day_of_week'] >= 5

    # Hourly traffic count
    hourly_traffic = commercial_fine.groupby('hour').size()

    # Weekday vs Weekend patterns
    weekday_traffic = commercial_fine[~commercial_fine['is_weekend']].groupby('hour').size()
    weekend_traffic = commercial_fine[commercial_fine['is_weekend']].groupby('hour').size()

    return hourly_traffic, weekday_traffic, weekend_traffic, commercial_fine

def analyze_base_station_load(commercial_df):
    """Analyze traffic load distribution across commercial base stations"""
    bs_traffic = commercial_df.groupby('base_station_id').size().sort_values(ascending=False)
    return bs_traffic

def analyze_persona_distribution(commercial_df):
    """Analyze user persona distribution in commercial zone"""
    if 'persona_type' in commercial_df.columns:
        persona_traffic = commercial_df.groupby('persona_type').size().sort_values(ascending=False)
        return persona_traffic
    return None

def analyze_peak_hours(commercial_df):
    """Identify peak hours and their characteristics"""
    commercial_df['hour'] = commercial_df['timestamp'].dt.hour
    hourly_counts = commercial_df.groupby('hour').size()

    peak_hours = hourly_counts.nlargest(5)
    off_peak_hours = hourly_counts.nsmallest(5)

    return peak_hours, off_peak_hours

def plot_hourly_traffic_patterns(hourly_traffic, weekday_traffic, weekend_traffic):
    """Plot hourly traffic patterns"""
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # Overall hourly pattern
    ax1 = axes[0]
    hours = range(24)
    ax1.plot(hours, hourly_traffic, marker='o', linewidth=2, markersize=8, color='#2E86AB')
    ax1.fill_between(hours, hourly_traffic, alpha=0.3, color='#2E86AB')
    ax1.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Number of Connections', fontsize=12, fontweight='bold')
    ax1.set_title('North Commercial Zone - Hourly Traffic Pattern (7-Day Average)',
                  fontsize=14, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xticks(hours)

    # Mark meal times
    meal_times = [(11, 13, 'Lunch'), (17, 20, 'Dinner')]
    for start, end, label in meal_times:
        ax1.axvspan(start, end, alpha=0.2, color='orange', label=f'{label} Hours')
    ax1.legend(loc='upper left')

    # Weekday vs Weekend comparison
    ax2 = axes[1]
    ax2.plot(hours, weekday_traffic, marker='o', linewidth=2, markersize=6,
             label='Weekday', color='#A23B72')
    ax2.plot(hours, weekend_traffic, marker='s', linewidth=2, markersize=6,
             label='Weekend', color='#F18F01')
    ax2.fill_between(hours, weekday_traffic, alpha=0.2, color='#A23B72')
    ax2.fill_between(hours, weekend_traffic, alpha=0.2, color='#F18F01')
    ax2.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Number of Connections', fontsize=12, fontweight='bold')
    ax2.set_title('Weekday vs Weekend Traffic Comparison',
                  fontsize=14, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xticks(hours)
    ax2.legend(loc='upper left', fontsize=11)

    plt.tight_layout()
    plt.savefig('commercial_hourly_patterns.png', dpi=300, bbox_inches='tight')
    print("Saved: commercial_hourly_patterns.png")
    plt.close()

def plot_base_station_heatmap(commercial_df, base_stations_df):
    """Create heatmap of base station traffic by hour"""
    commercial_df['hour'] = commercial_df['timestamp'].dt.hour

    # Create pivot table: base_station x hour
    heatmap_data = commercial_df.pivot_table(
        index='base_station_id',
        columns='hour',
        values='user_id',
        aggfunc='count',
        fill_value=0
    )

    # Reindex to ensure all commercial stations are shown
    heatmap_data = heatmap_data.reindex(NORTH_COMMERCIAL_STATIONS, fill_value=0)

    # Create heatmap
    fig, ax = plt.subplots(figsize=(16, 6))
    sns.heatmap(heatmap_data, annot=True, fmt='g', cmap='YlOrRd',
                cbar_kws={'label': 'Connection Count'}, ax=ax)
    ax.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
    ax.set_ylabel('Base Station ID', fontsize=12, fontweight='bold')
    ax.set_title('North Commercial Zone - Base Station Traffic Heatmap (Hourly)',
                 fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig('commercial_bs_heatmap.png', dpi=300, bbox_inches='tight')
    print("Saved: commercial_bs_heatmap.png")
    plt.close()

def plot_base_station_load(bs_traffic, base_stations_df):
    """Plot base station load distribution"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Bar chart
    ax1 = axes[0]
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(bs_traffic)))
    bars = ax1.bar(range(len(bs_traffic)), bs_traffic.values, color=colors)
    ax1.set_xticks(range(len(bs_traffic)))
    ax1.set_xticklabels(bs_traffic.index, rotation=0, fontsize=11)
    ax1.set_xlabel('Base Station ID', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Total Connections', fontsize=12, fontweight='bold')
    ax1.set_title('Traffic Load Distribution Across Base Stations',
                  fontsize=14, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3, axis='y', linestyle='--')

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Pie chart
    ax2 = axes[1]
    colors_pie = plt.cm.Set3(np.linspace(0, 1, len(bs_traffic)))
    wedges, texts, autotexts = ax2.pie(bs_traffic.values, labels=bs_traffic.index,
                                         autopct='%1.1f%%', startangle=90,
                                         colors=colors_pie, textprops={'fontsize': 11})
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    ax2.set_title('Traffic Share by Base Station',
                  fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig('commercial_bs_load.png', dpi=300, bbox_inches='tight')
    print("Saved: commercial_bs_load.png")
    plt.close()

def plot_persona_distribution(persona_traffic):
    """Plot user persona distribution in commercial zone"""
    if persona_traffic is None or len(persona_traffic) == 0:
        print("No persona data available for plotting")
        return

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Horizontal bar chart
    ax1 = axes[0]
    colors = plt.cm.Spectral(np.linspace(0.2, 0.8, len(persona_traffic)))
    y_pos = range(len(persona_traffic))
    bars = ax1.barh(y_pos, persona_traffic.values, color=colors)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(persona_traffic.index, fontsize=11)
    ax1.set_xlabel('Number of Connections', fontsize=12, fontweight='bold')
    ax1.set_ylabel('User Persona', fontsize=12, fontweight='bold')
    ax1.set_title('User Persona Traffic Distribution in Commercial Zone',
                  fontsize=14, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3, axis='x', linestyle='--')

    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax1.text(width, bar.get_y() + bar.get_height()/2.,
                f'{int(width)} ({persona_traffic.values[i]/persona_traffic.sum()*100:.1f}%)',
                ha='left', va='center', fontsize=10, fontweight='bold')

    # Persona composition by hour (if possible)
    ax2 = axes[1]
    # For now, just show a different view
    colors_pie = plt.cm.Paired(np.linspace(0, 1, len(persona_traffic)))
    wedges, texts, autotexts = ax2.pie(persona_traffic.values, labels=persona_traffic.index,
                                         autopct='%1.1f%%', startangle=45,
                                         colors=colors_pie, textprops={'fontsize': 10})
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    ax2.set_title('Persona Share in Commercial Zone',
                  fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig('commercial_persona_distribution.png', dpi=300, bbox_inches='tight')
    print("Saved: commercial_persona_distribution.png")
    plt.close()

def plot_daily_trends(commercial_df):
    """Plot daily traffic trends"""
    commercial_df['date'] = commercial_df['timestamp'].dt.date
    daily_traffic = commercial_df.groupby('date').size()

    fig, ax = plt.subplots(figsize=(14, 6))
    dates = range(len(daily_traffic))
    ax.plot(dates, daily_traffic.values, marker='o', linewidth=2.5,
            markersize=10, color='#C73E1D')
    ax.fill_between(dates, daily_traffic.values, alpha=0.3, color='#C73E1D')

    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Connections', fontsize=12, fontweight='bold')
    ax.set_title('North Commercial Zone - Daily Traffic Trend',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(dates)
    ax.set_xticklabels([str(d) for d in daily_traffic.index], rotation=45, ha='right')
    ax.grid(True, alpha=0.3, linestyle='--')

    # Add value labels
    for i, v in enumerate(daily_traffic.values):
        ax.text(i, v, f'{int(v)}', ha='center', va='bottom',
                fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig('commercial_daily_trend.png', dpi=300, bbox_inches='tight')
    print("Saved: commercial_daily_trend.png")
    plt.close()

def generate_statistics_report(commercial_df, bs_traffic, persona_traffic, peak_hours, off_peak_hours):
    """Generate comprehensive statistics report"""
    report = []
    report.append("=" * 80)
    report.append("NORTH COMMERCIAL ZONE (北门商业区) - TRAFFIC ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")

    # Overall statistics
    report.append("1. OVERALL STATISTICS")
    report.append("-" * 80)
    report.append(f"   Total Connections: {len(commercial_df):,}")
    report.append(f"   Unique Users: {commercial_df['user_id'].nunique():,}")
    report.append(f"   Base Stations: {', '.join(NORTH_COMMERCIAL_STATIONS)}")
    report.append(f"   Time Period: {commercial_df['timestamp'].min()} to {commercial_df['timestamp'].max()}")
    report.append(f"   Duration: {(commercial_df['timestamp'].max() - commercial_df['timestamp'].min()).days + 1} days")
    report.append("")

    # Base station statistics
    report.append("2. BASE STATION LOAD DISTRIBUTION")
    report.append("-" * 80)
    for bs, count in bs_traffic.items():
        percentage = (count / len(commercial_df)) * 100
        report.append(f"   {bs}: {count:,} connections ({percentage:.2f}%)")
    report.append(f"   Average per station: {len(commercial_df) / len(bs_traffic):.1f} connections")
    report.append(f"   Load balance ratio: {bs_traffic.max() / bs_traffic.min():.2f}x (max/min)")
    report.append("")

    # Peak hours analysis
    report.append("3. PEAK HOURS ANALYSIS")
    report.append("-" * 80)
    report.append("   Top 5 Peak Hours:")
    for hour, count in peak_hours.items():
        report.append(f"      {hour:02d}:00 - {count:,} connections")
    report.append("")
    report.append("   Top 5 Off-Peak Hours:")
    for hour, count in off_peak_hours.items():
        report.append(f"      {hour:02d}:00 - {count:,} connections")
    report.append("")

    # Persona distribution
    if persona_traffic is not None:
        report.append("4. USER PERSONA DISTRIBUTION")
        report.append("-" * 80)
        for persona, count in persona_traffic.items():
            percentage = (count / len(commercial_df)) * 100
            report.append(f"   {persona}: {count:,} connections ({percentage:.2f}%)")
        report.append("")

    # Time-based patterns
    commercial_df['hour'] = commercial_df['timestamp'].dt.hour
    commercial_df['is_weekend'] = commercial_df['timestamp'].dt.dayofweek >= 5

    weekday_traffic = len(commercial_df[~commercial_df['is_weekend']])
    weekend_traffic = len(commercial_df[commercial_df['is_weekend']])

    report.append("5. WEEKDAY vs WEEKEND PATTERNS")
    report.append("-" * 80)
    report.append(f"   Weekday Traffic: {weekday_traffic:,} connections")
    report.append(f"   Weekend Traffic: {weekend_traffic:,} connections")
    report.append(f"   Weekend/Weekday Ratio: {weekend_traffic/weekday_traffic:.2f}x")
    report.append("")

    # Hourly statistics
    hourly_avg = commercial_df.groupby('hour').size().mean()
    hourly_max = commercial_df.groupby('hour').size().max()
    hourly_min = commercial_df.groupby('hour').size().min()

    report.append("6. HOURLY TRAFFIC STATISTICS")
    report.append("-" * 80)
    report.append(f"   Average per hour: {hourly_avg:.1f} connections")
    report.append(f"   Peak hour traffic: {hourly_max:,} connections")
    report.append(f"   Off-peak hour traffic: {hourly_min:,} connections")
    report.append(f"   Peak/Off-peak ratio: {hourly_max/hourly_min:.2f}x")
    report.append("")

    # Business insights
    report.append("7. BUSINESS INSIGHTS")
    report.append("-" * 80)

    # Identify meal time peaks
    lunch_hours = [11, 12, 13]
    dinner_hours = [17, 18, 19, 20]

    lunch_traffic = commercial_df[commercial_df['hour'].isin(lunch_hours)].shape[0]
    dinner_traffic = commercial_df[commercial_df['hour'].isin(dinner_hours)].shape[0]

    report.append(f"   Lunch Hours (11:00-13:00): {lunch_traffic:,} connections ({lunch_traffic/len(commercial_df)*100:.1f}%)")
    report.append(f"   Dinner Hours (17:00-20:00): {dinner_traffic:,} connections ({dinner_traffic/len(commercial_df)*100:.1f}%)")
    report.append("")

    if persona_traffic is not None and len(persona_traffic) > 0:
        top_persona = persona_traffic.index[0]
        top_persona_pct = (persona_traffic.iloc[0] / len(commercial_df)) * 100
        report.append(f"   Dominant User Type: {top_persona} ({top_persona_pct:.1f}%)")

    report.append("")
    report.append("=" * 80)

    # Save report
    report_text = "\n".join(report)
    with open('commercial_traffic_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)

    print("\n" + report_text)
    print("\nReport saved to: commercial_traffic_report.txt")

def main():
    """Main analysis workflow"""
    print("=" * 80)
    print("NORTH COMMERCIAL ZONE TRAFFIC ANALYSIS")
    print("=" * 80)
    print()

    # Load data
    base_stations, signaling_coarse, signaling_fine, user_activities = load_data()
    print()

    # Analyze fine-grained data (more detailed hourly patterns)
    print("Analyzing fine-grained signaling data...")
    hourly_traffic, weekday_traffic, weekend_traffic, commercial_fine = analyze_hourly_patterns(signaling_fine)

    # Base station load analysis
    bs_traffic = analyze_base_station_load(commercial_fine)

    # Persona distribution
    persona_traffic = analyze_persona_distribution(commercial_fine)

    # Peak hours
    peak_hours, off_peak_hours = analyze_peak_hours(commercial_fine)

    print()
    print("Generating visualizations...")

    # Create all plots
    plot_hourly_traffic_patterns(hourly_traffic, weekday_traffic, weekend_traffic)
    plot_base_station_heatmap(commercial_fine, base_stations)
    plot_base_station_load(bs_traffic, base_stations)
    if persona_traffic is not None:
        plot_persona_distribution(persona_traffic)
    plot_daily_trends(commercial_fine)

    print()
    print("Generating statistics report...")
    generate_statistics_report(commercial_fine, bs_traffic, persona_traffic,
                               peak_hours, off_peak_hours)

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    print()
    print("Generated files:")
    print("  1. commercial_hourly_patterns.png - Hourly traffic patterns")
    print("  2. commercial_bs_heatmap.png - Base station traffic heatmap")
    print("  3. commercial_bs_load.png - Base station load distribution")
    print("  4. commercial_persona_distribution.png - User persona analysis")
    print("  5. commercial_daily_trend.png - Daily traffic trends")
    print("  6. commercial_traffic_report.txt - Comprehensive statistics report")
    print()

if __name__ == '__main__':
    main()
