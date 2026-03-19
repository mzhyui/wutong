#!/usr/bin/env python3
import os
import requests
import csv
import random
from typing import List, Dict, Optional

# 从环境变量获取API密钥
API_KEY = os.getenv("AMAP_API_KEY")
if not API_KEY:
    raise ValueError("请设置环境变量 AMAP_API_KEY")

BASE_URL = "https://restapi.amap.com/v3/place/around"

# 商铺类型编码（可根据需要调整）
SHOP_TYPES = [
    "060000",  # 购物服务
    "050000",  # 餐饮服务
    "070000",  # 生活服务
    "080000",  # 体育休闲服务
    "090000",  # 医疗服务
]

def generate_shop_id(index: int) -> str:
    """生成商铺ID，格式为Cxx"""
    return f"C{index:02d}"

def generate_rent_range(area_sqm: int) -> str:
    """根据面积生成租金范围（模拟逻辑）"""
    base = area_sqm * 180  # 每平米约180元/月
    variation = random.randint(-200, 200) * area_sqm // 10
    low = base - variation
    high = base + variation
    return f"{low}-{high}"

def fetch_pois(location: str, radius: int = 2000, city: Optional[str] = None) -> List[Dict]:
    """使用周边搜索API获取POI数据"""
    params = {
        'key': API_KEY,
        'location': location,
        'radius': radius,
        'types': '|'.join(SHOP_TYPES),
        'offset': 50,  # 每页记录数（最大50）
        'page': 1,
        'extensions': 'all',  # 获取完整信息
        'sortrule': 'distance'
    }
    if city:
        params['city'] = city
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') != '1':
            print(f"API请求失败: {data.get('info')}")
            return []
        
        return data.get('pois', [])
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return []
    except ValueError as e:
        print(f"JSON解析错误: {e}")
        return []

def parse_poi_to_shop_data(poi: Dict, index: int) -> Dict:
    """解析POI数据为商铺格式"""
    shop_id = generate_shop_id(index)
    
    # 地址
    address = poi.get('address', '')
    if not address:
        address = poi.get('name', '') + poi.get('adname', '')
    
    # 经纬度
    location = poi.get('location', '')
    if location:
        longitude, latitude = location.split(',')
    else:
        # 模拟数据（如果API没有返回）
        latitude = round(32.045 + random.uniform(-0.005, 0.005), 4)
        longitude = round(118.785 + random.uniform(-0.005, 0.005), 4)
    
    # 面积（模拟，实际API不提供）
    area_options = [30, 35, 40, 45, 50, 55, 60, 65]
    area_sqm = random.choice(area_options)
    
    # 租金范围（模拟）
    rent_range = generate_rent_range(area_sqm)
    
    return {
        'shop_id': shop_id,
        'address': address,
        'latitude': latitude,
        'longitude': longitude,
        'area_sqm': area_sqm,
        'rent_range': rent_range
    }

def get_shops_by_campus(campus_name: str, city: str) -> List[Dict]:
    """根据大学名称获取周边商铺数据"""
    # 首先通过文本搜索获取大学坐标
    search_url = "https://restapi.amap.com/v3/place/text"
    search_params = {
        'key': API_KEY,
        'keywords': campus_name,
        'city': city,
        'offset': 1,
        'page': 1,
        'extensions': 'base'
    }
    
    try:
        search_resp = requests.get(search_url, params=search_params, timeout=5)
        search_data = search_resp.json()
        
        if search_data.get('status') != '1' or not search_data.get('pois'):
            print(f"找不到{campus_name}的位置，使用默认坐标")
            # 默认坐标（示例：南京大学附近）
            default_location = "118.7920,32.0485"
            pois = fetch_pois(default_location, city=city)
        else:
            # 使用第一个POI的坐标
            university = search_data['pois'][0]
            location = university.get('location')
            if not location:
                raise ValueError("大学坐标缺失")
            pois = fetch_pois(location, city=city)
    except Exception as e:
        print(f"获取大学坐标失败: {e}")
        # 备用坐标
        pois = fetch_pois("118.7920,32.0485", city=city)
    
    shops = []
    for i, poi in enumerate(pois[:20], 1):  # 取最多20个
        shop_data = parse_poi_to_shop_data(poi, i)
        shops.append(shop_data)
    
    return shops

def save_to_csv(shops: List[Dict], filename: str = "shops_data.csv"):
    """保存数据到CSV文件"""
    fieldnames = ['shop_id', 'address', 'latitude', 'longitude', 'area_sqm', 'rent_range']
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(shops)
    
    print(f"数据已保存到 {filename}")

def main():
    # 示例：获取南京大学周边的商铺数据
    campus = "南京大学"
    city = "南京"
    
    print(f"正在获取{campus}周边的商铺数据...")
    shops = get_shops_by_campus(campus, city)
    
    if not shops:
        raise ValueError("未能获取到商铺数据")
        # # 如果API没有返回足够数据，生成模拟数据
        # print("API数据不足，生成模拟数据")
        # shops = []
        # base_lat = 32.0485
        # base_lng = 118.7920
        
        # for i in range(1, 21):
        #     # 模拟不同位置的商铺
        #     lat_offset = random.uniform(-0.005, 0.005)
        #     lng_offset = random.uniform(-0.005, 0.005)
            
        #     shop_data = {
        #         'shop_id': generate_shop_id(i),
        #         'address': f"模拟地址{i}号",
        #         'latitude': round(base_lat + lat_offset, 4),
        #         'longitude': round(base_lng + lng_offset, 4),
        #         'area_sqm': random.choice([30, 35, 40, 45, 50, 55, 60, 65]),
        #         'rent_range': generate_rent_range(shop_data['area_sqm'])
        #     }
        #     shops.append(shop_data)
    
    # 打印数据
    print("\n获取的商铺数据:")
    for shop in shops:
        print(f"{shop['shop_id']},{shop['address']},{shop['latitude']},{shop['longitude']},{shop['area_sqm']},{shop['rent_range']}")
    
    # 保存到CSV
    save_to_csv(shops)

if __name__ == "__main__":
    main()