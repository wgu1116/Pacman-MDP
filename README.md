# Pacman
Use MDP and python to control pacman
The code that I writed is in mdpAgents.py
You can simply run this in smallGrid by running:
python pacman.py -q -n 25 -p MDPAgent -l smallGrid
-l is shorthand for -layout. -p is shorthand for -pacman. -q runs the game without the interface (making it faster).
And run this in mediumClassic by running:
python pacman.py -q -n 25 -p MDPAgent -l mediumClassic
The -n 25 runs 25 games in a row.
By evaluating my code in 250 games, the winning rate is 0.708 that Pacman could win more than 15 times in every 25 games in smallGrid and the winning rate is 0.563 that Pacman could win more than 10 times in every 25 games in mediumClass.
