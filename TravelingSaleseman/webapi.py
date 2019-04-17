
# ---------------------------------------------------------
# Web API (Google Map API, GuruNavi API)関連モジュール
# 
#                             Coded by AKIHIKO ITO in 2019
# ---------------------------------------------------------

import math
import requests
import folium
import googlemaps

# ---------------------------------------------------------
# ぐるなびレストラン検索
# ---------------------------------------------------------
class GuruNaviRestSearchAPI:
    __url    = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
    __keyid  = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" # use your own access key

    def search(self,latitude,longitude,range_area,freeword):
        self.num_data   = 0
        self.latitudes  = []
        self.longitudes = []
        self.shopnames  = []
        
        num_hit_per_page = 100
        params                 = {}
        params["keyid"]        = self.__keyid
        params["latitude"]     = latitude
        params["longitude"]    = longitude
        params["freeword"]     = freeword
        params["range"]        = range_area
        params["hit_per_page"] = num_hit_per_page
        params["offset_page"]  = 1
        response = requests.get(self.__url,params).json()

        if ("error" in response):
            self.err_code    = response["error"][0]["code"]
            self.err_message = response["error"][0]["message"]
            return False

        num_hit = response["total_hit_count"]
        num_itr = math.floor((num_hit-1)/num_hit_per_page)

        num_data_page = len(response["rest"])
        for iData in range(num_data_page):
            data_lat = response["rest"][iData]["latitude" ]
            data_lon = response["rest"][iData]["longitude"]
            data_name = response["rest"][iData]["name"]
            if (data_lat and data_lon):
                self.latitudes .append(float(data_lat))
                self.longitudes.append(float(data_lon))
                self.shopnames.append(data_name)

        for iSearch in range(num_itr):
            params["offset_page"] += 1
            response = requests.get(self.__url,params).json()
            num_data_page = len(response["rest"])
            for iData in range (num_data_page):
                data_lat = response["rest"][iData]["latitude" ]
                data_lon = response["rest"][iData]["longitude"]
                data_name = response["rest"][iData]["name"]
                if (data_lat and data_lon):
                    self.latitudes .append(float(data_lat))
                    self.longitudes.append(float(data_lon))
                    self.shopnames.append(data_name)

        self.num_data = len(self.latitudes)

        return True

# ---------------------------------------------------------
# ジオコーディング（Google Map API）
# ---------------------------------------------------------    
class GoogleMapGeocodingAPI:
    __url   = "https://maps.googleapis.com/maps/api/geocode/json"
    __keyid = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" # use your own access key

    def get_position(self,name_place):
        params                 = {}
        params["key"]          = self.__keyid
        params["address"]      = name_place
        params["language"]     = "ja"

        response = requests.get(self.__url,params).json()

        if (not response["status"]=="OK"):
            self.err_message = response["status"]
            return False

        self.latitude  = response["results"][0]["geometry"]["location"]["lat"]
        self.longitude = response["results"][0]["geometry"]["location"]["lng"]
        return True

# ---------------------------------------------------------
# 距離マトリックス作成（Google Map API）
# ---------------------------------------------------------   
class GoogleMapDistanceMatrixAPI:
    __url   = "https://maps.googleapis.com/maps/api/distancematrix/json"
    __keyid = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" # use your own access key

    def get_matrix(self, latitudes, longitudes):

        num_max_input = 10 # 一度に取得可能な要素数 10x10=100

        num_place = len(latitudes)
        self.matrix = [[0 for i in range(num_place)] for j in range(num_place)]

        num_itr = math.floor((num_place-1)/num_max_input)+1

        for i_search in range(num_itr):
            num_origin = num_place - i_search*num_max_input
            num_origin = num_origin if (num_origin<num_max_input) else num_max_input
            origins = ""
            for i in range (num_origin):
                origins+=str(latitudes [i+i_search*num_max_input]); origins+=","
                origins+=str(longitudes[i+i_search*num_max_input]); origins+="|"
            origins = origins[:-1]

            for j_search in range(num_itr):
                num_destination = num_place - j_search*num_max_input
                num_destination = num_destination if (num_destination<num_max_input) else num_max_input
                destinations = ""
                for j in range (num_destination):
                    destinations+=str(latitudes [j+j_search*num_max_input]); destinations+=","
                    destinations+=str(longitudes[j+j_search*num_max_input]); destinations+="|"
                destinations = destinations[:-1]

                params                 = {}
                params["key"]          = self.__keyid
                params["origins"]      = origins
                params["destinations"] = destinations
                params["mode"]         = "walking"

                response = requests.get(self.__url,params).json()

                if (not response["status"]=="OK"):
                    self.err_message = response["status"]
                    return False

                for i in range(num_origin):
                    for j in range(num_destination):
                       self.matrix[i+i_search*num_max_input][j+j_search*num_max_input] = \
                           response["rows"][i]["elements"][j]["distance"]["value"]

        return True

# ---------------------------------------------------------
# 地図のプロット（Google Map API, Folium）
# ---------------------------------------------------------  
class GoogleMapPlotAPI:
    __url   = "https://maps.googleapis.com/maps/api/directions/json"
    __keyid = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" # use your own access key

    # 地図の作成
    def create_map(self, lat_cnt, lng_cnt, zoom):
        self.map = folium.Map(location=[lat_cnt,lng_cnt], zoom_start=zoom, API_key=self.__keyid)

    # マーカー描画
    def add_marker(self, lat, lng, label, name_color="blue"):
        icon_marker = folium.Icon(color=name_color, icon="info-sign")
        folium.Marker(location=[lat,lng], popup=label, icon=icon_marker).add_to(self.map)
    
    # ルート描画
    def plot_route(self, lat_org, lng_org, lat_dst, lng_dst):
        params                 = {}
        params["key"]          = self.__keyid
        params["origin"]       = str(lat_org)+","+str(lng_org)
        params["destination"]  = str(lat_dst)+","+str(lng_dst)
        params["mode"]         = "walking"
        response = requests.get(self.__url,params).json()

        if (not response["status"]=="OK"):
            self.err_message = response["status"]
            return False

        decode = googlemaps.convert.decode_polyline
        locs_polyline = []
        for step in response["routes"][0]["legs"][0]["steps"]:
            locs = decode(step['polyline']['points'])
            locs = [[loc['lat'], loc['lng']] for loc in locs]
            locs_polyline.extend(locs)

        folium.PolyLine(locs_polyline).add_to(self.map)
        return True
    
    # 地図の出力
    def save_map(self, name_file):
        self.map.save(outfile=name_file)