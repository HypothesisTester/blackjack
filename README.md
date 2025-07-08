# Blackjack

A simple Blackjack game featuring both **text-based** (CLI) and **graphical** (Pygame) interfaces. Perfect for practicing basic strategy and card counting.

---

## Features

- **Dual UI modes**:
  - **CLI Version** (`textblackjack.py`): A lightweight, text-based interface for quick gameplay.
  - **Graphical Version** (`blackjack.py`): A visually appealing interface built with Pygame.
- **Card Counting**: Implements the Hi-Lo system for strategic play.
- **Gameplay Mechanics**: Supports multiple players, splitting hands, and doubling down.
- **Chip Management**: Automatic reshuffle and rebuy when chips run low.

---

## 🛠️ Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/HypothesisTester/blackjack.git
   cd blackjack
   ```

2. **Create a Virtual Environment** (optional):

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install pygame
   ```

---

## 🚀 Usage

### Graphical (Pygame) Version

Run the graphical interface:

```bash
python3 blackjack.py
```

### Text (CLI) Version

Run the text-based interface:

```bash
python3 textblackjack.py
```

---

## 🎮 Demo

### Screenshots

#### Pygame UI

![Main Table View](docs/screenshots/pygame_main.png)#### CLI UI

![Text UI Example](docs/screenshots/cli_play.png)---

## 📖 How to Play

1. **Objective**: Get a hand value as close to 21 as possible without going over.
2. **Controls**:
   - **Pygame**: Use mouse clicks to interact with buttons for hitting, standing, splitting, or doubling down.
   - **CLI**: Enter commands (e.g., `hit`, `stand`, `split`, `double`) to play.
3. **Card Counting**: Track the Hi-Lo count displayed in the interface to inform your strategy.

---

## 📜 License

This project is licensed under the MIT License. See the LICENSE file for details.