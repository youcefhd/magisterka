from pyfis.struct import *
from pyfis.anfis import *


# Tworzenie nowego systemu rozmytego typu TSK
fis = Fis()

for j in range(2):
    # Tworzenie nowego wejścia systemu
    inp = Input()
    for i in range(4):
        # Dodawanie funkcji przynależności
        inp.mem_func.append(BellMemFunc([3.3, 4, -10+i*6.6]))
    # Dodawanie wejścia do systemu
    fis.inputs.append(inp)

for i in range(4):
    for j in range(4):
        # Tworzenie i dodawanie reguł systemu
        rule = Rule([0, 0, 0])
        rule.inputs.append((0, i))
        rule.inputs.append((1, j))
        fis.rules.append(rule)

# Dostrajanie modelu (trzeba zdefiniować dane trenujące)
train(fis, train_data, epochs=30, n=1, num_of_backprops=5)
