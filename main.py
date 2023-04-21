from xml.etree.ElementPath import get_parent_map
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime, timedelta
from colorama import init, Fore, Back
from time import time
import configparser
import requests
import json
import re
import numpy as np
import pandas as pd

API = IQ_Option('eduardomoura88@outlook.com', '1802Edu0##')
API.connect()
CONNECT = API.connect()
if (CONNECT):
    print('Conectado com sucesso')


# função para pegar o nome dos pares:


def get_pares(API):
    PARES = API.get_all_open_time()
    ARRAY_PARES = []

    for PAR in PARES['digital']:
        if PARES['digital'][PAR]['open'] == True:
            ARRAY_PARES.append(PAR)

    return np.unique(ARRAY_PARES)


def String_Format(string_par):
    format_string = string_par.replace('/', '')
    if re.match('(A-Z){6} {5}', format_string):
        format_string = format_string.split(' ')
        format_string = format_string[0] + '-OTC'
    return format_string

# PEGANDO AS INFORMAÇÕES DE CADA ATIVO DISPONIBILIZADO PELA IQOPTION:


def get_time_atv():
    info_binarias = {}
    info_digitais = {}
    url = 'https://fininfo.iqoption.com/api/graphql'
    arquivo_playload = open('payload_post.txt', 'r')
    reqisicao = requests.post(url, data=arquivo_playload)
    dados = json.loads(reqisicao.text)
    for data in dados['data']['BinaryOptions']:
        if data['type'] == 'Forex' and len(data['schedule']) != 0:
            x = []
            y = {}
            paridade = data['name']
            y['data'] = data['schedule'][0]['from'].split('T')[0]
            y['abertura'] = data['schedule'][0]['from'].split('T')[1].split('-')[0]
            y['fechamento'] = data['schedule'][0]['to'].split('T')[1].split('-')[0]
            x = [y]
            paridade = String_Format(paridade)
            info_binarias[paridade] = x
    for data in dados['data']['DigitalOptions']:
        if data['type'] == 'Forex' and len(data['schedule']) != 0:
            x = []
            y = {}
            paridade = data['name']
            y['data'] = data['schedule'][0]['from'].split('T')[0]
            y['abertura'] = data['schedule'][0]['from'].split('T')[1].split('-')[0]
            y['fechamento'] = data['schedule'][0]['to'].split('T')[1].split('-')[0]
            x = [y]
            paridade = String_Format(paridade)
            info_digitais[paridade] = x
    return info_binarias, info_digitais


def catalogar(par, dias, prct_call, prct_put, timeframe, data_atual):
    data = []
    datas_testadas = []
    time = time()
    sair = False
    analise = {}

    while sair == False:
        velas = API.get_candles(par, (timeframe * 60), 1000, time)
        velas.reverse()
        posicao = 0

        for x in velas:
            if datetime.fromtimestamp(x['from']).strftime('%Y-%m-%d') != data_atual:
                if datetime.fromtimestamp(x['from']).strftime('%Y-%m-%d') not in datas_testadas:
                    datas_testadas.append(datetime.fromtimestamp(
                        x['from']).strftime('%Y-%m-%d'))

                if len(datas_testadas) <= dias:
                    x.update({'cor': 'verde' if x['open'] < x['close']
                             else 'vermelha' if x['open'] > x['close'] else 'doji'})
                    data.append(x)
                else:
                    sair = True
                    break
            posicao += 1
        time = int(velas[posicao - 1]['from'] - 1)

    for velas in data:
        horario = datetime.fromtimestamp(velas['from']).strftime('%H:%M')
        if horario not in analise:
            analise.update({horario: {'verde': 0, 'vermelha': 0, 'doji': 0, '%': 0,
                           'dir': '', 'tendencia': 0, 'contra_verde': 0, 'contra_vermelha': 0}})
        analise[horario][velas['cor']] += 1

        try:
            analise[horario]['%'] = round(((analise[horario]['verde'] * 100) / (
                analise[horario]['verde'] + analise[horario]['vermelha'] + analise[horario]['doji'])), 2)
        except:
            pass

    for horario in analise:
        if analise[horario]['%'] > 86:
            analise[horario]['dir'] = 'CALL'
        elif analise[horario]['%'] < 86:
            analise[horario]['%'], analise[horario]['dir'] = 100 - \
                analise[horario]['%'], 'PUT'

    return analise


if (CONNECT):
    # variaveis para fazer analise:
    CONFIG = {}
    CONFIG['timeframe'] = 15
    CONFIG['days'] = 15
    CONFIG['porcent'] = 86
    CONFIG['martingale'] = 0
    CONFIG['porcent_call'] = abs(CONFIG['porcent'])
    CONFIG['porcent_put'] = abs(100 - CONFIG['porcent'])
    CONFIG['pares'] = get_pares(API)
    CONFIG['time_now'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    CONFIG['info_binarias'], CONFIG['info_digitais'] = API.get_time_atv()

    # iniciando a catalogação:
    CATALOGADOS = {}
    CONTADOR = 1
    catalogar = catalogar()
    for PAR in CONFIG['pares']:
        CATALOGADOS.update({PAR: catalogar(
            PAR, CONFIG['days'], CONFIG['percent_call'], CONFIG['percent_put'], CONFIG['timeframe'], CONFIG['time_now'])})

        # verificando cada vela de par para analise:
        for par in CATALOGADOS:
            for horario in sorted(CATALOGADOS[par]):
                if CONFIG['martingale'] != 0:

                    rg_time = horario
                    soma = {'verde': CATALOGADOS[par][horario]['verde'], 'vermelha': CATALOGADOS[par]
                            [horario]['vermelha'], 'doji': CATALOGADOS[par][horario]['doji']}
                    for i in range(CONFIG['martingale']):
                        CATALOGADOS[par][horario].update(
                            {'mg' + str(i + 1): {'verde': 0, 'vermelha': 0, 'doji': 0, '%': 0}})
                        rg_time = str(datetime.strptime((datetime.now().strftime(
                            '%Y-%m-%d') + str(rg_time), '%Y-%m-%d%H:%M:%S') + timedelta(minutes=CONFIG['timeframe'])))
                        if rg_time in CATALOGADOS[par]:
                            CATALOGADOS[par][horario]['mg' + str(
                                i + 1)]['verde'] += CATALOGADOS[par][rg_time]['verde'] + soma['verde']
                            CATALOGADOS[par][horario]['mg' + str(
                                i + 1)]['vermelha'] += CATALOGADOS[par][rg_time]['vermelha'] + soma['vermelha']
                            CATALOGADOS[par][horario]['mg'
                                                      + str(i + 1)]['doji'] += CATALOGADOS[par][rg_time]['doji'] + soma['doji']

                            CATALOGADOS[par][horario]['mg' + str(i + 1)]['%'] = (CATALOGADOS[par][horario]['mg' + str(i + 1)]['verde'] / (CATALOGADOS[par][horario]['mg' + str(
                                i + 1)]['verde'] + CATALOGADOS[par][horario]['mg' + str(i + 1)]['vermelha'] + CATALOGADOS[par][horario]['mg' + str(i + 1)]['doji'])) * 100
                            soma['verde'] += CATALOGADOS[par][horario][rg_time]['verde']
                            soma['vermelha'] += CATALOGADOS[par][horario][rg_time]['vermelha']
                            soma['doji'] += CATALOGADOS[par][horario][rg_time]['doji']
                        else:
                            CATALOGADOS[par][horario]['mg' + str(i + 1)]['%'] = 0
        CONTADOR += 1
    print(json.dumps(CATALOGADOS, indent=1))
else:
    print('Não foi possivel conectar a API')
API.disconnect()
