import csv
import time
file_tel = open('./txt/telefones.txt', 'r').read()
tels = file_tel.split('\n')
sem_dup = list(set(tels))
sem_dup_filtrado = [string for string in sem_dup if string != ""]
print(len(sem_dup))

with open('./csv/telefones_vivo_fixo_salto.csv', 'w') as f:
    writer = csv.writer(f)
    for tel in sem_dup_filtrado:
        writer.writerow([tel])