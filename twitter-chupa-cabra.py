#! /usr/bin/python
# -*- coding: utf-8 -*-

import twitter
import pycurl
import StringIO
import simplejson

USER                = '????????????????'
CONSUMER_KEY        = '????????????????'
CONSUMER_SECRET     = '????????????????'
ACCESS_TOKEN_KEY    = '????????????????'
ACCESS_TOKEN_SECRET = '????????????????'

def get_api():
    
    api = twitter.Api(consumer_key=CONSUMER_KEY, 
                      consumer_secret=CONSUMER_SECRET, 
                      access_token_key=ACCESS_TOKEN_KEY, 
                      access_token_secret=ACCESS_TOKEN_SECRET)
    
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
    curl.close()
    return False if response == 'false' else True

def do_follow(api, qtd):
    pag = int(raw_input('A partir de qual pagina: '))
    seguidores_de = raw_input('Seguir os seguidores de qual usuario: ')
    
    print
    
    seguidores_de_user = api.GetUser(seguidores_de)
    
    meu_user = api.GetUser(USER)
    
    followers_dict = get_followers_ids(seguidores_de_user.id)
    followers_ids = followers_dict['ids']

    contador = 0
    seguidos = 0
    
    cursor_ini = pag * qtd - qtd
    cursor_fim = pag * qtd if pag * qtd < len(followers_ids) else len(followers_ids)
    
    for i in range(cursor_ini, cursor_fim):
        esta_seguindo = chk_friendships_exists(meu_user.id, followers_ids[i])
        
        contador = contador + 1
        
        if esta_seguindo:
            print '%s - Follow (%s) = Ja esta seguindo!!!' % (contador, followers_ids[i])
        else:
            api.CreateFriendship(followers_ids[i])

            seguidos = seguidos + 1
    
            print '%s - Follow (%s)' % (contador, followers_ids[i])
    
    print
    print 'Total de Follow = %s' % seguidos
    print

def do_unfollow(api, qtd):
    print
    
    excluidos = 0
    
    friends = api.GetFriends(USER)

    while (friends and excluidos < qtd):
        
        for user in friends:
            api.DestroyFriendship(user.id) 
            
            excluidos = excluidos + 1
            
            print '%s - Unfollow (%s)' % (excluidos, user.screen_name)
            
            if excluidos == qtd:
                break
        else:
            friends = api.GetFriends(USER)

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

opt = int(raw_input('Entre com o tipo de processo = (1) Follow | (2) Unfollow: '))
qtd = int(raw_input('Quantidade: '))

api = get_api()

if opt == 1:
    do_follow(api, qtd)
elif opt == 2:
    do_unfollow(api, qtd)
