class Team:
    def __init__(self, pos_and_counts_needed: dict):
        self.needed_pos_counts = pos_and_counts_needed.copy()
        self.current_roster_size = 0
        self.current_pos_counts = {pos: 0 for pos in pos_and_counts_needed.keys()}
        self.score = 0.0
        self.pos_draft_order = list()

    def add_player(self, pos: str, score: float) -> None:
        self.score += score
        self.pos_draft_order.append(f"{pos}")
        self.current_pos_counts[pos] += 1
        self.needed_pos_counts[pos] -= 1
        self.current_roster_size += 1
        if self.needed_pos_counts[pos] == 0:
            del self.needed_pos_counts[pos]
