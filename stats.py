import random

def getOCStats(maxtotal = 40):
    stats = {
        "Agility": 0,
        "Speed": 0,
        "Strength": 0,
        "Defense": 0,
        "Evasiveness": 0,
        "Dexterity": 0,
        "Intelligence": 0,
        "Skill": 0
    }

    # Some OCs can't have maxtotal for stats, so some will have decrease
    randDecrease = int(abs(round(random.gauss(2, 2))))
    # Making sure randDecrease is in the correct range
    randDecrease = randDecrease if randDecrease >= 0 else 0
    randDecrease = randDecrease if randDecrease <= maxtotal else maxtotal
    # Then apply the decrease
    maxtotal -= randDecrease

    # Just give random stats at first
    for k in stats:
        stats[k] = random.uniform(0,10)
    # Now scale to the maximum total
    statsSum = sum(stats.values())
    for k in stats:
        stats[k] = int(min([10,round(stats[k] / statsSum * (maxtotal - 0.5))]))

    return stats
