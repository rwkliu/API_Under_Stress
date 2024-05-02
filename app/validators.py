def is_valid_skill(skill):
    valid_skills = ["BJJ", "Karate", "Judo", "KungFu", "Capoeira", "Boxing", "Taekwondo", "Aikido", "KravMaga",
                    "MuayThai", "KickBoxing", "Pankration", "Wrestling", "Sambo", "Savate", "Sumo", "Kendo",
                    "Hapkido", "LutaLivre", "WingChu", "Ninjutsu", "Fencing", "ArmWrestling", "SuckerPunch",
                    "44Magnum"]
    return skill in valid_skills


def validate_fight_skills(fight_skills):
    if not all(is_valid_skill(skill) for skill in fight_skills):
        return "Bad Request - Invalid fight skill"
    if not fight_skills:
        return "Bad Request - Fight skills cannot be empty"
    if len(fight_skills) > 20:
        return "Bad Request - Fight skills cannot have more than 20 skills"
    return None
