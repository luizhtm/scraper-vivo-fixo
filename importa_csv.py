import csv
import time

def limpa_telefones_e_importa_para_csv(cidade):
    # limpa o parametro
    cidade = cidade.strip().lower()
    cidade = cidade.replace(' ', '-')

    file_tel = open('./txt/telefones_{cidade}.txt'.format(cidade=cidade), 'r').read()
    tels = file_tel.split('\n')
    sem_dup = list(set(tels))
    sem_dup_filtrado = [string for string in sem_dup if string != ""]

    total = len(sem_dup_filtrado)
    total_proc_5 = total - 5
    with open('./csv/telefones_vivo_fixo_{cidade}.csv'.format(cidade = cidade), 'w', newline='') as f:
        writer = csv.writer(f)
        i = 0
        while i < total_proc_5:
            writer.writerow([sem_dup_filtrado[i], sem_dup_filtrado[i+1], sem_dup_filtrado[i+2], sem_dup_filtrado[i+3], sem_dup_filtrado[i+4]])
            i += 5

        restantes = total % 5
        pos_restante = total - restantes

        if(restantes == 1):
            writer.writerow([sem_dup_filtrado[pos_restante]])
        elif(restantes == 2):
            writer.writerow([sem_dup_filtrado[pos_restante], sem_dup_filtrado[pos_restante+1]])
        elif(restantes == 3):
            writer.writerow([sem_dup_filtrado[pos_restante], sem_dup_filtrado[pos_restante+1], sem_dup_filtrado[pos_restante+2]])
        elif(restantes == 4):
            writer.writerow([sem_dup_filtrado[pos_restante], sem_dup_filtrado[pos_restante+1], sem_dup_filtrado[pos_restante+2], sem_dup_filtrado[pos_restante+3]])
        elif(restantes == 5):
            writer.writerow([sem_dup_filtrado[pos_restante], sem_dup_filtrado[pos_restante+1], sem_dup_filtrado[pos_restante+2], sem_dup_filtrado[pos_restante+3], sem_dup_filtrado[pos_restante+4]])
        else: # restantes == 0
            pass
    
    print(len(sem_dup_filtrado))