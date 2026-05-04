# Hashed Maze
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

def calculate_force(pass_: str) -> int:
    if not pass_:
        return 0
    score = 0
    if len(pass_) >= 8:
        score += 25
    if len(pass_) >= 12:
        score += 25
    if any(c.isupper() for c in pass_):
        score += 15
    if any(c.isdigit() for c in pass_):
        score += 15
    if any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in pass_):
        score += 20
    return score