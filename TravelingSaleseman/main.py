
# ---------------------------------------------------------
# 登録地点近傍のレストラン店舗の最適巡回経路作成ツール
# （蟻コロニー最適化法による巡回セールスマン問題解決）
# 
#                             Coded by AKIHIKO ITO in 2019
# ---------------------------------------------------------

# ---------------------------------------------------------
# モジュール
# ---------------------------------------------------------
from webapi import GuruNaviRestSearchAPI      as GNaviAPI
from webapi import GoogleMapGeocodingAPI      as GeocodingAPI
from webapi import GoogleMapDistanceMatrixAPI as DistMatAPI
from webapi import GoogleMapPlotAPI           as MapPlotAPI
from aco    import TSPSolver                  as TSPSolver

# ---------------------------------------------------------
# 検索パラメータ
# ---------------------------------------------------------
name_place = "新宿駅"
freeword   = "豚骨ラーメン"
range_area = 2  # 1:300m、2:500m、3:1000m、4:2000m、5:3000m

# ---------------------------------------------------------
# ジオコーディング（地理座標取得）
# ---------------------------------------------------------
geocod = GeocodingAPI()
if (not geocod.get_position(name_place)):
    print("*** Geocoding Error ***")
    print(geocod.err_message)
    quit(1)

# 地理座標出力
print("Geocoding Done.")
print("Lat:"+str(geocod.latitude)+ \
      " Lng:"+str(geocod.longitude))
print("")

# ---------------------------------------------------------
# ぐるなびレストラン検索
# ---------------------------------------------------------
gnavi  = GNaviAPI()
if ( not gnavi.search(geocod.latitude,geocod.longitude,range_area,freeword) ):
    print("*** GuruNavi Restaurant Search Error ***")
    print(gnavi.err_code)
    print(gnavi.err_message)
    quit(1)

# 検索結果出力
print("GuruNavi Restaurant Search Done.")
print("Search Number: "+str(gnavi.num_data))
for i in range (gnavi.num_data):
    print(gnavi.shopnames[i])
print("")

# ---------------------------------------------------------
# 距離マトリックス計算
# ---------------------------------------------------------
dstmat = DistMatAPI()
latitudes  = []
longitudes = []
latitudes .append(geocod.latitude )
longitudes.append(geocod.longitude)
latitudes  += gnavi.latitudes
longitudes += gnavi.longitudes

if ( not dstmat.get_matrix(latitudes, longitudes)):
    print("*** Matrix Genration Error ***")
    quit(1)

# マトリックス出力
print("Matrix Generation Done.")
for i in range (len(dstmat.matrix)):
    print(dstmat.matrix[i])
print("")

# ---------------------------------------------------------
# 蟻コロニー最適化法による巡回セールスマン問題解決
# ---------------------------------------------------------
solver_tsp = TSPSolver()

pos_stt = 0       # 初期位置
num_ant = 50      # 一度に放たれる蟻の数
num_itr = 50      # 巡回させる回数
exp_phr = 1       # フェロモン優先指数
exp_dst = 2       # 距離優先指数
r_evap  = 0.4     # フェロモン蒸発率
q_phr   = 2000.0  # フェロモン分泌係数

solver_tsp.solve(
    mat_dst = dstmat.matrix,
    pos_stt = pos_stt,
    num_ant = num_ant,
    num_itr = num_itr,
    exp_phr = exp_phr,
    exp_dst = exp_dst,
    r_evap  = r_evap,
    q_phr   = q_phr,
    b_print = True)

print("")

# ---------------------------------------------------------
# 計算結果のプロット
# ---------------------------------------------------------
mapplot = MapPlotAPI()
mapplot.create_map(geocod.latitude,geocod.longitude,16)

mapplot.add_marker(geocod.latitude,geocod.longitude,name_place,"red")
for i in range(gnavi.num_data):
    mapplot.add_marker(gnavi.latitudes[i],gnavi.longitudes[i],gnavi.shopnames[i])

for i in range(len(solver_tsp.final_route)-1):
    id_org = solver_tsp.final_route[i  ]
    id_dst = solver_tsp.final_route[i+1]
    mapplot.plot_route(latitudes[id_org],longitudes[id_org],latitudes[id_dst],longitudes[id_dst])

name_file_output = "result.html"
mapplot.save_map(name_file_output)

print("Plot Saved to " + name_file_output)
print("")
print("Program Done.")