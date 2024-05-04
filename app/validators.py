def is_valid_skill(skill):
    valid_skills = {
        "BJJ": True, "Karate": True, "Judo": True, "KungFu": True, "Capoeira": True, "Boxing": True, 
        "Taekwondo": True, "Aikido": True, "KravMaga": True, "MuayThai": True, "KickBoxing": True, 
        "Pankration": True, "Wrestling": True, "Sambo": True, "Savate": True, "Sumo": True, "Kendo": True, 
        "Hapkido": True, "LutaLivre": True, "WingChu": True, "Ninjutsu": True, "Fencing": True, 
        "ArmWrestling": True, "SuckerPunch": True, "44Magnum": True
    }
    return valid_skills.get(skill, False)


def validate_fight_skills(fight_skills):
    if not fight_skills:
        return "Bad Request - Fight skills cannot be empty"
    if len(fight_skills) > 20:
        return "Bad Request - Fight skills cannot have more than 20 skills"
    if not all(is_valid_skill(skill) for skill in fight_skills):
        return "Bad Request - Invalid fight skill"
    return None


