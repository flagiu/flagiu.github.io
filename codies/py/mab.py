#!/bin/python

import sys, random

baseMap = [
    ["            A        "],
    ["         /     \\     "],
    ["      /           \\   "],
    ["   /                 \\ "],
    ["F                     B"],
    ["|                     |"],
    ["|                     |"],
    ["|                     |"],
    ["|                     |"],
    ["E                     C"],
    ["   \\                 / "],
    ["     \\             /   "],
    ["       \\         /     "],
    ["         \\     /       "],
    ["            D        "],
]

# slots and player_symbols must all differ!
slots = ["A", "B", "C", "D", "E", "F"]
# user vs MAB
player_symbols = ["O","X"]

# strategy 0: you want to put three adiacent circles,
#  i.e. ABC, EFA or FAB
strategy_goal = {
    0: "Put 3 NON-ADIACENT circles",
    1: "Put 3 ADIACENT circles",
    2: "Put 2 ADIACENT + 1 NON-ADIACENT circles"
}
strategy_winning_conf = {
    0: [f"{slots[0]}{slots[2]}{slots[4]}"],
    1: [
        f"{slots[0]}{slots[1]}{slots[2]}",
        f"{slots[0]}{slots[1]}{slots[-1]}",
        f"{slots[0]}{slots[-2]}{slots[-1]}",
        ],
    2: [
        f"{slots[0]}{slots[1]}{slots[3]}",
        f"{slots[0]}{slots[1]}{slots[-2]}",
        f"{slots[0]}{slots[2]}{slots[3]}",
        f"{slots[0]}{slots[-2]}{slots[-3]}",
        ]
}

def GetNumRounds(nmin=3, nmax=100):
    n = -1
    firstAttempt=True
    question = f"Select number of rounds (between {nmin} and {nmax}): "
    while not n>=nmin and n<=nmax:
        if not firstAttempt:
            print("Please retry.")
        n = int(input(question,))
        firstAttempt=False
    return n

def GetPlayerStrategy():
    strat = -1
    firstAttempt=True
    question = "Select your strategy between {\n"
    for strategy in strategy_goal.keys():
        question += f" {strategy}: {strategy_goal[strategy]}\n"
    question += "}. Which one? "
    while not strat in strategy_goal.keys():
        if not firstAttempt:
            print("Please retry.")
        strat = int(input(question,))
        firstAttempt=False
    return strat

def GetPossibleMoves(conf):
    poss_moves = []
    for el in conf:
        if not el in player_symbols:
            poss_moves.append(el)
    return poss_moves

def GetPlayerMove(conf):
    poss_moves = GetPossibleMoves(conf)
    move = [""]
    firstAttempt=True
    question = "Make your move ( "
    for el in poss_moves:
        question += el+" "
    question += "): "
    while not move in poss_moves:
        if not firstAttempt:
            print("Wrong move. Retry.")
        move = input(question,).upper()
        firstAttempt=False
    return move

def MakeMove(conf, player_i, chosen_slot):
    new_conf = conf.replace(chosen_slot, player_symbols[player_i])
    return new_conf

def TestConfIsValid(conf):
    assert len(conf)==len(slots)
    for i in range(len(slots)):
        assert conf[i]==slots[i] or conf[i] in player_symbols
    return

def TestUserWon(conf, strategy):
    slot_user = "".join([slots[i] for i in range(len(conf)) if conf[i]==player_symbols[0]])
    #print("Slots occupied by user are:",slot_user)
    for el in strategy_winning_conf[strategy]:
        if len(el)==len(slot_user) and "".join(sorted(el)) == "".join(sorted(slot_user)):
            return True
    return False

def TestRoundIsOver(conf, strategy):
    return TestUserWon(conf, strategy) or len(GetPossibleMoves(conf))==0

def displayMap(map, conf):    # Display the current configuration
    for map_row in map:
        map_row = ''.join(map_row)
        for i,slot in enumerate(slots):
            if slot in map_row:
                map_row = map_row.replace(slot, conf[i])
        print(map_row)

def clear_screen():
    print("\033c", end="")

class MAB():
    def __init__(self, other=None):
        if other is not None:
            self.confs = other.confs
            self.move_counters = other.move_counters
            self.moves = other.moves
        else:
            self.confs = []
            self.move_counters = []
            self.moves = []
        return

    def Display(self):
        print("--------------------------------------")
        print("MAB parameters:")
        for i in range(len(self.confs)):
            print("", self.confs[i], *self.move_counters[i])
        print("--------------------------------------")

    def ResetCounter(self, i):
        # start with 1 count for each possible move
        poss_moves = GetPossibleMoves(self.confs[i])
        self.move_counters[i] = [1]*len(poss_moves)
        return

    def AddConf(self, conf):
        self.confs.append(conf)
        self.move_counters.append(None)
        self.ResetCounter(-1)
        return
    
    def ChooseMove(self, conf):
        if not conf in self.confs:
            self.AddConf(conf)
        for i in range(len(self.confs)):
            if self.confs[i]==conf:
                poss_moves = GetPossibleMoves(conf)
                move_counter = self.move_counters[i]
                if len(poss_moves)==0:
                    print("ERROR!")
                    sys.exit(1)
                #cumulative sum
                cumsum = [0]*len(poss_moves)
                for j in range(len(poss_moves)):
                    cumsum[j] += move_counter[j]
                    if j>0:
                        cumsum[j] += cumsum[j-1]
                #random number
                r = random.randint(0,cumsum[-1]-1)
                # choose the move, weighted by its counter
                for j in range(len(poss_moves)):
                    if r<cumsum[j]:
                        move = poss_moves[j]
                        # remember the conf and the move
                        self.moves.append((i,j))
                        #and remove 1 from its counter
                        self.move_counters[i][j] -= 1
                        break
        return move

    def Reward(self, did_MAB_win):
        if did_MAB_win:
            # reward if won, penalize if lost: add 2 or add 0 to the chosen moves (who got -1)
            for i,j in self.moves:
                self.move_counters[i][j] += 2
        #if any conf has empty counters, reset them
        for i in range(len(self.confs)):
            empty=True
            for j in range(len(self.move_counters[i])):
                if self.move_counters[i][j]>0:
                    empty=False
                    break
            if empty:
                self.ResetCounter(i)
        #reset the moves history!
        self.moves = []



if __name__=="__main__":
    clear_screen()
    mab = MAB()
    print("Game Start")
    for i in range(len(player_symbols)):
        print(f" Player {i+1} draws: '{player_symbols[i]}'")
    nrounds = GetNumRounds()
    strategy = GetPlayerStrategy()
    print(f" You chose strategy n.{strategy}: {strategy_goal[strategy]}")
    print(f" Winning configurations are thus:", end='')
    for el in strategy_winning_conf[strategy]:
        print(f" {el}", end='')
    print()
    nwon = 0
    for k in range(nrounds):
        print(f"\n\o/ Round {k+1} of {nrounds} (User: {nwon} | MAB: {k-nwon})")
        # configurations are strings of slots or symbols
        currentConf = "".join(slots)
        # Player 1 (User) starts, always with the moves "A"
        move = slots[0]
        print("Your first move is mandatory: ", move)
        currentConf = MakeMove(currentConf, 0, move)
        displayMap(baseMap, currentConf)
        RoundOver = False
        while not RoundOver:
            # Player 2 (MAB)
            clear_screen()
            progress_bar = '[' + (k+1)*'='+ '>' + (nrounds-k)*'-' + ']'
            print(f"# {progress_bar}")
            print(f"\n# Round {k+1} of {nrounds} (User: {nwon} | MAB: {k-nwon})")
            print(f"#  (Your strategy is n.{strategy}: {strategy_goal[strategy]})")
            move = mab.ChooseMove(currentConf)
            print("MAB's last move was: ", move)
            currentConf = MakeMove(currentConf, 1, move)
            displayMap(baseMap, currentConf)
            RoundOver = TestRoundIsOver(currentConf, strategy)
            if not RoundOver:
                # Player 1 (User)
                move = GetPlayerMove(currentConf)
                print("Your move is: ", move)
                currentConf = MakeMove(currentConf, 0, move)
                displayMap(baseMap, currentConf)
                RoundOver = TestRoundIsOver(currentConf, strategy)
        print("Round is Over")
        UserWon = TestUserWon(currentConf, strategy)
        if UserWon:
            print(" You Won the Round!")
            nwon += 1
        else:
            print(" MAB Won the Round")
        mab.Reward(not UserWon)
        mab.Display()
    print("Game Completed")
    nlost = nrounds-nwon
    print(f" User: {nwon} | MAB: {nlost}")
    if nwon > nlost:
        print(" You Won the Game!")
    elif nwon < nlost:
        print(" MAB Won the Game")
    else:
        print(" No winner...")
