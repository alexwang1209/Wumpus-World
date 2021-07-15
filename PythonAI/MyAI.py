# ======================================================================
# FILE:        MyAI.py
#
# AUTHOR:      Abdullah Younis
#
# DESCRIPTION: This file contains your agent class, which you will
#              implement. You are responsible for implementing the
#              'getAction' function and any helper methods you feel you
#              need.
#
# NOTES:       - If you are having trouble understanding how the shell
#                works, look at the other parts of the code, as well as
#                the documentation.
#
#              - You are only allowed to make changes to this portion of
#                the code. Any changes to other portions of the code will
#                be lost when the tournament runs your code.
# ======================================================================

from Agent import Agent


class MyAI(Agent):




    def __init__(self):

        # agent info
        self.x = 1
        self.y = 1
        self.direction = "right"
        self.has_gold = False
        self.escape_mode = False
        self.last_action = None
        self.target_square = None
        self.way_back_home = []
        self.traversed = {(1, 1)}

        # pit info
        self.breezesquares = set()
        self.possiblepits = set()
        self.no_pits_sqrs = {(1, 1)}
        self.breeze_possible_pits_dic = {}
        self.pits = set()
        self.possible_pit_prob = {}

        # wumpus info
        self.kill_mode = False
        self.has_arrow = True
        self.stenchsquares = set()
        self.wumpus_dead = False
        self.possible_wumpus_pos = set()
        self.no_wumpus_sqrs = {(1, 1)}
        self.wumpus_unsure = set()
        self.wumpus_pos_known = False
        self.wumpus_loc = None
        self.shot_loc = None

        # world info
        self.safesquares = {(1, 1)}
        self.world_X = None
        self.world_Y = None

        # for sake of efficiency
        self.prev_len = 0




    # main step function
    def getAction(self, stench, breeze, glitter, bump, scream):

        # update info every move
        if bump:
            if self.direction == "left":
                self.x += 1
            elif self.direction == "up":
                self.y += -1
                self.world_Y = self.y
            elif self.direction == "right":
                self.x += -1
                self.world_X = self.x
            elif self.direction == "down":
                self.y += 1
        self.safesquares.add((self.x, self.y))
        self.traversed.add((self.x, self.y))
        adjsquares = [(self.x - 1, self.y), (self.x + 1, self.y), (self.x, self.y - 1), (self.x, self.y + 1)]
        if not stench and not breeze:
            self.update_safesquares()
        if self.wumpus_dead and not breeze:
            self.update_safesquares()
        if not stench:
            self.update_no_wumpus_sqrs()
        elif self.wumpus_dead:
            self.update_no_wumpus_sqrs()
        else:
            self.update_wumpus_info()
        if not breeze:
            self.update_no_pit_sqrs()
        else:
            self.update_pit_info()
        self.general_update()
        self.update_target()
        self.shorten_homepath()
        if len(self.traversed) != self.prev_len:
            self.prev_len = len(self.traversed)
            self.update_pit_prob()



        # DEBUG PRINT INFO #
        # print("\ncurrent spot: " + str((self.x, self.y)))
        # print("traversed: " + str(self.traversed))
        # print("safesquares: " + str(self.safesquares))
        # print("no wumpus squares: " + str(self.no_wumpus_sqrs))
        # print("possible wumpus squares: " + str(self.possible_wumpus_pos))
        # print("stench squares: " + str(self.stenchsquares))
        # print("possible pits: " + str(self.possiblepits))
        # print("breeze pits dic: " + str(self.breeze_possible_pits_dic))
        # print("pits: " + str(self.pits))
        # print("possible pits prob: " + str(self.possible_pit_prob) + "\n")



        # if gold picked up, then make way back to exit and climb
        if self.has_gold:
            return self.go_exit()


        # if there is a glitter, pick up the gold
        if glitter:
            self.has_gold = True
            self.last_action = "GRAB"
            return Agent.Action.GRAB



        # if has a target
        if self.target_square != None:
            # print("target square: " + str(self.target_square))
            if self.x == self.target_square[0] and self.y == self.target_square[1]:
                self.target_square = None
            else:
                return self.go_to(self.target_square)



        # ready to shoot wumpus
        if self.kill_mode:
            return self.kill_wumpus()
        if self.last_action == "SHOOT":
            if scream:
                self.wumpus_dead = True
                self.no_wumpus_sqrs.update(self.wumpus_unsure)
                if self.wumpus_pos_known:
                    sqr = (self.wumpus_x, self.wumpus_y)
                    self.possible_wumpus_pos = set()
                    self.no_wumpus_sqrs.add(sqr)
                    if sqr not in self.possiblepits:
                        self.safesquares.add(sqr)
                elif self.x == 1 and self.y == 1:
                    self.no_wumpus_sqrs.add((1, 2))
                    self.no_wumpus_sqrs.add((2, 1))
                    self.wumpus_x = 2
                    self.wumpus_y = 1
                    self.wumpus_pos_known = True
                    self.update_safesquares()
                else:
                    self.wumpus_pos_known = True
                    self.no_wumpus_sqrs.update(adjsquares)
                    if self.direction == "left":
                        self.wumpus_x = self.shot_loc[0] - 1
                        self.wumpus_y = self.shot_loc[1]
                    if self.direction == "right":
                        self.wumpus_x = self.shot_loc[0] + 1
                        self.wumpus_y = self.shot_loc[1]
                    if self.direction == "up":
                        self.wumpus_x = self.shot_loc[0]
                        self.wumpus_y = self.shot_loc[1] + 1
                    if self.direction == "down":
                        self.wumpus_x = self.shot_loc[0]
                        self.wumpus_y = self.shot_loc[1] - 1
                self.update_safesquares()
            else:
                if self.x == 1 and self.y == 1:
                    self.possible_wumpus_pos.add((1, 2))
                    self.no_wumpus_sqrs.add((2, 1))
                    self.wumpus_x = 1
                    self.wumpus_y = 2
                    self.wumpus_pos_known = True
                    self.general_update()
                else:
                    if self.direction == "left":
                        self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[1] != self.y}
                        self.no_wumpus_sqrs.add((self.x - 1, self.y))
                    if self.direction == "right":
                        self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[1] != self.y}
                        self.no_wumpus_sqrs.add((self.x + 1, self.y))
                    if self.direction == "up":
                        self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[1] != self.y}
                        self.no_wumpus_sqrs.add((self.x, self.y + 1))
                    if self.direction == "down":
                        self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[1] != self.y}
                        self.no_wumpus_sqrs.add((self.x, self.y - 1))
                    self.general_update()



        # if there is a stench
        if stench and not self.wumpus_dead:

            ### REPLACE LATER ############################################
            # if len(self.safesquares) > len(self.traversed):
            #     self.target_square = self.find_closest_safesquare()
            #     return self.go_to(self.target_square)
            ### REPLACE LATER ############################################

            if self.wumpus_pos_known and self.has_arrow:
                return self.kill_wumpus()

            # elif len(self.possible_wumpus_pos) == 2:
            #     self.last_action = "SHOOT"
            #     return Agent.Action.SHOOT

            elif self.x == 1 and self.y == 1 and self.has_arrow and not breeze:
                self.last_action = "SHOOT"
                self.has_arrow = False
                return Agent.Action.SHOOT

            # elif len(self.safesquares) == len(self.traversed) and len(self.traversed) < 8:
            #     self.shot_loc = (self.x, self.y)
            #     self.last_action = "SHOOT"
            #     self.has_arrow = False
            #     return Agent.Action.SHOOT

            else:
                if len(self.safesquares) > len(self.traversed):
                    self.target_square = self.find_closest_safesquare()
                    return self.go_to(self.target_square)



        # if there is a breeze
        if breeze:

            if len(self.safesquares) > len(self.traversed):
                self.target_square = self.find_closest_safesquare()
                return self.go_to(self.target_square)

            ### REPLACE LATER ############################################
            # self.escape_mode = True
            ### REPLACE LATER ############################################

            self.update_pit_prob()
            least_risk_p = min(self.possible_pit_prob.values())

            if least_risk_p < 0.25 and len(self.traversed) < 25:
                candidates = [k for k, v in self.possible_pit_prob.items() if v == least_risk_p]
                sqr = self.find_closest(candidates)
                if not self.wumpus_dead and sqr in self.possible_wumpus_pos:
                    self.escape_mode = True
                else:
                    self.possiblepits.remove(sqr)
                    del self.possible_pit_prob[sqr]
                    self.no_pits_sqrs.add(sqr)
                    self.safesquares.add(sqr)
                    self.target_square = sqr
                    return self.go_to(sqr)
            else:
                self.escape_mode = True



        # if it is time to run
        if self.escape_mode:
            return self.go_exit()



        ### REPLACE LATER ################################################
        if len(self.traversed) == len(self.safesquares):
            if self.x == 1 and self.y == 1:
                return Agent.Action.CLIMB
            return self.go_to((1, 1))
        ### REPLACE LATER ################################################



        # hit boundary
        if len(self.safesquares) > len(self.traversed):
            if self.direction == "left" and self.x == 1:
                self.target_square = self.find_closest_safesquare()
                return self.go_to(self.target_square)
            if self.direction == "up" and self.world_Y is not None and self.y == self.world_Y:
                self.target_square = self.find_closest_safesquare()
                return self.go_to(self.target_square)
            if self.direction == "right" and self.world_X is not None and self.x == self.world_X:
                self.target_square = self.find_closest_safesquare()
                return self.go_to(self.target_square)
            if self.direction == "down" and self.y == 1:
                self.target_square = self.find_closest_safesquare()
                return self.go_to(self.target_square)


        # default move forward
        if self.direction == "left":
            # if (self.x - 1, self.y) in self.traversed:
            #     self.target_square = self.find_closest_safesquare()
            #     return self.go_to(self.target_square)
            self.x += -1
        elif self.direction == "up":
            # if (self.x, self.y + 1) in self.traversed:
            #     self.target_square = self.find_closest_safesquare()
            #     return self.go_to(self.target_square)
            self.y += 1
        elif self.direction == "right":
            # if (self.x + 1, self.y) in self.traversed:
            #     self.target_square = self.find_closest_safesquare()
            #     return self.go_to(self.target_square)
            self.x += 1
        elif self.direction == "down":
            # if (self.x, self.y - 1) in self.traversed:
            #     self.target_square = self.find_closest_safesquare()
            #     return self.go_to(self.target_square)
            self.y += -1
        self.last_action = "FORWARD"
        return Agent.Action.FORWARD










    # get to a square from safesquares
    def go_to(self, square):

        if self.x == square[0] and self.y == square[1]:
            return

        path = self.bfs(self.safesquares, (self.x, self.y), (square[0], square[1]))
        next_square = path[0]

        if self.x > next_square[0]:
            if self.direction == "left":
                del path[0]
                self.x += -1
                self.last_action = "FORWARD"
                return Agent.Action.FORWARD
            elif self.direction == "up":
                self.direction = "left"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            elif self.direction == "right":
                self.direction = "up"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            else:
                self.direction = "left"
                self.last_action = "TURN_RIGHT"
                return Agent.Action.TURN_RIGHT

        if self.x < next_square[0]:
            if self.direction == "left":
                self.direction = "down"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            elif self.direction == "up":
                self.direction = "right"
                self.last_action = "TURN_RIGHT"
                return Agent.Action.TURN_RIGHT
            elif self.direction == "right":
                del path[0]
                self.x += 1
                self.last_action = "FORWARD"
                return Agent.Action.FORWARD
            else:
                self.direction = "right"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT

        if self.y > next_square[1]:
            if self.direction == "left":
                self.direction = "down"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            elif self.direction == "up":
                self.direction = "left"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            elif self.direction == "right":
                self.direction = "down"
                self.last_action = "TURN_RIGHT"
                return Agent.Action.TURN_RIGHT
            else:
                del path[0]
                self.y += -1
                self.last_action = "FORWARD"
                return Agent.Action.FORWARD

        if self.y < next_square[1]:
            if self.direction == "left":
                self.direction = "up"
                self.last_action = "TURN_RIGHT"
                return Agent.Action.TURN_RIGHT
            elif self.direction == "up":
                del path[0]
                self.y += 1
                self.last_action = "FORWARD"
                return Agent.Action.FORWARD
            elif self.direction == "right":
                self.direction = "up"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            else:
                self.direction = "right"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT



    # # NOT OPTIMIZED ###################
    # # uses breadth-first search to return a list of the shortest path to destination from origin with the possible paths
    # def bfs(self, paths, origin: tuple, destination: tuple):
    #
    #     graph = {}
    #     final_path = []
    #     frontier = []
    #     visited = set()
    #
    #     if origin != destination:
    #         frontier.append(origin)
    #
    #     while len(frontier) != 0:
    #         sqr = frontier.pop(0)
    #         visited.add(sqr)
    #         adjsquares = [(sqr[0] - 1, sqr[1]), (sqr[0] + 1, sqr[1]), (sqr[0], sqr[1] - 1), (sqr[0], sqr[1] + 1)]
    #         to_search = [s for s in adjsquares if s in paths and s not in visited]
    #         for s in to_search:
    #             graph[s] = sqr
    #             frontier.append(s)
    #             if s == destination:
    #                 currentsqr = s
    #                 while currentsqr != origin:
    #                     final_path.append(currentsqr)
    #                     currentsqr = graph[currentsqr]
    #                 final_path.reverse()
    #                 return final_path
    #
    #     return final_path




    # optimized version of bfs
    def bfs(self, paths, origin: tuple, destination: tuple):

        graph = {}
        final_path = []
        frontier = [(origin[0], origin[1], self.direction)]
        visited = set()

        while len(frontier) != 0:
            sqr = frontier.pop(0)
            visited.add(sqr)
            adj_sqrs = []
            if sqr[2] == "left":
                adj_sqrs = [(sqr[0] - 1, sqr[1], "left"), (sqr[0], sqr[1], "up"), (sqr[0], sqr[1], "down")]
            elif sqr[2] == "up":
                adj_sqrs = [(sqr[0], sqr[1], "left"), (sqr[0], sqr[1] + 1, "up"), (sqr[0], sqr[1], "right")]
            elif sqr[2] == "right":
                adj_sqrs = [(sqr[0], sqr[1], "up"), (sqr[0] + 1, sqr[1], "right"), (sqr[0], sqr[1], "down")]
            else:
                adj_sqrs = [(sqr[0], sqr[1], "left"), (sqr[0], sqr[1], "right"), (sqr[0], sqr[1] - 1, "down")]
            to_search = [s for s in adj_sqrs if (s[0], s[1]) in paths and s not in visited]
            for s in to_search:
                graph[s] = sqr
                frontier.append(s)
                if (s[0], s[1]) == destination:
                    currentsqr = s
                    while (currentsqr[0], currentsqr[1]) != origin:
                        final_path.append(currentsqr)
                        currentsqr = graph[currentsqr]
                    final_path.reverse()
                    for i in range(len(final_path)):
                        final_path[i] = (final_path[i][0], final_path[i][1])
                    final_path = list(dict.fromkeys(final_path))
                    return final_path

        return final_path




    # find the square that is the closest to get to
    def find_closest(self, sqrs):
        dic = {}
        for sqr in sqrs:
            dic[sqr] = len(self.bfs(self.safesquares, (self.x, self.y), sqr))
        lengths = sorted(dic.items(), key=lambda x: x[1])
        return lengths[0][0]




    # find closest not explored safesquare
    def find_closest_safesquare(self):

        not_traversed = self.safesquares - self.traversed
        frontier = []
        visited = set()

        if len(not_traversed) != 0:
            frontier.append((self.x, self.y))

        while len(frontier) != 0:
            sqr = frontier.pop(0)
            visited.add(sqr)
            adj_sqrs = [(sqr[0] - 1, sqr[1]), (sqr[0] + 1, sqr[1]), (sqr[0], sqr[1] - 1), (sqr[0], sqr[1] + 1)]
            to_search = [s for s in adj_sqrs if s in self.safesquares and s not in visited]
            for s in to_search:
                frontier.append(s)
                if s in not_traversed:
                    return s




    # find the square that is the closest to get to
    def find_closest(self, sqrs):
        dic = {}
        temp = self.safesquares.union(sqrs)
        for sqr in sqrs:
            dic[sqr] = len(self.bfs(temp, (self.x, self.y), sqr))
        lengths = sorted(dic.items(), key=lambda x: x[1])
        return lengths[0][0]




    # kill wumpus
    def kill_wumpus(self):
        self.kill_mode = True
        adjsquares = [(self.wumpus_x - 1, self.wumpus_y), (self.wumpus_x + 1, self.wumpus_y), (self.wumpus_x, self.wumpus_y - 1), (self.wumpus_x, self.wumpus_y + 1)]
        possible = [s for s in adjsquares if s in self.safesquares]
        self.target_square = self.find_closest(possible)
        if self.x != self.target_square[0] or self.y != self.target_square[1]:
            return self.go_to(self.target_square)
        else:
            return self.turn_to_and_shoot(self.wumpus_x, self.wumpus_y)


    # turn to an adjacent square
    def turn_to_and_shoot(self, x, y):

        if self.x > x:
            if self.direction == "left":
                self.kill_mode = False
                self.last_action = "SHOOT"
                return Agent.Action.SHOOT
            elif self.direction == "up":
                self.direction = "left"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            elif self.direction == "right":
                self.direction = "up"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            else:
                self.direction = "left"
                self.last_action = "TURN_RIGHT"
                return Agent.Action.TURN_RIGHT

        if self.x < x:
            if self.direction == "left":
                self.direction = "down"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            elif self.direction == "up":
                self.direction = "right"
                self.last_action = "TURN_RIGHT"
                return Agent.Action.TURN_RIGHT
            elif self.direction == "right":
                self.kill_mode = False
                self.last_action = "SHOOT"
                return Agent.Action.SHOOT
            else:
                self.direction = "right"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT

        if self.y > y:
            if self.direction == "left":
                self.direction = "down"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            elif self.direction == "up":
                self.direction = "left"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            elif self.direction == "right":
                self.direction = "down"
                self.last_action = "TURN_RIGHT"
                return Agent.Action.TURN_RIGHT
            else:
                self.kill_mode = False
                self.last_action = "SHOOT"
                return Agent.Action.SHOOT

        if self.y < y:
            if self.direction == "left":
                self.direction = "up"
                self.last_action = "TURN_RIGHT"
                return Agent.Action.TURN_RIGHT
            elif self.direction == "up":
                self.kill_mode = False
                self.last_action = "SHOOT"
                return Agent.Action.SHOOT
            elif self.direction == "right":
                self.direction = "up"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            else:
                self.direction = "right"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT




    # check if there is a shorter way back home
    def shorten_homepath(self):
        path = self.bfs(self.safesquares, (self.x, self.y), (1, 1))
        path.reverse()
        self.way_back_home = path




    # update safesquares if no dangerous percepts
    def update_safesquares(self):
        self.safesquares.add((self.x, self.y))
        adjsquares = [(self.x - 1, self.y), (self.x + 1, self.y), (self.x, self.y - 1), (self.x, self.y + 1)]
        for sqr in adjsquares:
            if sqr in self.no_wumpus_sqrs and sqr in self.no_pits_sqrs:
                self.safesquares.add(sqr)
        self.safesquares = {s for s in self.safesquares if s[0] > 0 and s[1] > 0}
        if self.world_X is not None:
            self.safesquares = {s for s in self.safesquares if s[0] < self.world_X + 1}
        if self.world_Y is not None:
            self.safesquares = {s for s in self.safesquares if s[1] < self.world_Y + 1}




    # update no_wumpus_sqrs
    def update_no_wumpus_sqrs(self):
        self.no_wumpus_sqrs.add((self.x, self.y))
        adjsquares = [(self.x - 1, self.y), (self.x + 1, self.y), (self.x, self.y - 1), (self.x, self.y + 1)]
        for sqr in adjsquares:
            self.no_wumpus_sqrs.add(sqr)
        self.no_wumpus_sqrs = {s for s in self.no_wumpus_sqrs if s[0] > 0 and s[1] > 0}
        if self.world_X is not None:
            self.no_wumpus_sqrs = {s for s in self.no_wumpus_sqrs if s[0] < self.world_X + 1}
        if self.world_Y is not None:
            self.no_wumpus_sqrs = {s for s in self.no_wumpus_sqrs if s[1] < self.world_Y + 1}
        self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s not in self.no_wumpus_sqrs}
        if len(self.possible_wumpus_pos) == 1:
            xs = list(self.possible_wumpus_pos)
            self.wumpus_x = xs[0][0]
            self.wumpus_y = xs[0][1]
            self.wumpus_pos_known = True




    # update no_pit_sqrs
    def update_no_pit_sqrs(self):
        self.no_pits_sqrs.add((self.x, self.y))
        adjsquares = [(self.x - 1, self.y), (self.x + 1, self.y), (self.x, self.y - 1), (self.x, self.y + 1)]
        for sqr in adjsquares:
            self.no_pits_sqrs.add(sqr)
        self.no_pits_sqrs = {s for s in self.no_pits_sqrs if s[0] > 0 and s[1] > 0}
        if self.world_X is not None:
            self.no_pits_sqrs = {s for s in self.no_pits_sqrs if s[0] < self.world_X + 1}
        if self.world_Y is not None:
            self.no_pits_sqrs = {s for s in self.no_pits_sqrs if s[1] < self.world_Y + 1}
        self.possiblepits = {s for s in self.possiblepits if s not in self.no_pits_sqrs}
        for k in self.breeze_possible_pits_dic:
            self.breeze_possible_pits_dic[k] = {s for s in self.breeze_possible_pits_dic[k] if s not in self.no_pits_sqrs}
            if len(self.breeze_possible_pits_dic[k]) == 1:
                for sqr in self.breeze_possible_pits_dic[k]:
                    self.pits.add(sqr)




    # update wumpus info if stench
    def update_wumpus_info(self):
        self.stenchsquares.add((self.x, self.y))
        adjsquares = {(self.x - 1, self.y), (self.x + 1, self.y), (self.x, self.y - 1), (self.x, self.y + 1)}
        if len(self.stenchsquares) == 1:
            for sqr in adjsquares:
                if sqr not in self.no_wumpus_sqrs:
                    self.possible_wumpus_pos.add(sqr)
                    self.wumpus_unsure.add(sqr)
        else:
            self.possible_wumpus_pos = self.possible_wumpus_pos.intersection(adjsquares)

        self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[0] > 0 and s[1] > 0}
        if self.world_X is not None:
            self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[0] < self.world_X + 1}
        if self.world_Y is not None:
            self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[1] < self.world_Y + 1}

        if len(self.stenchsquares) == 2 and not self.wumpus_pos_known:
            xs = list(self.stenchsquares)
            if xs[0][0] == xs[1][0]:
                self.wumpus_x = xs[0][0]
                self.wumpus_y = (xs[0][1] + xs[1][1]) / 2
                self.wumpus_pos_known = True
            elif xs[0][1] == xs[1][1]:
                self.wumpus_x = (xs[0][0] + xs[1][0]) / 2
                self.wumpus_y = xs[0][1]
                self.wumpus_pos_known = True
            else:
                pass

        elif len(self.stenchsquares) == 3 and not self.wumpus_pos_known:
            xs = list(self.stenchsquares)
            if xs[0][0] == xs[1][0] or xs[1][0] == xs[2][0] or xs[2][0] == xs[0][0]:
                if xs[0][0] == xs[1][0]:
                    self.wumpus_x = xs[0][0]
                    self.wumpus_y = (xs[0][1] + xs[1][1]) / 2
                    self.wumpus_pos_known = True
                if xs[1][0] == xs[2][0]:
                    self.wumpus_x = xs[1][0]
                    self.wumpus_y = (xs[1][1] + xs[2][1]) / 2
                    self.wumpus_pos_known = True
                if xs[2][0] == xs[0][0]:
                    self.wumpus_x = xs[2][0]
                    self.wumpus_y = (xs[2][1] + xs[0][1]) / 2
                    self.wumpus_pos_known = True
            else:
                if xs[0][1] == xs[1][1]:
                    self.wumpus_x = xs[0][1]
                    self.wumpus_y = (xs[0][0] + xs[1][0]) / 2
                    self.wumpus_pos_known = True
                if xs[1][1] == xs[2][1]:
                    self.wumpus_x = xs[1][1]
                    self.wumpus_y = (xs[1][0] + xs[2][0]) / 2
                    self.wumpus_pos_known = True
                if xs[2][1] == xs[0][1]:
                    self.wumpus_x = xs[2][1]
                    self.wumpus_y = (xs[2][0] + xs[0][0]) / 2
                    self.wumpus_pos_known = True

        if len(self.possible_wumpus_pos) == 1:
            xs = list(self.possible_wumpus_pos)
            self.wumpus_x = xs[0][0]
            self.wumpus_y = xs[0][1]
            self.wumpus_pos_known = True




    #update pit info if breeze
    def update_pit_info(self):

        self.breezesquares.add((self.x, self.y))
        adjsquares = [(self.x - 1, self.y), (self.x + 1, self.y), (self.x, self.y - 1), (self.x, self.y + 1)]
        for sqr in adjsquares:
            if sqr not in self.no_pits_sqrs:
                self.possiblepits.add(sqr)
        self.breeze_possible_pits_dic[(self.x, self.y)] = {s for s in adjsquares if s not in self.no_pits_sqrs}

        self.possiblepits = {s for s in self.possiblepits if s[0] > 0 and s[1] > 0}
        if self.world_X is not None:
            self.possiblepits = {s for s in self.possiblepits if s[0] < self.world_X + 1}
        if self.world_Y is not None:
            self.possiblepits = {s for s in self.possiblepits if s[1] < self.world_Y + 1}

        for k in self.breeze_possible_pits_dic:
            self.breeze_possible_pits_dic[k] = {s for s in self.breeze_possible_pits_dic[k] if s[0] > 0 and s[1] > 0}
            if self.world_X is not None and self.x == self.world_X:
                self.breeze_possible_pits_dic[k] = {s for s in self.breeze_possible_pits_dic[k] if s[0] < self.world_X + 1}
            if self.world_Y is not None and self.y == self.world_Y:
                self.breeze_possible_pits_dic[k] = {s for s in self.breeze_possible_pits_dic[k] if s[1] < self.world_Y + 1}
            if len(self.breeze_possible_pits_dic[k]) == 1:
                for sqr in self.breeze_possible_pits_dic[k]:
                    self.pits.add(sqr)




    # general update
    def general_update(self):
        temp = {s for s in self.no_wumpus_sqrs if s in self.no_pits_sqrs}
        self.safesquares.update(temp)




    # update target square
    def update_target(self):
        if self.target_square is not None:
            if self.target_square not in self.safesquares:
                self.target_square = None



    # given a set, return a powerlist
    def powerlist(self, s):
        xs = list(s)
        if xs == []:
            return [[]]
        x = self.powerlist(xs[1:])
        return x + [[xs[0]] + y for y in x]



    # update possible_pit_prob
    def update_pit_prob(self):
        possible_pit_configs = []
        pl = self.powerlist(self.possiblepits)
        pl.remove([])
        # print("pl: " + str(pl))
        for config in pl:
            for pit in self.pits:
                if pit not in config:
                    break
            adj_breeze_sqrs = set()
            for sqr in config:
                adj_sqrs = [(sqr[0] - 1, sqr[1]), (sqr[0] + 1, sqr[1]), (sqr[0], sqr[1] - 1), (sqr[0], sqr[1] + 1)]
                adj_breeze_sqrs.update(adj_sqrs)
            for sqr in self.breezesquares:
                if sqr not in adj_breeze_sqrs:
                    break
            else:
                possible_pit_configs.append(config)

        # print("possible pit configs: " + str(possible_pit_configs))

        self.possible_pit_prob = {}
        denominator = 0
        n = len(self.possiblepits)
        for config in possible_pit_configs:
            m = len(config)
            term = ((1 / 5)**m) * ((4 / 5)**(n - m))
            denominator += term
        for sqr in self.possiblepits:
            numerator = 0
            for config in possible_pit_configs:
                if sqr in config:
                    m = len(config)
                    term = ((1 / 5) ** m) * ((4 / 5) ** (n - m))
                    numerator += term
            self.possible_pit_prob[sqr] = numerator / denominator



    # follow way back home
    def go_exit(self):

        if len(self.way_back_home) == 0:
            return Agent.Action.CLIMB

        last_square = self.way_back_home[-1]

        if self.x > last_square[0]:
            if self.direction == "left":
                del self.way_back_home[-1]
                self.x += -1
                self.last_action = "FORWARD"
                return Agent.Action.FORWARD
            elif self.direction == "up":
                self.direction = "left"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            elif self.direction == "right":
                self.direction = "up"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            else:
                self.direction = "left"
                self.last_action = "TURN_RIGHT"
                return Agent.Action.TURN_RIGHT

        if self.x < last_square[0]:
            if self.direction == "left":
                self.direction = "down"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            elif self.direction == "up":
                self.direction = "right"
                self.last_action = "TURN_RIGHT"
                return Agent.Action.TURN_RIGHT
            elif self.direction == "right":
                del self.way_back_home[-1]
                self.x += 1
                self.last_action = "FORWARD"
                return Agent.Action.FORWARD
            else:
                self.direction = "right"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT

        if self.y > last_square[1]:
            if self.direction == "left":
                self.direction = "down"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            elif self.direction == "up":
                self.direction = "left"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            elif self.direction == "right":
                self.direction = "down"
                self.last_action = "TURN_RIGHT"
                return Agent.Action.TURN_RIGHT
            else:
                del self.way_back_home[-1]
                self.y += -1
                self.last_action = "FORWARD"
                return Agent.Action.FORWARD

        if self.y < last_square[1]:
            if self.direction == "left":
                self.direction = "up"
                self.last_action = "TURN_RIGHT"
                return Agent.Action.TURN_RIGHT
            elif self.direction == "up":
                del self.way_back_home[-1]
                self.y += 1
                self.last_action = "FORWARD"
                return Agent.Action.FORWARD
            elif self.direction == "right":
                self.direction = "up"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            else:
                self.direction = "right"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
