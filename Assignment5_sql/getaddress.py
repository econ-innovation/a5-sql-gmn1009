import requests
import sqlite3
import csv
import pandas as pd  # 引入 Pandas

# 读取TXT文件并添加列名
file_path = 'address.txt'
df = pd.read_csv(file_path, header=None, names=['address'])

# 创建SQLite数据库并将数据导入
conn = sqlite3.connect('addresses.db')
df.to_sql('addresses', conn, if_exists='replace', index=False)
conn.close()

# 高德地图API的基础URL和密钥
AMAP_URL = "https://restapi.amap.com/v3/geocode/geo"
AMAP_KEY = "8900073eeda5ed165bd768cf6a5459db"

# 输出CSV文件
output_csv_file = 'address_geo_info.csv'

# CSV头部
headers = ['address', 'Province', 'City', 'District', 'Street', 'Longitude', 'Latitude']

# 打开CSV文件准备写入
with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()

    # 从SQLite数据库中读取地址
    conn = sqlite3.connect('addresses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT address FROM addresses")

    for row in cursor.fetchall():
        address = row[0]
        params = {
            "key": AMAP_KEY,
            "address": address
        }
        response = requests.get(AMAP_URL, params=params)
        data = response.json()

        if data["status"] == "1" and data["geocodes"]:
            geo_info = data["geocodes"][0]
            location = geo_info["location"].split(',')
            address_dict = {
                'address': address,
                'Province': geo_info['province'],
                'City': geo_info['city'],
                'District': geo_info['district'],
                'Street': geo_info.get('street', ''),
                'Longitude': location[0],
                'Latitude': location[1]
            }
            writer.writerow(address_dict)
            print(address_dict)
        else:
            print(f"地址: {address}, 未找到地理信息")

    conn.close()

print(f"地理信息已保存到 {output_csv_file}")
