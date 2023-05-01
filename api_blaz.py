from tkinter import *
import requests



def buscar_giros():
    ultimas = [[i['color'],i['roll']]for i in requests.get('https://blaze.com/api/roulette_games/recent').json()][:5][::-1]
    return ultimas

def retornar_cor_numero(giros):
    lista = []
    for giro in giros:
        if giro[0] == 1:
            lista.append(['red','white',giro[1]])
        elif giro[0] == 2:
            lista.append(['black','white',giro[1]])
        else:
            lista.append(['white','white','0'])
    return lista

def atualizar():
    dados_blaze = buscar_giros()
    info = retornar_cor_numero(dados_blaze)
    n1['text'] = info[0][2]
    n2['text'] = info[1][2]
    n3['text'] = info[2][2]
    n4['text'] = info[3][2]
    n5['text'] = info[4][2]

    n1['bg'] = info[0][0]
    n2['bg'] = info[1][0]
    n3['bg'] = info[2][0]
    n4['bg'] = info[3][0]
    n5['bg'] = info[4][0]

    cor_prev = ''
    if sum([num[1] for num in dados_blaze])%2 == 0:
        cor_prev = 'black'
    else:
        cor_prev = 'red'
    previsao = Label(height=2,width=96,bg=cor_prev)
    previsao.grid(row=3,column=0,columnspan=5)




tela = Tk()
tela.resizable(False,False)
tela.title('Bot')
mensagem = Label(text= 'Giros Double Blaze',bg='blue',fg='white',height=2,font=('',12),width=96)
mensagem.grid(row=0,column=0,columnspan=5)
n1 = Label(text='',bg='gray',fg='white',height=5,width=15,font=('',15))
n2 = Label(text='',bg='gray',fg='white',height=5,width=15,font=('',15))
n3 = Label(text='',bg='gray',fg='white',height=5,width=15,font=('',15))
n4 = Label(text='',bg='gray',fg='white',height=5,width=15,font=('',15))
n5 = Label(text='',bg='gray',fg='white',height=5,width=15,font=('',15))

n1.grid(row=1,column=0)
n2.grid(row=1,column=1)
n3.grid(row=1,column=2)
n4.grid(row=1,column=3)
n5.grid(row=1,column=4)

btn = Button(text='Atualizar',height=2,width=96,font=('',12),command=atualizar)
btn.grid(row=2,column=0,columnspan=5)
#
