import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib
import numpy as np
from datetime import datetime

# Set webagg
matplotlib.use('WebAgg')

# Chinese font support
chinese_font = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')

# Read data from local CSV files
user_signaling_df = pd.read_csv('user_signaling_generated.csv')
base_station_df = pd.read_csv('base_station.csv')

# Convert timestamp to datetime
user_signaling_df['timestamp'] = pd.to_datetime(user_signaling_df['timestamp'])
user_signaling_df['date'] = user_signaling_df['timestamp'].dt.date
user_signaling_df['hour'] = user_signaling_df['timestamp'].dt.hour

# Calculate traffic metrics for each base station
bs_traffic = user_signaling_df.groupby('base_station_id').size().reset_index(name='total_connections')

# Merge with base station location data
bs_traffic_merged = bs_traffic.merge(base_station_df, on='base_station_id')

# Calculate hourly traffic patterns
hourly_traffic = user_signaling_df.groupby(['base_station_id', 'hour']).size().reset_index(name='connections')

# Calculate daily traffic patterns
daily_traffic = user_signaling_df.groupby(['base_station_id', 'date']).size().reset_index(name='connections')

# Create a comprehensive visualization with multiple subplots
fig = plt.figure(figsize=(20, 14))

# ===== Subplot 1: Geographic distribution of base station traffic =====
ax1 = plt.subplot(2, 3, 1)

# Separate indoor and outdoor stations
indoor_stations = bs_traffic_merged[bs_traffic_merged['coverage_type'] == '室内']
outdoor_stations = bs_traffic_merged[bs_traffic_merged['coverage_type'] == '室外']

# Plot outdoor stations
scatter1 = ax1.scatter(outdoor_stations['longitude'], outdoor_stations['latitude'],
                       s=outdoor_stations['total_connections'] * 20,
                       c='#4682B4', alpha=0.6, edgecolors='black', linewidth=1.5,
                       marker='^', label='室外基站')

# Plot indoor stations
scatter2 = ax1.scatter(indoor_stations['longitude'], indoor_stations['latitude'],
                       s=indoor_stations['total_connections'] * 20,
                       c='#FF6347', alpha=0.6, edgecolors='black', linewidth=1.5,
                       marker='o', label='室内基站')

# Add base station IDs and traffic count annotations
for idx, row in bs_traffic_merged.iterrows():
    ax1.annotate(f"{row['base_station_id']}\n({row['total_connections']})",
                (row['longitude'], row['latitude']),
                xytext=(0, 8), textcoords='offset points',
                fontsize=6, alpha=0.8, ha='center',
                bbox=dict(boxstyle='round,pad=0.3', fc='lightyellow', alpha=0.7, edgecolor='orange'))

ax1.set_xlabel('经度 (Longitude)', fontsize=10, fontproperties=chinese_font)
ax1.set_ylabel('纬度 (Latitude)', fontsize=10, fontproperties=chinese_font)
ax1.set_title('基站流量地理分布图\nBase Station Traffic Geographic Distribution',
              fontsize=12, fontweight='bold', fontproperties=chinese_font)
ax1.legend(prop=chinese_font, fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.set_aspect('equal', adjustable='box')

# ===== Subplot 2: Top 15 busiest base stations =====
ax2 = plt.subplot(2, 3, 2)

top_15_stations = bs_traffic_merged.nlargest(15, 'total_connections')
colors = ['#FF6347' if ct == '室内' else '#4682B4' for ct in top_15_stations['coverage_type']]

bars = ax2.barh(range(len(top_15_stations)), top_15_stations['total_connections'], color=colors, alpha=0.7, edgecolor='black')
ax2.set_yticks(range(len(top_15_stations)))
ax2.set_yticklabels([f"{bs} ({ct})" for bs, ct in zip(top_15_stations['base_station_id'], top_15_stations['coverage_type'])],
                     fontproperties=chinese_font, fontsize=8)
ax2.set_xlabel('连接次数 (Total Connections)', fontsize=10, fontproperties=chinese_font)
ax2.set_title('前15名最繁忙基站\nTop 15 Busiest Base Stations',
              fontsize=12, fontweight='bold', fontproperties=chinese_font)
ax2.grid(axis='x', alpha=0.3)

# Add value labels on bars
for i, (bar, val) in enumerate(zip(bars, top_15_stations['total_connections'])):
    ax2.text(val, i, f' {val}', va='center', fontsize=8)

# ===== Subplot 3: Indoor vs Outdoor traffic comparison =====
ax3 = plt.subplot(2, 3, 3)

coverage_stats = bs_traffic_merged.groupby('coverage_type').agg({
    'total_connections': ['sum', 'mean', 'count']
}).round(2)

coverage_types = ['室内', '室外']
total_connections = [bs_traffic_merged[bs_traffic_merged['coverage_type'] == ct]['total_connections'].sum()
                     for ct in coverage_types]

# Create pie chart
colors_pie = ['#FF6347', '#4682B4']
wedges, texts, autotexts = ax3.pie(total_connections, labels=coverage_types, autopct='%1.1f%%',
                                     colors=colors_pie, startangle=90, textprops={'fontproperties': chinese_font, 'fontsize': 10})

# Make percentage text bold
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(11)

ax3.set_title('室内外基站流量占比\nIndoor vs Outdoor Traffic Share',
              fontsize=12, fontweight='bold', fontproperties=chinese_font)

# Add legend with actual numbers
legend_labels = [f'{ct}: {conn} 次' for ct, conn in zip(coverage_types, total_connections)]
ax3.legend(legend_labels, loc='upper left', prop=chinese_font, fontsize=9)

# ===== Subplot 4: Hourly traffic pattern =====
ax4 = plt.subplot(2, 3, 4)

# Get top 10 stations for hourly analysis
top_10_stations = bs_traffic_merged.nlargest(10, 'total_connections')['base_station_id'].tolist()
hourly_traffic_top10 = hourly_traffic[hourly_traffic['base_station_id'].isin(top_10_stations)]

# Pivot for easier plotting
hourly_pivot = hourly_traffic_top10.pivot(index='hour', columns='base_station_id', values='connections').fillna(0)

# Plot with different colors
for i, station in enumerate(hourly_pivot.columns):
    ax4.plot(hourly_pivot.index, hourly_pivot[station], marker='o', linewidth=2,
             label=station, alpha=0.7)

ax4.set_xlabel('小时 (Hour of Day)', fontsize=10, fontproperties=chinese_font)
ax4.set_ylabel('连接次数 (Connections)', fontsize=10, fontproperties=chinese_font)
ax4.set_title('前10大基站每小时流量模式\nHourly Traffic Pattern (Top 10 Stations)',
              fontsize=12, fontweight='bold', fontproperties=chinese_font)
ax4.legend(ncol=2, fontsize=7, loc='upper left')
ax4.grid(True, alpha=0.3)
ax4.set_xticks(range(0, 24, 2))

# ===== Subplot 5: Daily traffic trend =====
ax5 = plt.subplot(2, 3, 5)

daily_total = user_signaling_df.groupby('date').size().reset_index(name='total_connections')
daily_total['date'] = pd.to_datetime(daily_total['date'])

ax5.plot(daily_total['date'], daily_total['total_connections'], marker='o', linewidth=2.5,
         color='#2E8B57', markersize=8, alpha=0.7)
ax5.fill_between(daily_total['date'], daily_total['total_connections'], alpha=0.3, color='#90EE90')

ax5.set_xlabel('日期 (Date)', fontsize=10, fontproperties=chinese_font)
ax5.set_ylabel('总连接次数 (Total Connections)', fontsize=10, fontproperties=chinese_font)
ax5.set_title('每日总流量趋势\nDaily Total Traffic Trend',
              fontsize=12, fontweight='bold', fontproperties=chinese_font)
ax5.grid(True, alpha=0.3)
ax5.tick_params(axis='x', rotation=45)

# Add value labels
for x, y in zip(daily_total['date'], daily_total['total_connections']):
    ax5.text(x, y, f'{y}', ha='center', va='bottom', fontsize=8)

# ===== Subplot 6: Traffic distribution statistics =====
ax6 = plt.subplot(2, 3, 6)

# Calculate statistics
traffic_stats = bs_traffic_merged['total_connections'].describe()

# Create box plot and histogram combined
ax6_twin = ax6.twinx()

# Histogram
n, bins, patches = ax6.hist(bs_traffic_merged['total_connections'], bins=15,
                             color='#87CEEB', alpha=0.7, edgecolor='black')

# Box plot on twin axis
bp = ax6_twin.boxplot([bs_traffic_merged['total_connections']],
                       positions=[max(n) * 0.7], widths=[max(n) * 0.3],
                       vert=False, patch_artist=True)
bp['boxes'][0].set_facecolor('#FFB6C1')
bp['boxes'][0].set_alpha(0.7)

ax6.set_xlabel('连接次数 (Connections)', fontsize=10, fontproperties=chinese_font)
ax6.set_ylabel('基站数量 (Number of Stations)', fontsize=10, fontproperties=chinese_font)
ax6.set_title('基站流量分布统计\nTraffic Distribution Statistics',
              fontsize=12, fontweight='bold', fontproperties=chinese_font)
ax6_twin.set_ylabel('箱线图 (Box Plot)', fontsize=10, fontproperties=chinese_font)
ax6.grid(True, alpha=0.3, axis='x')

# Add statistics text
stats_text = f'均值: {traffic_stats["mean"]:.1f}\n中位数: {traffic_stats["50%"]:.1f}\n最大值: {traffic_stats["max"]:.0f}\n最小值: {traffic_stats["min"]:.0f}'
ax6.text(0.65, 0.95, stats_text, transform=ax6.transAxes, fontsize=9,
         verticalalignment='top', fontproperties=chinese_font,
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Main title
fig.suptitle('基站流量综合分析报告\nBase Station Traffic Comprehensive Analysis Report',
             fontsize=16, fontweight='bold', fontproperties=chinese_font, y=0.995)

plt.tight_layout(rect=[0, 0, 1, 0.99])
plt.show()

# ===== Print comprehensive text analysis =====
print("\n" + "="*80)
print("基站流量综合分析报告")
print("BASE STATION TRAFFIC COMPREHENSIVE ANALYSIS REPORT")
print("="*80)

print(f"\n【总体概况 Overall Summary】")
print(f"分析时间范围: {user_signaling_df['timestamp'].min()} 至 {user_signaling_df['timestamp'].max()}")
print(f"总用户数: {user_signaling_df['user_id'].nunique()}")
print(f"总基站数: {len(base_station_df)}")
print(f"总连接记录数: {len(user_signaling_df)}")
print(f"平均每个基站连接次数: {bs_traffic['total_connections'].mean():.2f}")
print(f"平均每个用户连接次数: {len(user_signaling_df) / user_signaling_df['user_id'].nunique():.2f}")

print(f"\n【基站类型统计 Coverage Type Statistics】")
for coverage_type in ['室内', '室外']:
    stations = bs_traffic_merged[bs_traffic_merged['coverage_type'] == coverage_type]
    total_conn = stations['total_connections'].sum()
    avg_conn = stations['total_connections'].mean()
    count = len(stations)
    print(f"\n{coverage_type}基站:")
    print(f"  数量: {count} 个 ({count/len(base_station_df)*100:.1f}%)")
    print(f"  总连接数: {total_conn} 次 ({total_conn/len(user_signaling_df)*100:.1f}%)")
    print(f"  平均连接数: {avg_conn:.2f} 次/基站")
    print(f"  最大连接数: {stations['total_connections'].max()} 次")
    print(f"  最小连接数: {stations['total_connections'].min()} 次")

print(f"\n【最繁忙基站 Top Busiest Stations】")
print("前10名:")
for idx, (bs_id, conn, lat, lon, cov_type) in enumerate(bs_traffic_merged.nlargest(10, 'total_connections')[
    ['base_station_id', 'total_connections', 'latitude', 'longitude', 'coverage_type']].values, 1):
    print(f"  {idx}. {bs_id} ({cov_type}): {conn} 次连接 - 位置: ({lat:.4f}, {lon:.4f})")

print(f"\n【最空闲基站 Least Busy Stations】")
print("后10名:")
for idx, (bs_id, conn, lat, lon, cov_type) in enumerate(bs_traffic_merged.nsmallest(10, 'total_connections')[
    ['base_station_id', 'total_connections', 'latitude', 'longitude', 'coverage_type']].values, 1):
    print(f"  {idx}. {bs_id} ({cov_type}): {conn} 次连接 - 位置: ({lat:.4f}, {lon:.4f})")

print(f"\n【时间模式分析 Temporal Pattern Analysis】")

# Hourly pattern
hourly_total = user_signaling_df.groupby('hour').size()
peak_hour = hourly_total.idxmax()
low_hour = hourly_total.idxmin()
print(f"\n每小时流量模式:")
print(f"  高峰时段: {peak_hour}:00 ({hourly_total[peak_hour]} 次连接)")
print(f"  低谷时段: {low_hour}:00 ({hourly_total[low_hour]} 次连接)")
print(f"  峰谷比: {hourly_total[peak_hour] / hourly_total[low_hour]:.2f}")

# Define time periods
morning_hours = range(6, 12)
afternoon_hours = range(12, 18)
evening_hours = range(18, 24)
night_hours = list(range(0, 6))

morning_traffic = user_signaling_df[user_signaling_df['hour'].isin(morning_hours)].shape[0]
afternoon_traffic = user_signaling_df[user_signaling_df['hour'].isin(afternoon_hours)].shape[0]
evening_traffic = user_signaling_df[user_signaling_df['hour'].isin(evening_hours)].shape[0]
night_traffic = user_signaling_df[user_signaling_df['hour'].isin(night_hours)].shape[0]

print(f"\n时段流量分布:")
print(f"  早晨 (06:00-12:00): {morning_traffic} 次 ({morning_traffic/len(user_signaling_df)*100:.1f}%)")
print(f"  下午 (12:00-18:00): {afternoon_traffic} 次 ({afternoon_traffic/len(user_signaling_df)*100:.1f}%)")
print(f"  傍晚 (18:00-24:00): {evening_traffic} 次 ({evening_traffic/len(user_signaling_df)*100:.1f}%)")
print(f"  夜间 (00:00-06:00): {night_traffic} 次 ({night_traffic/len(user_signaling_df)*100:.1f}%)")

# Daily pattern
daily_total_full = user_signaling_df.groupby('date').size()
peak_day = daily_total_full.idxmax()
low_day = daily_total_full.idxmin()
print(f"\n每日流量模式:")
print(f"  最繁忙日期: {peak_day} ({daily_total_full[peak_day]} 次连接)")
print(f"  最空闲日期: {low_day} ({daily_total_full[low_day]} 次连接)")
print(f"  平均每日连接数: {daily_total_full.mean():.2f}")
print(f"  每日连接数标准差: {daily_total_full.std():.2f}")

print(f"\n【用户行为分析 User Behavior Analysis】")
user_activity = user_signaling_df.groupby('user_id').agg({
    'base_station_id': ['count', 'nunique']
}).round(2)
user_activity.columns = ['total_connections', 'unique_stations']

print(f"用户连接统计:")
print(f"  平均每用户连接次数: {user_activity['total_connections'].mean():.2f}")
print(f"  平均每用户使用基站数: {user_activity['unique_stations'].mean():.2f}")
print(f"  最活跃用户连接次数: {user_activity['total_connections'].max():.0f}")
print(f"  最活跃用户使用基站数: {user_activity['unique_stations'].max():.0f}")

# Most active users
top_users = user_activity.nlargest(5, 'total_connections')
print(f"\n最活跃用户 Top 5:")
for idx, (user_id, row) in enumerate(top_users.iterrows(), 1):
    print(f"  {idx}. {user_id}: {row['total_connections']:.0f} 次连接, {row['unique_stations']:.0f} 个不同基站")

print(f"\n【地理分布分析 Geographic Distribution Analysis】")
lat_range = base_station_df['latitude'].max() - base_station_df['latitude'].min()
lon_range = base_station_df['longitude'].max() - base_station_df['longitude'].min()
area_km2 = (lat_range * 111) * (lon_range * 111 * np.cos(np.radians(base_station_df['latitude'].mean())))

print(f"覆盖范围:")
print(f"  纬度范围: {base_station_df['latitude'].min():.4f} ~ {base_station_df['latitude'].max():.4f}")
print(f"  经度范围: {base_station_df['longitude'].min():.4f} ~ {base_station_df['longitude'].max():.4f}")
print(f"  大约覆盖面积: {area_km2:.3f} 平方公里")
print(f"  基站密度: {len(base_station_df) / area_km2:.2f} 个/平方公里")

print(f"\n【关键发现与建议 Key Findings & Recommendations】")
print("\n1. 流量集中度分析:")
top_10_pct = bs_traffic_merged.nlargest(10, 'total_connections')['total_connections'].sum() / len(user_signaling_df) * 100
print(f"   - 前10个基站承载了 {top_10_pct:.1f}% 的流量")
if top_10_pct > 50:
    print(f"   - 建议: 流量过于集中，建议优化负载均衡或增加高流量区域的基站容量")

print("\n2. 室内外基站效能:")
indoor_avg = bs_traffic_merged[bs_traffic_merged['coverage_type'] == '室内']['total_connections'].mean()
outdoor_avg = bs_traffic_merged[bs_traffic_merged['coverage_type'] == '室外']['total_connections'].mean()
if indoor_avg > outdoor_avg:
    print(f"   - 室内基站平均流量 ({indoor_avg:.1f}) 高于室外基站 ({outdoor_avg:.1f})")
    print(f"   - 建议: 重点维护室内基站，确保其稳定性和容量")
else:
    print(f"   - 室外基站平均流量 ({outdoor_avg:.1f}) 高于室内基站 ({indoor_avg:.1f})")
    print(f"   - 建议: 加强室外基站的信号覆盖和容量")

print("\n3. 时段优化建议:")
if morning_traffic > afternoon_traffic and morning_traffic > evening_traffic:
    print(f"   - 早晨时段流量最高，建议在此时段增加网络资源分配")
elif afternoon_traffic > morning_traffic and afternoon_traffic > evening_traffic:
    print(f"   - 下午时段流量最高，建议在此时段增加网络资源分配")
else:
    print(f"   - 傍晚时段流量最高，建议在此时段增加网络资源分配")

# Find stations with zero or very low traffic
low_traffic_threshold = bs_traffic['total_connections'].quantile(0.1)
low_traffic_stations = bs_traffic[bs_traffic['total_connections'] <= low_traffic_threshold]
print(f"\n4. 低利用率基站:")
print(f"   - 发现 {len(low_traffic_stations)} 个基站流量低于阈值 ({low_traffic_threshold:.0f} 次)")
print(f"   - 建议: 分析这些基站的位置和配置，考虑重新部署或调整参数")

print("\n" + "="*80)
print("分析完成 Analysis Complete")
print("="*80)
