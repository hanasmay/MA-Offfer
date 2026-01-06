import streamlit as st
import folium
from streamlit_folium import st_folium
from difflib import get_close_matches
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

# --- 2. 距离计算辅助函数 ---
def haversine(lat1, lon1, lat2, lon2):
    # 计算地球两点间距离 (KM)
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- 3. Streamlit 界面设置 ---
st.set_page_config(page_title="MA RMV 办公室分布图", layout="wide")
st.markdown("<h2 style='text-align: center;'>马萨诸塞州 (MA) RMV 签发办公室智能匹配系统</h2>", unsafe_allow_html=True)

# 侧边栏搜索逻辑
with st.sidebar:
    st.header("🔍 查找最近的 RMV")
    search_city = st.text_input("输入您所在的城市 (例如: Boston):", "").strip().title()
    st.write("---")
    st.info("本系统将根据坐标自动匹配 ZMA 代码。")

# --- 4. 逻辑处理：搜索定位与距离排序 ---
target_lat, target_lon = 42.3601, -71.0589  # 默认中心点：Boston
if search_city:
    # 模拟城市坐标匹配 (实际应用可接入 API)
    # 简单示例：如果搜索 Boston，中心移向 Boston RMV
    city_matches = get_close_matches(search_city, [v["name"].split(' ')[0] for v in MA_OFFICES.values()], n=1, cutoff=0.4)
    if city_matches:
        for code, info in MA_OFFICES.items():
            if city_matches[0] in info["name"]:
                target_lat, target_lon = info["lat"], info["lon"]
                st.sidebar.success(f"已定位到: {info['name']}")
                break

# 计算所有办公室与目标点的距离并排序
recommendations = []
for code, info in MA_OFFICES.items():
    dist = haversine(target_lat, target_lon, info["lat"], info["lon"])
    recommendations.append({"code": code, "name": info["name"], "dist": dist, "addr": info["addr"], "lat": info["lat"], "lon": info["lon"]})

recommendations.sort(key=lambda x: x["dist"])

# --- 5. 地图渲染 (带有鼠标触碰显示功能) ---
m = folium.Map(location=[target_lat, target_lon], zoom_start=9, tiles="cartodbpositron")

# 添加所有办公室标记
for rec in recommendations:
    # 构造悬停显示的文本 (HTML 格式)
    hover_html = f"""
        <b>办公室名称:</b> {rec['name']}<br>
        <b>ZMA 代码:</b> {rec['code']}<br>
        <b>地址:</b> {rec['addr']}<br>
        <b>距离:</b> {rec['dist']:.2f} KM
    """
    
    folium.Marker(
        location=[rec["lat"], rec["lon"]],
        tooltip=folium.Tooltip(hover_html, sticky=True), # 鼠标触碰显示
        icon=folium.Icon(color="blue" if rec["dist"] < 0.1 else "red", icon="info-sign")
    ).add_to(m)

# --- 6. 页面布局 ---
col_map, col_list = st.columns([3, 1.5])

with col_map:
    st.subheader("🗺️ RMV 分布地图")
    st_folium(m, width=800, height=600)

with col_list:
    st.subheader("📍 最近的 3 个办公室")
    for i in range(min(3, len(recommendations))):
        rec = recommendations[i]
        st.warning(f"**推荐 {i+1}: {rec['name']}**")
        st.write(f"- **ZMA 代码**: `{rec['code']}`")
        st.write(f"- **详细地址**: {rec['addr']}")
        st.write(f"- **直线距离**: {rec['dist']:.2f} KM")
        st.write("---")

    st.info("💡 提示：在左侧搜索城市后，列表将自动更新。")
