generalized_game_of_life/
│
├── README.md
├── requirements.txt
├── main.py                 # Entry point to run the interactive UI
│
├── engine/
│   ├── __init__.py
│   ├── ca.py               # Cellular Automaton simulation logic
│   └── genome.py           # Genotype definition, mutation, and crossover
│
└── ui/
    ├── __init__.py
    └── interface.py        # Window management, rendering, and user input
