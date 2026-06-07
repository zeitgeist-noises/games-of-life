# Games of Life

Games of Life is a python application that began with a curiousity for John Conway's [Game of Life](https://playgameoflife.com/). It is really magical that from such simple rules such beautiful complexity can emerge. It got me wondering what happens if one generalizes the notion of the game of life to arbitrary 2D cellular automata. What if you experiment with different kernel shapes? What about different dead-or-alive rules? As it turns out, most random configurations devolve into noise very quickly, and it is hard to intentionally design a set of rules that yields interesting results. Games of Life makes finding cool cellular automata easy by generating several slightly mutated rules, letting you choose your favorite, and repeating the process.

## Install and Set-up

1. Ensure you have Python installed (any recent version should work)

2. Clone the repository:
    
    `git clone https://github.com/zeitgeist-noises/games-of-life.git
    cd games-of-life`

3. If you want to keep dependencies clean, make a virtual environment:

    `python -m venv .venv
    source .venv/bin/activate   # linux/macos
    .venv/Scripts/Activate.ps1  # windows`

4. Install dependencies:

    `pip install --upgrade pip   # update first
    pip install -r requirements.txt`

5. Run the app :D

    `python main.py`
