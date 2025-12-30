def moyenne(notes):
    somme = 0
    for i in range(len(notes)):
        somme = somme + notes[i]
    return somme / i   # BUG ici

notes = [12, 15, 9, 18]
print("La moyenne est :", moyenne(notes))
