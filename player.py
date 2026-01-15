import json
import sys
import itertools
import random
from typing import List, Tuple

# 1. HELPER FUNCTIONS
# =============================================================================

RANKS = "23456789TJQKA"
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANKS)}

def parse_card(card_str: str) -> Tuple[int, str]:
    return RANK_VALUE[card_str[0]], card_str[1]

def is_straight_3(rank_values: List[int]) -> Tuple[bool, int]:
    r = sorted(rank_values)
    if r[0] + 1 == r[1] and r[1] + 1 == r[2]: return True, r[2]
    if set(r) == {14, 2, 3}: return True, 3
    return False, 0

def hand_category(hole: List[str], table: str) -> int:
    cards = hole + [table]
    rank_values, suits = zip(*[parse_card(c) for c in cards])
    flush = len(set(suits)) == 1
    counts = {}
    for v in rank_values: counts[v] = counts.get(v, 0) + 1
    straight, _ = is_straight_3(list(rank_values))
    
    if straight and flush: return 5
    if 3 in counts.values(): return 4
    if straight: return 3
    if flush: return 2
    if 2 in counts.values(): return 1
    return 0

# 2. DECIDE_ACTION
# =============================================================================

def decide_action(state: dict) -> str:
    # --- A. State Parsing ---
    hole = state.get("your_hole", [])       
    table = state.get("table_card", "")     
    if not hole or not table: return "FOLD"

    opp_stats = state.get("opponent_stats", {})
    my_pts = state.get("your_points", 0)
    opp_pts = state.get("opponent_points", 0)

    # B. Monte Carlo Simulation 
    suits = "CDHS"
    full_deck = [r + s for r in RANKS for s in suits]  
    known_cards = set(hole + [table])
    unknown_cards = [c for c in full_deck if c not in known_cards]

    wins, ties, total = 0, 0, 0
    my_cat = hand_category(hole, table)
    my_vals = [parse_card(c)[0] for c in hole + [table]]

    def get_pair_score(vals):
        counts = {x: vals.count(x) for x in vals}
        pair = next((k for k, v in counts.items() if v == 2), 0)
        kicker = next((k for k, v in counts.items() if v == 1), 0)
        return (pair, kicker)
    
    def get_straight_high(vals):
        if set(vals) == {14, 2, 3}: return 3
        return max(vals)

    # Simulation Loop
    for opp_hole_tuple in itertools.combinations(unknown_cards, 2):
        opp_hole = list(opp_hole_tuple)
        opp_cat = hand_category(opp_hole, table)
        
        if my_cat > opp_cat: 
            wins += 1
        elif my_cat < opp_cat: 
            pass
        else:
            # Tie-Breaker
            opp_vals = [parse_card(c)[0] for c in opp_hole + [table]]
            
            player_won = False
            is_tie = False
            
            if my_cat == 4: # Trips
                if my_vals[0] > opp_vals[0]: player_won = True
                elif my_vals[0] == opp_vals[0]: is_tie = True
            elif my_cat == 1: # Pair
                ms, os = get_pair_score(my_vals), get_pair_score(opp_vals)
                if ms > os: player_won = True
                elif ms == os: is_tie = True
            elif my_cat in [3, 5]: # Straight
                mh, oh = get_straight_high(my_vals), get_straight_high(opp_vals)
                if mh > oh: player_won = True
                elif mh == oh: is_tie = True
            else: # High Card / Flush
                if sorted(my_vals, reverse=True) > sorted(opp_vals, reverse=True): player_won = True
                elif sorted(my_vals, reverse=True) == sorted(opp_vals, reverse=True): is_tie = True
            
            if player_won: wins += 1
            elif is_tie: ties += 1
            
        total += 1

    p_win = (wins + 0.5 * ties) / total if total > 0 else 0.5

    # C.Thresholds
    # EV Calculation: Calling (-2 loss / +2 win) is better than Folding (-1) if P(Win) > 26%
    raise_threshold = 0.60
    call_threshold = 0.26 

    # D.Opponent Strategy 
    folds = opp_stats.get("fold", 0)
    calls = opp_stats.get("call", 0)
    raises = opp_stats.get("raise", 0)
    total_actions = folds + calls + raises

    if total_actions > 20:
        fold_rate = folds / total_actions
        call_rate = calls / total_actions
        raise_rate = raises / total_actions
        
        # 1.Check for Dummy Bots (Calling Stations)
        is_calling_station = (call_rate > 0.20) 
        
        if not is_calling_station:
            # 2. THE BULLY: Exploit Scared Players
            if fold_rate > 0.50:
                raise_threshold -= 0.15 # Bluff more
                # Semi-Bluff Logic
                if 0.40 <= p_win <= 0.50:
                    if random.random() < 0.20:
                        return "RAISE"

        # 3.SHIELD: Defend against Maniacs
        if raise_rate > 0.40:
            raise_threshold += 0.10 # Tighten up
            call_threshold += 0.05  # Don't call with trash

            # 4. THE TRAP: Slow Play Monster Hands
            if p_win > 0.92 and random.random() < 0.20:
                return "CALL"

    # E. End-Game Management 
    # Only active in the final ~50 rounds 
    if total_actions > 950: 
        score_diff = my_pts - opp_pts
        
        # Protect Lead
        if score_diff > 40:
            raise_threshold += 0.10
            call_threshold = 0.26
            
        # Chase Deficit
        elif score_diff < -20:
            raise_threshold -= 0.20 # Max Variance
            call_threshold -= 0.15

    #F. Execution -
    noise = random.uniform(-0.01, 0.01)
    if p_win >= (raise_threshold + noise):
        return "RAISE"
    elif p_win >= (call_threshold + noise):
        return "CALL"
    else:
        return "FOLD"


# 3. I/O LOOP 
# =============================================================================

def main():
    try:
        raw = sys.stdin.read().strip()
        state = json.loads(raw) if raw else {}
        action = decide_action(state)
        sys.stdout.write(json.dumps({"action": action}))
    except:
        sys.stdout.write(json.dumps({"action": "FOLD"}))

if __name__ == "__main__":
    main()