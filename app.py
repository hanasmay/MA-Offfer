import streamlit as st
import folium
from streamlit_folium import st_folium
import math

# --- 1. 马萨诸塞州 RMV 办公室数据库 (ZMA 代码) ---
MA_OFFICES = {
    "601": {"name": "Boston (Haymarket)", "lat": 42.3625, "lon": -71.0561, "addr": "136 Blackstone St"},
    "603": {"name": "Brockton", "lat": 42.0834, "lon": -71.0184, "addr": "490 Forest Ave"},
    "605": {"name": "Chicopee", "lat": 42.1490, "lon": -72.6079, "addr": "1011 Chicopee St"},
    "608": {"name": "Fall River", "lat": 41.7015, "lon": -71.1550, "addr": "179 President Ave"},
    "611": {"name": "Lawrence", "lat": 42.7070, "lon": -71.1631, "addr": "73 Winthrop Ave"},
    "613": {"name": "Leominster", "lat": 42.5251, "lon": -71.7598, "addr": "80 Erdman Way"},
    "615": {"name": "New Bedford", "lat": 41.6362, "lon": -70.9342, "addr": "53 North 6th St"},
    "620": {"name": "Quincy", "lat": 42.2529, "lon": -71.0023, "addr": "25 Newport Ave Ext"},
    "622": {"name": "Revere", "lat": 42.4084, "lon": -71.0120, "addr": "11 Everett St"},
    "625": {"name": "Springfield", "lat": 42.1015, "lon": -72.5898, "addr": "165 Liberty St"},
    "628": {"name": "Worcester", "lat": 42.2626, "lon": -71.8023, "addr": "611 Main St"},
    "640": {"name": "Danvers", "lat": 42.5651, "lon": -70.9259, "addr": "82 Woodbury St"},
    "645": {"name": "Lowell", "lat": 42.6334, "lon": -71.3162, "addr": "77 Fortune Blvd"},
    "652": {"name": "Plymouth", "lat": 41.9584, "lon": -70.6673, "addr": "40 Industrial Park Rd"},
    "660": {"name": "Taunton", "lat": 41.9001, "lon": -71.0898, "addr": "1 Washington St"},
    "670": {"name": "Watertown", "lat": 42.3709, "lon": -71.1828, "addr": "550 Arsenal St"},
    "688": {"name": "Wilmington", "lat": 42.5584, "lon": -71.1684, "addr": "355 Main St"}
}

# 距离计算函数
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- 2. 界面设计 ---
st.set_page_config(page_title="MA RMV Finder", layout="wide")
st.markdown("<h2 style='text-align: center;'>MA 签发办公室地图定位系统</h2>", unsafe_allow_html=True)

# 搜索输入
search_query = st.sidebar.text_input("📍 输入城市名称并按回车 (例如: Worcester, MA):", "")

# 默认地图中心 (波士顿)
view_lat, view_lon = 42.3601, -71.0589
found_location = None

# --- 3. 核心搜索与标记逻辑 ---
# 注意：在 Streamlit 环境中，我们通常需要调用地理编码 API。
# 这里我为您演示如何结合搜索结果进行标记。
if search_query:
    # 模拟地理编码：如果用户输入了包含办公室名称的城市
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="ma_rmv_finder")
    try:
        location = geolocator.geocode(search_query + ", Massachusetts, USA")
        if location:
            view_lat, view_lon = location.latitude, location.longitude
            found_location = [view_lat, view_lon]
            st.sidebar.success(f"已标记城市: {location.address}")
    except:
        st.sidebar.error("无法获取该城市坐标，请检查拼写。")

# 计算距离并排序
sorted_offices = []
for code, info in MA_OFFICES.items():
    dist = haversine(view_lat, view_lon, info["lat"], info["lon"])
    sorted_offices.append({**info, "code": code, "dist": dist})
sorted_offices.sort(key=lambda x: x["dist"])

# --- 4. 地图显示 ---
m = folium.Map(location=[view_lat, view_lon], zoom_start=10, tiles="cartodbpositron")

# 标记用户搜索的城市 (蓝色图钉)
if found_location:
    folium.Marker(
        location=found_location,
        popup="您搜索的位置",
        icon=folium.Icon(color="blue", icon="screenshot")
    ).add_to(m)

# 标记所有 RMV 办公室 (红色图钉)
for office in sorted_offices:
    folium.Marker(
        location=[office["lat"], office["lon"]],
        tooltip=f"代码: {office['code']} | {office['name']}",
        popup=f"地址: {office['addr']}<br>距离: {office['dist']:.2f} km",
        icon=folium.Icon(color="red", icon="home")
    ).add_to(m)

# 页面布局
col_m, col_t = st.columns([3, 1])
with col_m:
    st_folium(m, width=850, height=600, key="ma_map")

with col_t:
    st.subheader("📍 最近的办公室")
    for i in range(min(3, len(sorted_offices))):
        o = sorted_offices[i]
        st.info(f"**{o['name']}** (ZMA: `{o['code']}`)\n\n距离: {o['dist']:.2f} km\n\n地址: {o['addr']}")
