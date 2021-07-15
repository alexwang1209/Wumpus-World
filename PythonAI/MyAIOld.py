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

        self.x = 1
        self.y = 1
        self.direction = "right"
        self.has_gold = False
        self.escape_mode = False
        self.last_action = None

        self.target_square = None

        self.way_back_home = []

        self.safesquares = {(1, 1)}
        self.traversed = {(1, 1)}

        self.breezesquares = set()
        self.possiblepits = set()
        self.breeze_possible_pits_dic = {}
        self.pits = set()

        self.kill_mode = False
        self.stenchsquares = set()
        self.wumpus_dead = False
        self.possible_wumpus_pos = set()
        self.no_wumpus_sqrs = set()
        self.wumpus_pos_known = False
        self.wumpus_x = None
        self.wumpus_y = None

        self.world_X = None
        self.world_Y = None




    # main step function
    def getAction(self, stench, breeze, glitter, bump, scream):


        # update info from last move while exploring
        if self.last_action == "FORWARD" and self.has_gold is False and self.escape_mode is False:
            if bump:
                if self.direction == "up":
                    self.world_Y = self.y
                if self.direction == "right":
                    self.world_X = self.x
                if not breeze and not stench:
                    self.update_safesquares()
                else:
                    self.update_safesquares_boundary()
                self.update_wumpus_loc()
                self.update_pit_locs()
                self.update_breeze_pits_dic()
                self.update_target()
            else:
                self.way_back_home.append((self.x, self.y))
                if self.direction == "left":
                    self.x += -1
                if self.direction == "up":
                    self.y += 1
                if self.direction == "right":
                    self.x += 1
                if self.direction == "down":
                    self.y += -1
                self.traversed.add((self.x, self.y))
                self.safesquares.add((self.x, self.y))
                self.update_wumpus_loc()
                self.update_pit_locs()
                self.update_breeze_pits_dic()
                self.shorten_homepath()


        # if gold picked up, then make way back to exit and climb
        if self.has_gold:
            self.update_safesquares()
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


        # if hunting the wumpus
        if self.kill_mode:
            if scream:
                self.wumpus_dead = True
                self.kill_mode = False
                if (self.wumpus_x, self.wumpus_y) not in self.possiblepits:
                    self.safesquares.add((self.wumpus_x, self.wumpus_y))
            else:
                return self.kill_wumpus()

        # no stench
        # if not stench:
        #     adjsquares = {(self.x - 1, self.y), (self.x + 1, self.y), (self.x, self.y - 1), (self.x, self.y + 1)}
        #     self.no_wumpus_sqrs.update(adjsquares)


        # if there is a scream
        # if len(self.possible_wumpus_pos) == 2 and self.last_action == "SHOOT":
        #     if scream:
        #         if self.direction == "left" or self.direction == "right":
        #             self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[1] == self.y}
        #         if self.direction == "up" or self.direction == "down":
        #             self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[0] == self.x}
        #         self.update_wumpus_loc()
        #         self.wumpus_dead = True
        #         if (self.wumpus_x, self.wumpus_y) not in self.possiblepits:
        #             self.safesquares.add((self.wumpus_x, self.wumpus_y))
        #     else:
        #         if self.direction == "left" or self.direction == "right":
        #             self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[1] != self.y}
        #         if self.direction == "up" or self.direction == "down":
        #             self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[0] != self.x}
        #         self.update_wumpus_loc()


        # if there is a stench and the wumpus has not been killed yet
        if stench and not self.wumpus_dead:
            if len(self.safesquares) > len(self.traversed):
                self.target_square = self.find_closest_safesquare()
                return self.go_to(self.target_square)
            self.stenchsquares.add((self.x, self.y))
            adjsquares = [(self.x - 1, self.y), (self.x + 1, self.y), (self.x, self.y - 1), (self.x, self.y + 1)]
            for sqr in adjsquares:
                if sqr not in self.safesquares and sqr not in self.no_wumpus_sqrs and not self.wumpus_pos_known:
                    self.possible_wumpus_pos.add(sqr)
            self.update_wumpus_loc()
            if len(self.stenchsquares) == 2 and not self.wumpus_pos_known:
                xs = list(self.stenchsquares)
                if xs[0][0] == xs[1][0]:
                    self.wumpus_x = xs[0][0]
                    self.wumpus_y = (xs[0][1] + xs[1][1]) / 2
                    self.wumpus_pos_known = True
                    return self.kill_wumpus()
                elif xs[0][1] == xs[1][1]:
                    self.wumpus_x = (xs[0][0] + xs[1][0]) / 2
                    self.wumpus_y = xs[0][1]
                    self.wumpus_pos_known = True
                    return self.kill_wumpus()
                else:
                    self.possible_wumpus_pos = {x for x in adjsquares if (x not in self.safesquares and x in self.possible_wumpus_pos)}
                    self.update_wumpus_loc()

                    # if len(self.possible_wumpus_pos) == 2:
                    #     # maybe wrong code, change later
                    #     self.last_action == "SHOOT"
                    #     return Agent.Action.SHOOT
                    # else:
                    #     return self.kill_wumpus()

            # if len(self.possible_wumpus_pos) == 2:
            #     # maybe wrong code, change later
            #     self.last_action == "SHOOT"
            #     return Agent.Action.SHOOT
            #
            # if self.wumpus_pos_known and not self.wumpus_dead:
            #     return self.kill_wumpus()



        # if there is a breeze
        if breeze:

            self.breezesquares.add((self.x, self.y))
            adjsquares = [(self.x - 1, self.y), (self.x + 1, self.y), (self.x, self.y - 1), (self.x, self.y + 1)]
            for sqr in adjsquares:
                if sqr not in self.safesquares:
                    self.possiblepits.add(sqr)
            self.update_pit_locs()

            self.breeze_possible_pits_dic[(self.x, self.y)] = {s for s in adjsquares if s not in self.safesquares}
            self.update_breeze_pits_dic()

            if len(self.safesquares) > len(self.traversed):
                self.target_square = self.find_closest_safesquare()
                return self.go_to(self.target_square)

            ### REPLACE LATER ###
            self.escape_mode = True
            ### REPLACE LATER ###




        # if it is time to escape
        if self.escape_mode:
            return self.go_exit()



        # do checks at boundary
        self.update_safesquares()
        if self.direction == "left":
            if self.x == 1:
                if len(self.safesquares) > len(self.traversed):
                    self.target_square = self.find_closest_safesquare()
                    return self.go_to(self.target_square)

        if self.direction == "up":
            if self.world_Y is not None and self.y == self.world_Y:
                if len(self.safesquares) > len(self.traversed):
                    self.target_square = self.find_closest_safesquare()
                    return self.go_to(self.target_square)

        if self.direction == "right":
            if self.world_X is not None and self.x == self.world_X:
                if len(self.safesquares) > len(self.traversed):
                    self.target_square = self.find_closest_safesquare()
                    return self.go_to(self.target_square)

        if self.direction == "down":
            if self.y == 1:
                if len(self.safesquares) > len(self.traversed):
                    self.target_square = self.find_closest_safesquare()
                    return self.go_to(self.target_square)



        # if safe, update safesquares
        if not breeze and not stench:
            self.update_safesquares()



        # DEBUG PRINT INFO #
        # print("\ncurrent spot: " + str((self.x, self.y)))
        # print("traversed: " + str(self.traversed))
        # print("safesquares: " + str(self.safesquares))
        # print("possible wumpus squares: " + str(self.possible_wumpus_pos))
        # print("stench squares: " + str(self.stenchsquares))
        # print("possible pits: " + str(self.possiblepits))
        # print("breeze pits dic: " + str(self.breeze_possible_pits_dic))
        # print("pits: " + str(self.pits) + "\n")


        ### REPLACE LATER ###
        if len(self.traversed) == len(self.safesquares):
            if self.x == 1 and self.y == 1:
                return Agent.Action.CLIMB
            return self.go_to((1, 1))
        ### REPLACE LATER ###


        # move forward
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
                self.last_action = "FORWARD"
                return Agent.Action.FORWARD

        if self.y < next_square[1]:
            if self.direction == "left":
                self.direction = "up"
                self.last_action = "TURN_RIGHT"
                return Agent.Action.TURN_RIGHT
            elif self.direction == "up":
                del path[0]
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




    # uses breadth-first search to return a list of the shortest path to destination from origin with the possible paths
    def bfs(self, paths, origin: tuple, destination: tuple):

        graph = {}
        final_path = []
        frontier = []
        visited = set()

        if origin != destination:
            frontier.append(origin)

        while len(frontier) != 0:
            sqr = frontier.pop(0)
            visited.add(sqr)
            adjsquares = [(sqr[0] - 1, sqr[1]), (sqr[0] + 1, sqr[1]), (sqr[0], sqr[1] - 1), (sqr[0], sqr[1] + 1)]
            to_search = [s for s in adjsquares if s in paths and s not in visited]
            for s in to_search:
                graph[s] = sqr
                frontier.append(s)
                if s == destination:
                    currentsqr = s
                    while currentsqr != origin:
                        final_path.append(currentsqr)
                        currentsqr = graph[currentsqr]
                    final_path.reverse()
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





    # check if there is a shorter way back home
    def shorten_homepath(self):
        path = self.bfs(self.safesquares, (self.x, self.y), (1, 1))
        path.reverse()
        self.way_back_home = path




    # update only boundaries of safesquares
    def update_safesquares_boundary(self):
        if self.x == 1:
            self.safesquares = {s for s in self.safesquares if s[0] > 0}
        if self.world_X is not None and self.x == self.world_X:
            self.safesquares = {s for s in self.safesquares if s[0] < self.world_X + 1}
        if self.y == 1:
            self.safesquares = {s for s in self.safesquares if s[1] > 0}
        if self.world_Y is not None and self.y == self.world_Y:
            self.safesquares = {s for s in self.safesquares if s[1] < self.world_Y + 1}




    # update safesquares if no dangerous percepts
    def update_safesquares(self):
        adjsquares = [(self.x - 1, self.y), (self.x + 1, self.y), (self.x, self.y - 1), (self.x, self.y + 1)]
        for sqr in adjsquares:
            self.safesquares.add(sqr)
        self.update_safesquares_boundary()
        # if self.x == 1:
        #     self.safesquares = {s for s in self.safesquares if s[0] > 0}
        # if self.world_X is not None and self.x == self.world_X:
        #     self.safesquares = {s for s in self.safesquares if s[0] < self.world_X + 1}
        # if self.y == 1:
        #     self.safesquares = {s for s in self.safesquares if s[1] > 0}
        # if self.world_Y is not None and self.y == self.world_Y:
        #     self.safesquares = {s for s in self.safesquares if s[1] < self.world_Y + 1}




    # fix possible pit locations after knowing boundary
    def update_pit_locs(self):
        if self.x == 1:
            self.possiblepits = {s for s in self.possiblepits if s[0] > 0}
        if self.world_X is not None and self.x == self.world_X:
            self.possiblepits = {s for s in self.possiblepits if s[0] < self.world_X + 1}
        if self.y == 1:
            self.possiblepits = {s for s in self.possiblepits if s[1] > 0}
        if self.world_Y is not None and self.y == self.world_Y:
            self.possiblepits = {s for s in self.possiblepits if s[1] < self.world_Y + 1}
        self.possiblepits = {s for s in self.possiblepits if s not in self.safesquares}



    # update breeze to pits dictionary
    def update_breeze_pits_dic(self):
        for k in self.breeze_possible_pits_dic:
            if self.x == 1:
                self.breeze_possible_pits_dic[k] = {s for s in self.breeze_possible_pits_dic[k] if s[0] > 0}
            if self.world_X is not None and self.x == self.world_X:
                self.breeze_possible_pits_dic[k] = {s for s in self.breeze_possible_pits_dic[k] if s[0] < self.world_X + 1}
            if self.y == 1:
                self.breeze_possible_pits_dic[k] = {s for s in self.breeze_possible_pits_dic[k] if s[1] > 0}
            if self.world_Y is not None and self.y == self.world_Y:
                self.breeze_possible_pits_dic[k] = {s for s in self.breeze_possible_pits_dic[k] if s[1] < self.world_Y + 1}
            self.breeze_possible_pits_dic[k] = {s for s in self.breeze_possible_pits_dic[k] if s not in self.safesquares}
            if len(self.breeze_possible_pits_dic[k]) == 1:
                for sqr in self.breeze_possible_pits_dic[k]:
                    self.pits.add(sqr)



    # fix possible wumpus locations after knowing boundary
    def update_wumpus_loc(self):
        if self.x == 1:
            self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[0] > 0}
        if self.world_X is not None and self.x == self.world_X:
            self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[0] < self.world_X + 1}
        if self.y == 1:
            self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[1] > 0}
        if self.world_Y is not None and self.y == self.world_Y:
            self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if s[1] < self.world_Y + 1}
        self.possible_wumpus_pos = {s for s in self.possible_wumpus_pos if (s not in self.safesquares and s not in self.no_wumpus_sqrs)}
        if len(self.possible_wumpus_pos) == 1:
            xs = list(self.possible_wumpus_pos)
            self.wumpus_x = xs[0][0]
            self.wumpus_y = xs[0][1]
            self.wumpus_pos_known = True




    # go kill the wumpus if its position is known
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
                return Agent.Action.SHOOT

        if self.y < y:
            if self.direction == "left":
                self.direction = "up"
                self.last_action = "TURN_RIGHT"
                return Agent.Action.TURN_RIGHT
            elif self.direction == "up":
                return Agent.Action.SHOOT
            elif self.direction == "right":
                self.direction = "up"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT
            else:
                self.direction = "right"
                self.last_action = "TURN_LEFT"
                return Agent.Action.TURN_LEFT



    # update target square
    def update_target(self):
        if self.target_square is not None:
            if self.target_square not in self.safesquares:
                self.target_square = None




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
