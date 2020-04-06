import requests
import urllib.parse
import time
from bs4 import BeautifulSoup

file_ruas = open("./txt/ruas.txt", 'w')

def pega_ruas(cidade):
    
    # limpa o parametro
    cidade = cidade.strip()
    cidade = cidade.lower()

    url = "https://www.rastreamentocorreios.net/qual_cep/sp/{cidade}".format(cidade=cidade)
    response = requests.get(url)

    print(response)

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.table
    streets_table = table.findAll('a')

    streets_list = []

    for element in streets_table:
        street = element.get_text()
        streets_list.append(street)
        file_ruas.write(street + '\n')

    return streets_list

pega_ruas('salto')