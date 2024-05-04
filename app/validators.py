def is_valid_skill(skill):
    valid_skills = {
        "BJJ",
        "Karate",
        "Judo",
        "KungFu",
        "Capoeira",
        "Boxing",
        "Taekwondo",
        "Aikido",
        "KravMaga",
        "MuayThai",
        "KickBoxing",
        "Pankration",
        "Wrestling",
        "Sambo",
        "Savate",
        "Sumo",
        "Kendo",
        "Hapkido",
        "LutaLivre",
        "WingChu",
        "Ninjutsu",
        "Fencing",
        "ArmWrestling",
        "SuckerPunch",
        "44Magnum",
    }
    return skill in valid_skills


def contains_duplicates(skills):
    skills_set = set(skills)
    return len(skills) != len(skills_set)


def validate_fight_skills(fight_skills):
    if not fight_skills:
        return "Bad Request - Fight skills cannot be empty"

    try:
        if len(fight_skills) > 20:
            return "Bad Request - Fight skills cannot have more than 20 skills"
        if contains_duplicates(fight_skills):
            return "Bad Request - Fight skills contains duplicates"
        if not all(is_valid_skill(skill) for skill in fight_skills):
            return "Bad Request - Invalid fight skill"
    except TypeError:
        return "Bad Request - fight skill is not a string"
    except KeyError:
        return "Bad Request - Invalid fight skill"
    return None
