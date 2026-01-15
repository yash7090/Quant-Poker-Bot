The Poker Bot
A quantitative poker agent that employs advanced simulations and expected value analysis to play a three-card poker variant optimally.

Project Overview
This project is a poker bot designed to operate in a game of incomplete information. The primary goal was to create an agent that makes mathematically optimal decisions 
by relying on statistical models and game theory principles rather than human intuition. The solution is built around a stochastic probability engine and an expected value 
framework to determine optimal actions (Fold, Call, Raise) in real time.

Table of Contents
•Features
•Technical Methodology
•Installation & Usage
•Code Structure

Features
•Stochastic Probability Engine: Uses Monte Carlo simulations to calculate precise win probabilities for all possible opponent hands.
•Expected Value (EV) Analysis: All in-game actions are determined by EV-based decision thresholds derived from the game's payoff matrix.
•Robust Logic: Implements precise tie-breaker rules for various poker hands, handling complex edge cases like low straights (A-2-3) vs. high straights (Q-K-A).
•Risk Management: Features dynamic strategy adjustments in end-game scenarios (e.g., protecting a lead or maximizing variance when trailing).

Technical Methodology
The bot's intelligence is divided into three core components:
1. The Quant Engine (Probability & Simulation)
•Problem: Poker is a game of incomplete information; opponent cards are unknown.
•Solution: A Monte Carlo simulation is used to generate every possible unknown card combination (using itertools.combinations) and simulate game outcomes to determine a raw P(win) (win probability).

2. The Economist (Expected Value & Thresholds)
•Core Concept: The bot plays based on Expected Value (EV), not "feelings".
•Decision Rule: By solving the EV equation, the bot automatically calls when it has greater than a 25% chance of winning, as this is mathematically "less expensive" than paying the guaranteed -1 point
fold penalty in the long run. Raising is only done when P(win) > 60% to ensure statistical dominance and manage variance.

3. The Strategist (Opponent Profiling & Risk Management)
•Profiling: Opponents are categorized based on observed biases (e.g., "Calling Station," "Scared Player").
•Dynamic Adjustment: The strategy dynamically shifts based on real-time game state and time constraints, such as tightening thresholds when in a significant lead to reduce risk.

Installation & Usage
Prerequisites
•Python 3.x
•Required libraries: json, sys, itertools, random.

Running the Project
1. Clone the repository:
bash
git clone github.com
cd Quant-Poker-Bot

2. Run the main script:
bash
python poker_bot.py

3. The script reads game state from stdin (standard input) as a JSON object and writes the chosen action (FOLD, CALL, or RAISE) to stdout (standard output) as a JSON object.

Code Structure
•poker_bot.py: Main script containing all logic and functions including decide_action.



