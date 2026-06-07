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

    
where I left off: loading config behavior for evolution mode (probably shouldn't have an [l] option to load configs, asking on startup actually makes more sense)


