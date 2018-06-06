def mosy_score(missense, synonymous):
    try:
        return (missense+1)/(synonymous+1)
    except ZeroDivisionError:
        return None
 
def background_corrected_mosy_score(missense, missense_background, synonymous, synonymous_background):
    try:
        return ((missense+1)/(missense_background+1))/((synonymous+1)/(synonymous_background+1))
    except ZeroDivisionError:
        return None
