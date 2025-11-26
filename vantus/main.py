import sympy as sp
import random

description_cells = {
    "empty_cell": 0,
    "pit": -1,
    "vantus": -10,
    "wind": -2,
    "stink": -11,
}


class WampusWorld:
    def __init__(self, x, y, probability_of_pit):
        print(x, y, probability_of_pit)
        self.x = x
        self.y = y
        self.probability_of_pit = probability_of_pit
        self.description_cells = description_cells
        self.generation_world(x, y, probability_of_pit)

    def generation_world(self, x, y, probability_of_pit):
        self.world = [[0 for _ in range(self.x)] for _ in range(self.y)]

        for i in range(self.x):
            for j in range(self.y):
                if random.random() < self.probability_of_pit:
                    self.world[i][j] = -1
        placed = False
        for i in range(self.x):
            if placed:
                break
            for j in range(self.y):
                if (self.world[i][j] != -1 and (i != 0 and j != 0)) and (random.random() < self.probability_of_pit + 0, 3):
                    self.world[i][j] = -10
                    placed = True
                    break

        print('\n')
        for row in self.world:
            print(*row)


def main():
    print("Hello from ВАНТУС!")
    x = 4
    y = 4
    probability_of_pit = 0.2
    world = WampusWorld(x,  y, probability_of_pit)


if __name__ == "__main__":
    main()
