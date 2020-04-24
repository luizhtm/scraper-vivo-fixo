import requests
import urllib.parse
import time
from bs4 import BeautifulSoup

def pega_ruas(cidade):
    # limpa o parametro
    cidade = cidade.strip().lower()
    cidade = cidade.replace(' ', '+')

    lista_ruas = []
    maximo_paginas = 1000
    for i in range(1, maximo_paginas):
        url = "https://cep.guiamais.com.br/busca/{cidade}-sp?page={i}".format(cidade=cidade, i=i)
        response = requests.get(url)

        if response.status_code == 404:
            break

        doc = BeautifulSoup(response.text, "html.parser")
        table = doc.table
        a_table = table.findAll('a')

        for i in range(0, len(a_table), 5):
            rua = a_table[i].text.strip()
            lista_ruas.append(rua)

        time.sleep(0.2)
    
    sem_rep = list(set(lista_ruas))
    sem_rep_filtrado = [string for string in sem_rep if string != ""]

    return sem_rep_filtrado