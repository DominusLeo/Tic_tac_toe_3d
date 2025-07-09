# 3D Tic-Tac-Toe with Advanced AI

A sophisticated 3D Tic-Tac-Toe implementation featuring intelligent AI bots, real-time 3D visualization, and advanced strategic analysis. This project goes beyond traditional Tic-Tac-Toe with multiple difficulty levels, fork detection, and comprehensive game statistics.

## Features

### 🎮 Game Modes
- **Human vs Human**: Traditional two-player mode
- **Human vs Bot**: Single-player against AI (5 difficulty levels)
- **Bot vs Bot**: AI testing and analysis mode
- **Debug Mode**: Automated testing with controllable scenarios

### 🤖 Advanced AI System
- **Level 1**: Random moves with basic win/block detection
- **Level 2**: Line-based strategy with position evaluation  
- **Level 3**: Advanced positioning with weighted line analysis
- **Level 4**: Sophisticated strategy with fork detection and dead point analysis
- **Level 5**: Enhanced version with force move detection and multi-move lookahead

### 🎯 Strategic Features
- **Fork Detection**: Identifies opportunities to create multiple winning threats
- **Dead Point Analysis**: Recognizes strategically critical positions
- **Force Moves**: Detects mandatory moves to prevent immediate loss
- **Gravity Physics**: Optional mode where pieces fall to lowest available position
- **3D Visualization**: Real-time 3D rendering with matplotlib

### 📊 Analytics & Statistics
- **Game Logging**: Comprehensive move recording
- **Performance Tracking**: Win/loss statistics with detailed metrics
- **Bot Analysis**: Performance comparison between different AI levels
- **Strategic Insights**: Fork analysis and position evaluation

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup
1. Clone or download the repository
2. Navigate to the project directory:
   ```bash
   cd Tic_tac_toe_3d
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Dependencies
- `matplotlib`: 3D visualization and plotting
- `numpy`: Mathematical operations and array handling
- `pandas`: Data analysis and statistics
- `sympy`: Geometric calculations
- `tqdm`: Progress bars
- `seaborn`: Statistical visualizations

## Configuration

### Game Settings
Edit `constants.py` to customize game behavior:

```python
class Configs:
    GRAVITY = True          # Enable/disable gravity physics
    SHAPE = 4              # Board size (4x4x4 recommended)
    play_vs_bot = 1        # 0=Human vs Human, 1=Human vs Bot, 2=Bot vs Human
    bot_difficult = 4      # Bot difficulty (1-5)
    second_bot = 0         # Second bot difficulty (for Bot vs Bot)
    debug_mod = False      # Enable debug mode
```

### Visual Settings
- **Colors**: Customize player colors in `stack` dictionary
- **Transparency**: Adjust 3D visualization opacity
- **Sizing**: Configure piece sizes and board dimensions

## How to Play

### Starting the Game
```bash
python game_process.py
```

### Game Controls
- **Make a move**: Enter coordinates in format `xyz` (e.g., `123` for position x=1, y=2, z=3)
- **Exit game**: Type `ex`
- **Cancel last two turns**: Type `c` (undoes both your move and opponent's move)
- **Follow hints**: The game provides guidance in the terminal

### Coordinate System
- **X-axis**: Left to right (1-4)
- **Y-axis**: Front to back (1-4)  
- **Z-axis**: Bottom to top (1-4)
- **Example**: `234` places a piece at position (2, 3, 4)

### Winning Conditions
Connect 4 pieces in a line in any direction:
- **Horizontal**: Same Z-level, straight line
- **Vertical**: Same X,Y coordinates, different Z-levels
- **Diagonal**: Diagonal lines within planes or across 3D space
- **3D Diagonals**: Corner-to-corner through the cube

## Project Structure

### Core Files
- **`game_process.py`**: Main game engine and loop
- **`constants.py`**: Game configuration, rules, and bot settings
- **`bot_utils.py`**: AI logic and strategic analysis
- **`funcs.py`**: Game mechanics and 3D visualization
- **`utils.py`**: Supporting functions and calculations

### Analysis & Testing
- **`explore_scrypts.py`**: Bot performance testing and analysis
- **`generate_winning_lines.py`**: Utility to generate winning combinations
- **`data/leaderboard.csv`**: Game statistics and records
- **`test_data/`**: Saved game states for debugging

## Advanced Features

### AI Strategy Components
- **Line Weight Calculation**: Assigns strategic values to potential winning lines
- **Fork Analysis**: Detects complex multi-line winning opportunities
- **Position Evaluation**: Considers spatial relationships and strategic value
- **Threat Assessment**: Evaluates opponent's potential winning moves

### 3D Visualization
- **Real-time Rendering**: Dynamic board updates as moves are made
- **Customizable Views**: Adjustable perspective and camera angles
- **Visual Effects**: Transparency and sizing based on position
- **Win Visualization**: Highlights winning combinations when game ends

### Game Analysis
- **Move History**: Complete game replay capability
- **Statistical Analysis**: Performance metrics and trend analysis
- **Strategic Insights**: Post-game analysis of critical decisions
- **Bot Comparison**: Head-to-head AI performance evaluation

## Development & Testing

### Running Bot Analysis
```bash
python explore_scrypts.py
```

### Generating Winning Combinations
```bash
python generate_winning_lines.py
```

### Debug Mode
Enable debug mode in `constants.py` for automated testing and analysis.

## Tips for Players

### Strategy Basics
1. **Control the Center**: Center positions offer more winning lines
2. **Watch for Forks**: Look for opportunities to create multiple threats
3. **Block Opponent**: Always block immediate winning threats
4. **Think 3D**: Consider all planes and diagonal possibilities
5. **Use Gravity**: When enabled, plan your moves considering piece physics

### Advanced Tactics
- **Dead Point Control**: Secure strategically important positions early
- **Fork Creation**: Set up multiple winning threats simultaneously
- **Vertical Strategy**: Use the Z-axis for unexpected attacks
- **Corner Control**: Corner positions can be powerful in 3D space

## Contributing

This project demonstrates advanced concepts in:
- **Game AI**: Multi-level strategic thinking
- **3D Graphics**: Real-time visualization with matplotlib
- **Strategic Analysis**: Complex position evaluation
- **Software Architecture**: Modular design with clear separation of concerns

## License

This project is open source and available for educational and research purposes.

---

*Developed by Lev & Leo - A sophisticated implementation of 3D Tic-Tac-Toe with advanced AI capabilities*
