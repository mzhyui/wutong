import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib
# set webagg
matplotlib.use('WebAgg')
# chinese font support
chinese_font = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
import numpy as np

# Read data from local CSV files
campus_poi_df = pd.read_csv('campus_poi.csv')
competitor_shops_df = pd.read_csv('competitor_shops.csv')
base_station_df = pd.read_csv('base_station.csv')

# Define colors for competitor shop categories
shop_category_colors = {
    '奶茶': '#FF69B4',     # Hot pink
    '咖啡': '#8B4513',     # Saddle brown
    '快餐': '#FF4500',     # Orange red
    '文创': '#9370DB',     # Medium purple
    '服务': '#32CD32',     # Lime green
    '便利店': '#4169E1',   # Royal blue
    '轻食': '#FFD700',     # Gold
    '烘焙': '#DEB887',     # Burlywood
    '零食': '#FF1493',     # Deep pink
    '百货': '#20B2AA'      # Light sea green
}

# Define colors for campus POI types
poi_type_colors = {
    '教学楼': '#87CEEB',   # Sky blue
    '宿舍': '#FFA07A',     # Light salmon
    '食堂': '#98FB98',     # Pale green
    '图书馆': '#DDA0DD',   # Plum
    '体育馆': '#F0E68C',   # Khaki
    '公共服务': '#B0C4DE', # Light steel blue
    '商业': '#FFB6C1'      # Light pink
}

# Define colors for base station types
base_station_colors = {
    '室内': '#FF6347',     # Tomato red
    '室外': '#4682B4'      # Steel blue
}

# Create figure and axis
plt.figure(figsize=(18, 12))
ax = plt.gca()

# Combine all data to determine bounds
all_lats = pd.concat([campus_poi_df['latitude'], competitor_shops_df['latitude'], base_station_df['latitude']])
all_lons = pd.concat([campus_poi_df['longitude'], competitor_shops_df['longitude'], base_station_df['longitude']])

# Set up the grid
lat_min, lat_max = all_lats.min(), all_lats.max()
lon_min, lon_max = all_lons.min(), all_lons.max()

# Add some padding to the bounds
lat_padding = (lat_max - lat_min) * 0.05
lon_padding = (lon_max - lon_min) * 0.05

lat_min -= lat_padding
lat_max += lat_padding
lon_min -= lon_padding
lon_max += lon_padding

# Create grid lines
n_grid = 10  # 10x10 grid
lat_grid = np.linspace(lat_min, lat_max, n_grid + 1)
lon_grid = np.linspace(lon_min, lon_max, n_grid + 1)

# Draw grid lines
for lat in lat_grid:
    plt.axhline(y=lat, color='lightgray', linestyle='-', alpha=0.3, linewidth=0.5)
for lon in lon_grid:
    plt.axvline(x=lon, color='lightgray', linestyle='-', alpha=0.3, linewidth=0.5)

# Plot campus POIs by type
for poi_type in poi_type_colors.keys():
    poi_data = campus_poi_df[campus_poi_df['poi_type'] == poi_type]
    if not poi_data.empty:
        plt.scatter(poi_data['longitude'], poi_data['latitude'],
                   c=poi_type_colors[poi_type], label=f'校园-{poi_type}',
                   s=200, alpha=0.6, edgecolors='black', linewidth=1.5, marker='s')

# Plot competitor shops by category
for category in shop_category_colors.keys():
    category_data = competitor_shops_df[competitor_shops_df['category'] == category]
    if not category_data.empty:
        plt.scatter(category_data['longitude'], category_data['latitude'],
                   c=shop_category_colors[category], label=f'竞品-{category}',
                   s=100, alpha=0.8, edgecolors='black', linewidth=0.5, marker='o')

# Plot base stations by coverage type
for coverage_type in base_station_colors.keys():
    station_data = base_station_df[base_station_df['coverage_type'] == coverage_type]
    if not station_data.empty:
        plt.scatter(station_data['longitude'], station_data['latitude'],
                   c=base_station_colors[coverage_type], label=f'基站-{coverage_type}',
                   s=150, alpha=0.7, edgecolors='black', linewidth=1, marker='^')

# Add POI names as annotations
for idx, row in campus_poi_df.iterrows():
    plt.annotate(row['poi_name'],
                (row['longitude'], row['latitude']),
                xytext=(5, 5), textcoords='offset points',
                fontsize=7, alpha=0.8, fontproperties=chinese_font,
                bbox=dict(boxstyle='round,pad=0.3', fc='lightblue', alpha=0.7, edgecolor='navy'))

# Add shop names as annotations
for idx, row in competitor_shops_df.iterrows():
    plt.annotate(row['shop_name'],
                (row['longitude'], row['latitude']),
                xytext=(5, 5), textcoords='offset points',
                fontsize=7, alpha=0.7, fontproperties=chinese_font,
                bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.7))

# Add base station IDs as annotations
for idx, row in base_station_df.iterrows():
    plt.annotate(row['base_station_id'],
                (row['longitude'], row['latitude']),
                xytext=(5, -10), textcoords='offset points',
                fontsize=6, alpha=0.8, color='darkblue',
                bbox=dict(boxstyle='round,pad=0.2', fc='lightyellow', alpha=0.8, edgecolor='blue'))

# Customize the plot
plt.xlabel('Longitude (经度)', fontsize=14, fontproperties=chinese_font)
plt.ylabel('Latitude (纬度)', fontsize=14, fontproperties=chinese_font)
plt.title('Campus Environment, Competitor & Base Station Analysis Map\n校园环境、竞品与基站分析地图', fontsize=18, fontweight='bold', fontproperties=chinese_font, pad=20)

# Add legend with better formatting
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9, ncol=2,
          prop=chinese_font, framealpha=0.9, edgecolor='gray')

# Set axis limits
plt.xlim(lon_min, lon_max)
plt.ylim(lat_min, lat_max)

# Make the plot look more like a map
plt.grid(True, alpha=0.3)
plt.gca().set_aspect('equal', adjustable='box')

# Adjust layout to prevent legend cutoff
plt.tight_layout()

# Show the plot
plt.show()

# Print summary statistics
print("\n" + "="*60)
print("Campus Environment, Competitor & Base Station Analysis Summary")
print("校园环境、竞品与基站分析总结")
print("="*60)

print(f"\n【Campus POIs 校园设施】")
print(f"Total POIs: {len(campus_poi_df)}")
print(f"POI Types: {len(campus_poi_df['poi_type'].unique())}")
print("\nPOIs by type:")
for poi_type, count in campus_poi_df['poi_type'].value_counts().items():
    print(f"  {poi_type}: {count}")

print(f"\n【Competitor Shops 竞品商店】")
print(f"Total shops: {len(competitor_shops_df)}")
print(f"Shop categories: {len(competitor_shops_df['category'].unique())}")
print("\nShops by category:")
for category, count in competitor_shops_df['category'].value_counts().items():
    print(f"  {category}: {count}")

print(f"\n【Base Stations 基站】")
print(f"Total base stations: {len(base_station_df)}")
print(f"Coverage types: {len(base_station_df['coverage_type'].unique())}")
print("\nBase stations by coverage type:")
for coverage_type, count in base_station_df['coverage_type'].value_counts().items():
    print(f"  {coverage_type}: {count}")

print(f"\n【Geographic Range 地理范围】")
print(f"Latitude range: {all_lats.min():.4f} to {all_lats.max():.4f}")
print(f"Longitude range: {all_lons.min():.4f} to {all_lons.max():.4f}")
print(f"Area coverage: ~{((all_lats.max()-all_lats.min())*111):.2f} km × {((all_lons.max()-all_lons.min())*111*np.cos(np.radians(all_lats.mean()))):.2f} km")

print("="*60)