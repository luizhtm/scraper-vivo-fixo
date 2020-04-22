import requests
import urllib.parse
import math
import sys
import time
from selenium import webdriver
from get_ruas import pega_ruas
from importa_csv import limpa_telefones_e_importa_para_csv

# O driver varia de acordo com o OS...
# Versões desatualizadas também não vão funcionar então baixe na hora de usar.
chromedriver_location = "C:\\chromedriver"

street_file = open('./txt/ruas.txt', 'r')
street_texto = street_file.read()
street_list = street_texto.split('\n')
street_list = [string for string in street_list if string != ""]

cidade = ''

file_telefones = open("./txt/telefones.txt", "a")
file_nomes = open("./txt/nomes.txt", "a")

if(len(street_list) == 0):
    street_file.close()

    print("O arquivo de ruas esta vazio...")
    cidade = input("Digite o nome da cidade: ").strip()
    print("Populando o arquivo com as ruas da cidade...")
    pega_ruas(cidade)
    
    street_texto = open('./txt/ruas.txt', 'r').read()
    street_list = street_texto.split('\n')
    street_list = [string for string in street_list if string != ""]

    file_telefones.close()
    file_nomes.close()

    file_telefones = open("./txt/telefones.txt", "w")
    file_nomes = open("./txt/nomes.txt", "w")
else:
    print("Encontrei ruas no ruas.txt")
    resposta = input("Quer limpar o arquivo e pegar ruas novamente? (S/n)\n").strip().lower()
    if(resposta == 's'):
        street_file.close()

        cidade = input("Digite o nome da cidade: ").strip()
        print("Populando o arquivo com as ruas da cidade...")
        pega_ruas(cidade)

        street_texto = open('./txt/ruas.txt', 'r').read()
        street_list = street_texto.split('\n')
        street_list = [string for string in street_list if string != ""]

        file_telefones.close()
        file_nomes.close()

        file_telefones = open("./txt/telefones.txt", "w")
        file_nomes = open("./txt/nomes.txt", "w")
    else:
        cidade = input("Digite o nome da cidade: ").strip()

opts = webdriver.chrome.options.Options()
#opts.headless = True
opts.add_argument('log-level=3') # so mostra erros graves no terminal

url = "https://meuvivofixo.vivo.com.br/servlet/Satellite?c=Page&cid=1382552299186&pagename=MeuVivoFixo%2FPage%2FTemplateGlobalAreaAberta"
driver = webdriver.Chrome(options=opts, executable_path=chromedriver_location)
driver.implicitly_wait(10)
driver.get(url)

numero_inicial = 1

for street in street_list:
    print(street)
    
    repete = False

    xpath_campo_endereco = '//*[@id="LOGRADOURO_ASSINANTE"]'
    xpath_campo_numero = '//*[@id="NUM_LOGR_ASSINANTE"]'
    xpath_campo_ate_numero = '//*[@id="NUM_LOGR_ASSINANTE_ATE"]'
    xpath_campo_cidade = '//*[@id="CIDADE_ASSINANTE"]'
    xpath_botao_pesquisar = '//*[@id="btnPesquisar"]/img'
    
    driver.find_element_by_xpath(xpath_campo_endereco).send_keys(street)
    driver.find_element_by_xpath(xpath_campo_numero).send_keys("{num}".format(num=numero_inicial))
    driver.find_element_by_xpath(xpath_campo_ate_numero).send_keys("99999")
    driver.find_element_by_xpath(xpath_campo_cidade).send_keys(cidade)

    driver.find_element_by_xpath(xpath_botao_pesquisar).click()

    xpath_quantidade_resultados = '//*[@id="formWCSVivo"]/div/p'

    tentativas_maxima = 10
    for i in range(tentativas_maxima):
        try:
            texto_quantidade = driver.find_element_by_xpath(xpath_quantidade_resultados).text
        except:
            time.sleep(0.2)
            try:
                xpath_botao_ok = '//*[@id="btnOK"]/span'
                driver.find_element_by_xpath(xpath_botao_ok).click()
            except:
                continue
            else:
                driver.find_element_by_xpath(xpath_botao_pesquisar).click()
                break
        else:
            break

    time.sleep(0.2)
    
    texto_quantidade = texto_quantidade.strip()

    if(texto_quantidade == "Nenhum número de telefone foi encontrado. Tente novamente!" or \
        texto_quantidade == "Não foi possível realizar a sua consulta. Por favor, tente novamente."):
        xpath_botao_nova_busca = '//*[@id="btnPesquisar"]/img'
        driver.find_element_by_xpath(xpath_botao_nova_busca).click()
        continue

    if(texto_quantidade == "Foi encontrado apenas 1 Cliente."):
        texto_quantidade_cortado = 1
    elif(texto_quantidade[:20] == "O número de Clientes"):
        texto_quantidade_cortado = 45
        repete = True
    else:
        texto_quantidade_cortado = texto_quantidade[-3:]
        texto_quantidade_cortado = texto_quantidade_cortado.strip(':')
        texto_quantidade_cortado = texto_quantidade_cortado.strip()

    quantidade_resultados = int(texto_quantidade_cortado)
    quantidade_paginas = math.ceil(quantidade_resultados / 15.0)

    for i in range(1, quantidade_paginas):
        for j in range(1, 16):
            xpath_tel = '//*[@id="formWCSVivo"]/table/tbody/tr[{j}]/td/table/tbody/tr[2]/td[1]'.format(j=j)
            xpath_nome = '//*[@id="formWCSVivo"]/table/tbody/tr[{j}]/td/table/tbody/tr[1]/td[1]/strong'.format(j=j)
            tel = driver.find_element_by_xpath(xpath_tel).text
            nome = driver.find_element_by_xpath(xpath_nome).text
            file_telefones.write(tel + '\n')
            file_nomes.write(nome + '\n')
        xpath_botao_prox = '//*[@id="formWCSVivo"]/table/tbody/tr[16]/td/a[{i}]'.format(i=i+1)
        driver.find_element_by_xpath(xpath_botao_prox).click()
    
    restantes = quantidade_resultados % 15
    if restantes == 0:
        restantes = 15

    for i in range(1, restantes + 1):
        xpath_tel = '//*[@id="formWCSVivo"]/table/tbody/tr[{i}]/td/table/tbody/tr[2]/td[1]'.format(i=i)
        xpath_nome = '//*[@id="formWCSVivo"]/table/tbody/tr[{i}]/td/table/tbody/tr[1]/td[1]/strong'.format(i=i)

        tel = driver.find_element_by_xpath(xpath_tel).text
        nome = driver.find_element_by_xpath(xpath_nome).text

        file_telefones.write(tel + '\n')
        file_nomes.write(nome + '\n')

    if(repete):
        xpath_endereco_ultimo_resultado = '//*[@id="formWCSVivo"]/table/tbody/tr[15]/td/table/tbody/tr[1]/td[2]'
        ultimo_endereco = driver.find_element_by_xpath(xpath_endereco_ultimo_resultado).text
        ultimo_endereco_split = ultimo_endereco.split(',')
        try:
            ultimo_numero = int(ultimo_endereco_split[-1].strip())
        except ValueError:
            ultimo_numero = int(ultimo_endereco_split[-1].split('-')[0].strip())
        numero_inicial = ultimo_numero + 1
        street_list.insert(0, street)
    else:
        numero_inicial = 1

    xpath_botao_nova_busca = '//*[@id="btnPesquisar"]/img'
    driver.find_element_by_xpath(xpath_botao_nova_busca).click()

file_telefones.close()
file_nomes.close()

limpa_telefones_e_importa_para_csv(cidade)

# limpa arquivos
file_telefones = open("./txt/telefones.txt", "w")
file_nomes = open("./txt/nomes.txt", "w")
file_ruas = open("./txt/ruas.txt", "w")
file_telefones.close()
file_nomes.close()
file_ruas.close()

driver.quit()