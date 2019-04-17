
# ---------------------------------------------------------
# 蟻コロニー最適化法による
# 巡回セールスマン問題解決アルゴリズム
# 
#                             Coded by AKIHIKO ITO in 2019
# ---------------------------------------------------------

import random

# ---------------------------------------------------------
# ソルバークラス
# ---------------------------------------------------------
class TSPSolver:

    # 確率分布からインデックスをランダムに選ぶ
    def choose_random_index(self, probabilities):
        sum_prob = sum(probabilities)
        probabilities_norm = [p/sum_prob for p in probabilities]
        val_num = random.random()

        id_choose = 0
        for i in range(len(probabilities_norm)):
            val_num = val_num - probabilities_norm[i]
            if ( val_num<=0 ):
                id_choose = i
                break
                
        return id_choose

    # 巡回セールスマン問題を解く
    def solve(self, mat_dst, pos_stt=0, num_ant=20, num_itr=50, exp_phr=1, exp_dst=5, r_evap=0.4, q_phr=1000.0, b_print=False):
        # mat_dst : 距離配列
        # pos_stt : 初期地点のID
        # num_ant : 一度に放たれる蟻の数
        # num_itr : 繰り返し回数
        # num_itr : 繰り返し数
        # exp_phr : フェロモン優先度
        # exp_dst : 距離優先度
        # r_evap  : フェロモン蒸発率
        # q_phr   : フェロモン分泌係数

        val_att_inf = 1e3 # 距離がゼロの場合の魅惑値

        if b_print:
            print("-----------------------------------------")
            print("Traveling Saleseman Problem Solver Start,")

        num_town = len(mat_dst)
        towns = [i for i in range(num_town)]

        # ヒューリスティックな魅惑値 (距離の逆数)
        mat_att = [[1/mat_dst[i][j] if (mat_dst[i][j]!=0.0) else val_att_inf for i in towns] for j in towns]
        
        # 初期フェロモン量
        mat_phr = [[random.random() for i in towns] for j in towns]

        self.arr_costs_best  = [] # 最適コスト
        self.arr_costs_avg   = [] # 平均コスト
        self.arr_routes_best = [] # 最適ルート
        for id_time in range(num_itr):
            arr_costs =[]
            arr_routes=[]

            for id_ant in range(num_ant):
                cost = 0.0 # 巡回コスト(=距離の総和)
                town_cur = pos_stt # 現在地
                towns_visited = [town_cur] # 訪問地
                towns_notvisited = [i for i in towns if i!=town_cur] # 未訪問地
            
                # 蟻の巡回
                while len(towns_notvisited)>0 :
                    probabilities = [pow(mat_phr[town_cur][i],exp_phr)*pow(mat_att[town_cur][i],exp_dst) \
                       for i in towns_notvisited]
                    town_next = towns_notvisited[self.choose_random_index(probabilities)]
                    cost += mat_dst[town_cur][town_next]

                    town_cur = town_next
                    towns_visited.append(town_cur)
                    towns_notvisited = [i for i in towns_notvisited if i!=town_cur]
            
                # 訪問コストおよびルート登録
                arr_costs.append(cost)
                arr_routes.append(towns_visited)

            # フェロモンの更新
            for i in range(num_town):
                for j in range(num_town):
                    mat_phr[i][j] = mat_phr[i][j]*(1-r_evap)
            
            for id_ant in range(num_ant):
                for i_town in range(num_town-1):
                    id1 = arr_routes[id_ant][i_town]
                    id2 = arr_routes[id_ant][i_town+1]
                    mat_phr[id1][id2] += q_phr/arr_costs[id_ant]

            # ベストルート選択
            id_ant_best = 0
            cost_best = arr_costs[0]
            for id_ant in range(num_ant):
                if ( arr_costs[id_ant]<cost_best ):
                    id_ant_best = id_ant
                    cost_best = arr_costs[id_ant]
            
            cost_avg = sum(arr_costs)/len(arr_costs)

            self.arr_costs_best.append(cost_best)
            self.arr_costs_avg.append(cost_avg)
            self.arr_routes_best.append(arr_routes[id_ant_best])

            if b_print:
                print("Itr=" + str(id_time) + \
                    ", Avg Cost ="+str(cost_avg) + \
                    ", Best Cost="+str(cost_best) + \
                    ", Best Route="+ str(arr_routes[id_ant_best]))

        # 計算結果の登録
        self.final_cost  = self.arr_costs_best [num_itr-1]
        self.final_route = self.arr_routes_best[num_itr-1]

        if b_print:
            print("Traveling Saleseman Problem Solver End,")
            print("-----------------------------------------")