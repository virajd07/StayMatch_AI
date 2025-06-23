def calculate_pg_score(food, room, safety, rent):
    rent_score = 10 if rent <= 5000 else 8 if rent <= 8000 else 5
    return round((food + room + safety + rent_score) / 4, 2)
