# Wumpus-World
AI for Wumpus World Competition

AI Search Algorithm:
1) finds safe adjacent squares and adds it to set of safesquares, updating other info if needed
2) finds nearest unvisited safesquare and travels to it with optimised BFS, reducing number of turns/points needed, updating other info if needed
3) when all safesquares have been visited, AI looks up probability table that it calculates and keeps track of and extracts a list of all squares that are safe to a certain threshold that we calibrate, then travels to the safest one, otherwise exits if there are none considered safe enough
4) explore until considered too dangerous or finds gold or dies

AI Wumpus Killing/Avoiding Algorithm:
1) if wumpus position known, kill it
2) on first turn, if there is a stench, just shoot to see if wumpus dies, in every other scenario, we can always either confirm the position of the wumpus or disregard the wumpus
