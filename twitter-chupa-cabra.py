#! /usr/bin/python
# -*- coding: utf-8 -*-

import twitter
import pycurl
import StringIO
import simplejson
import settings

def get_api():
    
    api = twitter.Api(consumer_key=settings.CONSUMER_KEY, 
                      consumer_secret=settings.CONSUMER_SECRET, 
                      access_token_key=settings.ACCESS_TOKEN_KEY, 
                      access_token_secret=settings.ACCESS_TOKEN_SECRET)
    
    return api

def get_followers_ids(user_id, cursor=-1):
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, 'http://api.twitter.com/1/followers/ids.json?user_id=%s&cursor=%s' % (user_id, cursor))
    content_io = StringIO.StringIO()
    curl.setopt(pycurl.WRITEFUNCTION, content_io.write)
    curl.perform()
    response = content_io.getvalue()
    response_dict = simplejson.loads(response)
    curl.close()
    return response_dict

def chk_friendships_exists(user_id_a, user_id_b):
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, 'http://api.twitter.com/1/friendships/exists.json?user_id_a=%s&user_id_b=%s' % (user_id_a, user_id_b))
    content_io = StringIO.StringIO()
    curl.setopt(pycurl.WRITEFUNCTION, content_io.write)
    curl.perform()
    response = content_io.getvalue()
    response_dict = simplejson.loads(response)
    curl.close()
    return response_dict

def do_whitelist(api):
    print
    
    contador = 0
    
    friends = api.GetFriends(settings.USER)
    
    f = open('whitelist.txt', 'w')

    f.write('#comentario\n')

    while (friends):
        
        for user in friends:
            contador = contador + 1
            
            f.write('%s\n' % user.screen_name)
            
            print '%s - Whitelist (%s)' % (contador, user.screen_name)

        else:
            friends = api.GetFriends(settings.USER)
            
    f.close()

    print
    print 'Total de Whitelist = %s' % contador
    print

def load_whitelist():

    f = open('whitelist.txt', 'r')

    whitelist = []
    
    for line in f:
        line = line.replace('\n', '')
        if not line.startswith('#'):
            if line:
                whitelist.append(line)
            
    f.close()
    
    return whitelist

def do_follow(api):
    qtd = int(raw_input('Quantidade: '))
    pag = int(raw_input('A partir de qual pagina: '))
    seguidores_de = raw_input('Seguir os seguidores de qual usuario: ')
    chk_amizade = int(raw_input('Deseja fazer verificacao de amizade = (1) Sim | (2) Nao: '))

    print

    contador = 0
    seguidos = 0
    
    seguidores_de_user = api.GetUser(seguidores_de)
    
    meu_user = api.GetUser(settings.USER)
    
    followers_dict = get_followers_ids(seguidores_de_user.id)
    
    if not followers_dict.has_key('error'): 
    
        followers_ids = followers_dict['ids']
    
        cursor_ini = pag * qtd - qtd
        cursor_fim = pag * qtd if pag * qtd < len(followers_ids) else len(followers_ids)
        
        for i in range(cursor_ini, cursor_fim):
            contador = contador + 1
            
            if chk_amizade == 1:
                esta_seguindo = chk_friendships_exists(meu_user.id, followers_ids[i])
                
                if isinstance(esta_seguindo, bool):
                    esta_seguindo = str(esta_seguindo)
                else:
                    esta_seguindo = esta_seguindo['error']
            else:
                esta_seguindo = 'False'
            
            if esta_seguindo == 'False':
                try:
                    api.CreateFriendship(followers_ids[i])
        
                    seguidos = seguidos + 1
            
                    print '%s - Follow (%s)' % (contador, followers_ids[i])
                except Exception, e:
                    print '%s - Follow (%s) = ERROR AO TENTAR DAR O FOLLOW!!!!!!' % (contador, followers_ids[i])

            elif esta_seguindo == 'True':
                print '%s - Follow (%s) = Ja esta seguindo!!!' % (contador, followers_ids[i])
                
            elif esta_seguindo == 'Following information is not available for protected users without authentication.':
                print '%s - Follow (%s) = Nao foi possivel fazer verificacao de amizade. Usuario bloqueou sua lista de seguidores!!!' % (contador, followers_ids[i])

            else: 
                print '%s - Follow (%s) = ERROR AO TENTAR FAZER VERIFICACAO DE AMIZADE!!!' % (contador, esta_seguindo)
                continuar_verificando = int(raw_input('Deseja continuar sem verificacao de amizade = (1) Continuar | (2) Parrar: '))
                
                if continuar_verificando == 1:
                    chk_amizade = 2
                else:
                    break

    else:
        print '%s - Follow (%s) = ERROR AO TENTAR RECUPERAR OS FOLLOWERS!!!' % (contador, followers_dict['error'])
        
    print
    print 'Total de Follow = %s' % seguidos
    print

def do_unfollow(api):
    qtd = int(raw_input('Quantidade: '))

    print
    
    whitelist = load_whitelist()
    
    contador = 0
    excluidos = 0
    
    friends = api.GetFriends(settings.USER)

    while (friends and contador < qtd):
        
        for user in friends:
            contador = contador + 1
            
            if user.screen_name not in whitelist:
                try:
                    api.DestroyFriendship(user.id) 
                    
                    excluidos = excluidos + 1
                    
                    print '%s - Unfollow (%s)' % (contador, user.screen_name)
                except Exception, e:
                    print '%s - Unfollow (%s) = ERROR AO TENTAR DAR O UNFOLLOW!!!' % (contador, user.screen_name)
            else:
                print '%s - Whitelist (%s) = WHITELIST!!!' % (contador, user.screen_name)
                        
            if contador == qtd:
                break
        else:
            friends = api.GetFriends(settings.USER)

    print
    print 'Total de Unfollow = %s' % excluidos
    print

####################################################################################
####################################################################################

print
print '###########################'
print '### TWITTER CHUPA CABRA ###'
print '###########################'
print

opt = int(raw_input('Entre com o tipo de processo = (1) Follow | (2) Unfollow | (3) Whitelist: '))

api = get_api()

if opt == 1:
    do_follow(api)
elif opt == 2:
    do_unfollow(api)
elif opt == 3:
    do_whitelist(api)
