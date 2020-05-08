import requests
import urllib.parse
import math
import time
from selenium import webdriver
from get_ruas import pega_ruas
from importa_csv import limpa_telefones_e_importa_para_csv

def main():
    # O driver varia de acordo com o OS...
    # Versões desatualizadas também não vão funcionar então baixe na hora de usar.
    geckodriver_location = "./geckodriver"

    cidade = input("Digite uma cidade (SP): ").strip()

    street_list = pega_ruas(cidade)
    street_list = [string for string in street_list if string != ""]

    opts = webdriver.firefox.options.Options()
    #opts.headless = True
    opts.add_argument('log-level=3') # so mostra erros graves no terminal

    url = "https://meuvivofixo.vivo.com.br/servlet/Satellite?c=Page&cid=1382552299186&pagename=MeuVivoFixo%2FPage%2FTemplateGlobalAreaAberta"
    driver = webdriver.Firefox(options=opts, executable_path=geckodriver_location)
    driver.implicitly_wait(30)
    driver.get(url)

    numero_inicial = 1

    nome_cidade_arquivo = cidade.replace(' ', '-').lower()
    file_telefones = open('./txt/telefones_{cidade}.txt'.format(cidade=nome_cidade_arquivo), 'w')

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

        xpath_quantidade_resultados = '//*[@id="formWCSVivo"]/div/p'

        tentativas_maxima = 5
        redirecionado = False
        for i in range(tentativas_maxima):
            if driver.current_url == 'https://meuvivofixo.vivo.com.br/servlet/null':
                driver.get(url)
                redirecionado = True
                break

            driver.find_element_by_xpath(xpath_botao_pesquisar).click()

            espera = 10
            sucesso = False
            for j in range(espera):
                try:
                    texto_quantidade = driver.find_element_by_xpath(xpath_quantidade_resultados).text
                except:
                    xpath_botao_ok = '//*[@id="btnOK"]/span'
                    try:
                        driver.find_element_by_xpath(xpath_botao_ok).click()
                    except:
                        time.sleep(0.5)
                    else:
                        break
                else:
                    sucesso = True
                    break

            if sucesso:
                break

        if redirecionado:
            street_list.insert(0, street)
            continue
        
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
                tel = driver.find_element_by_xpath(xpath_tel).text
                file_telefones.write(tel + '\n')
            xpath_botao_prox = '//*[@id="formWCSVivo"]/table/tbody/tr[16]/td/a[{i}]'.format(i=i+1)
            driver.find_element_by_xpath(xpath_botao_prox).click()
            time.sleep(1)
        
        restantes = quantidade_resultados % 15
        if restantes == 0:
            restantes = 15

        for i in range(1, restantes + 1):
            xpath_tel = '//*[@id="formWCSVivo"]/table/tbody/tr[{i}]/td/table/tbody/tr[2]/td[1]'.format(i=i)
            tel = driver.find_element_by_xpath(xpath_tel).text
            file_telefones.write(tel + '\n')

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

    limpa_telefones_e_importa_para_csv(cidade)

    driver.quit()

if __name__ == "__main__":
    main()
