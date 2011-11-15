#! /usr/bin/python
# -*- coding: utf-8 -*-

import twitter
import pycurl
import StringIO
import simplejson
import settings

def seleciona_conta_twitter():
    if settings.conta_twitter_default:
        if settings.contas_twitter.has_key(settings.conta_twitter_default):
            return settings.conta_twitter_default, \
                   settings.contas_twitter[settings.conta_twitter_default]['consumer_key'], \
                   settings.contas_twitter[settings.conta_twitter_default]['consumer_secret'], \
                   settings.contas_twitter[settings.conta_twitter_default]['access_token_key'], \
                   settings.contas_twitter[settings.conta_twitter_default]['access_token_secret']
        else:
            print 'O parametro (conta_twitter_default) nao corresponde a uma conta valida configurada, verifique o (settings.py)'
            return None
    else:
        conta_twitter = raw_input('Entre com o SEU usuario twitter: ')
        if settings.contas_twitter.has_key(conta_twitter):
            return conta_twitter, \
                   settings.contas_twitter[conta_twitter]['consumer_key'], \
                   settings.contas_twitter[conta_twitter]['consumer_secret'], \
                   settings.contas_twitter[conta_twitter]['access_token_key'], \
                   settings.contas_twitter[conta_twitter]['access_token_secret']
        else:
            print 'O usuario twitter informado nao corresponde a uma conta valida configurada'
            return None
        
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

def load_followers_seguindo(user_id, chk_seguindo):

    ids = []
    
    if chk_seguindo == 2:
    
        followers_dict = get_followers_ids(user_id)
        
        if followers_dict.has_key('error'):
            return followers_dict
    
        while (followers_dict['ids']):
            
            for id in followers_dict['ids']:
                ids.append(int(id))
            else:
                next_cursor = int(followers_dict['next_cursor'])
                followers_dict = get_followers_ids(user_id, cursor=next_cursor)
    
                if followers_dict.has_key('error'):
                    return followers_dict
            
    return ids

def do_whitelist(api):
    print
    
    contador = 0
    
    friend_ids = api.GetFriendIDs(user=USER, cursor=-1)
    
    f = open('whitelist.txt', 'w')

    f.write('#comentario\n')
    f.write('#user.id\n')
    f.write('#99999999\n')
    f.write('#user.screen_name\n')
    f.write('#@chiquinho\n')

    while (friend_ids['ids']):
        
        for user_id in friend_ids['ids']:
            contador = contador + 1
            
            f.write('%s\n' % user_id)
            
            print '%s - Whitelist (%s)' % (contador, user_id)

        else:
            next_cursor = int(friend_ids['next_cursor'])
            friend_ids = api.GetFriendIDs(user=USER, cursor=next_cursor)
            
    f.close()

    print
    print 'Total de Whitelist = %s' % contador
    print

def load_whitelist():

    f = open('whitelist.txt', 'r')

    whitelist_ids = []
    whitelist_screen_name = []
    
    for line in f:
        line = line.replace('\n', '')
        if not line.startswith('#'):
            if line:
                if line.startswith('@'):
                    line = line.replace('@', '')
                    whitelist_screen_name.append(line)
                else:
                    whitelist_ids.append(int(line))
            
    f.close()
    
    return whitelist_ids, whitelist_screen_name

def load_friends_list(api, chk_amizade):

    ids = []
    
    if chk_amizade == 1:

        friend_ids = api.GetFriendIDs(user=USER, cursor=-1)
    
        while (friend_ids['ids']):
            
            for user_id in friend_ids['ids']:
                ids.append(int(user_id))
            else:
                next_cursor = int(friend_ids['next_cursor'])
                friend_ids = api.GetFriendIDs(user=USER, cursor=next_cursor)
            
    return ids
    
def load_dont_disturb():

    f = open('dont_disturb.txt', 'r')

    ids = []
    
    for line in f:
        line = line.replace('\n', '')
        if not line.startswith('#'):
            if line:
                ids.append(int(line))
            
    f.close()
    
    return ids

def do_follow(api):
    qtd = int(raw_input('Quantidade: '))
    pag = int(raw_input('A partir de qual pagina: '))
    seguidores_de = raw_input('Seguir os seguidores de qual usuario: ')
    chk_amizade = int(raw_input('Deseja fazer verificacao de amizade = (1) Sim | (2) Nao: '))

    print
    
    contador = 0
    seguidos = 0
    
    seguidores_de_user = api.GetUser(seguidores_de)
    
    meu_user = api.GetUser(USER)
    
    followers_dict = get_followers_ids(seguidores_de_user.id)
    
    friend_ids_atual = load_friends_list(api, chk_amizade)
    
    ids_dont_disturb = load_dont_disturb()

    if not followers_dict.has_key('error'): 
    
        followers_ids = followers_dict['ids']
    
        cursor_ini = pag * qtd - qtd
        cursor_fim = pag * qtd if pag * qtd < len(followers_ids) else len(followers_ids)
        
        f = open('dont_disturb.txt', 'a')
        
        for i in range(cursor_ini, cursor_fim):
            contador = contador + 1
            
            if followers_ids[i] not in friend_ids_atual:
                if followers_ids[i] not in ids_dont_disturb:                
                    try:
                        api.CreateFriendship(followers_ids[i])
            
                        seguidos = seguidos + 1
                        
                        f.write('%s\n' % followers_ids[i])
                        ids_dont_disturb.append(followers_ids[i])
                
                        print '%s - Follow (%s)' % (contador, followers_ids[i])
                    except Exception, e:
                        print '%s - Follow (%s) = ERROR AO TENTAR DAR O FOLLOW!!!!!!' % (contador, followers_ids[i])

                else:
                    print '%s - Follow (%s) = Dont Disturb!!!' % (contador, followers_ids[i])
            else:
                print '%s - Follow (%s) = Ja esta seguindo!!!' % (contador, followers_ids[i])
        
        f.close()

    else:
        print '%s - Follow (%s) = ERROR AO TENTAR RECUPERAR OS FOLLOWERS!!!' % (contador, followers_dict['error'])
        
    print
    print 'Total de Follow = %s' % seguidos
    print

def do_unfollow(api):
    qtd = int(raw_input('Quantidade: '))
    chk_seguindo = int(raw_input('Deseja dar unfollow em usuarios que estao te seguindo = (1) Sim | (2) Nao: '))

    print
    
    whitelist_ids, whitelist_screen_name = load_whitelist()
    
    meu_user = api.GetUser(USER)
    ids_seguindo = load_followers_seguindo(meu_user.id, chk_seguindo)
    
    if isinstance(ids_seguindo, dict):
        print 'Unfollow (%s) = ERROR AO TENTAR RECUPERAR OS USUARIOS QUE ESTAO TE SEGUINDO!!!' % ids_seguindo['error']
        return
    
    contador = 0
    excluidos = 0
    
    friends = api.GetFriends(USER)
    
    ids_dont_disturb = load_dont_disturb()

    f = open('dont_disturb.txt', 'a')

    while (friends and contador < qtd):
        
        for user in friends:
            contador = contador + 1

            if (user.id not in whitelist_ids) and (user.screen_name not in whitelist_screen_name):
                if user.id not in ids_seguindo:
                    try:
                        api.DestroyFriendship(user.id) 
                        
                        excluidos = excluidos + 1
                        
                        if user.id not in ids_dont_disturb:
                            f.write('%s\n' % user.id)
                            ids_dont_disturb.append(user.id)
                        
                        print '%s - Unfollow (%s)' % (contador, user.screen_name)
                    except Exception, e:
                        print '%s - Unfollow (%s) = ERROR AO TENTAR DAR O UNFOLLOW!!!' % (contador, user.screen_name)
                else:
                    print '%s - Unfollow (%s) = ESSE USUARIO ESTA TE SEGUINDO!!!' % (contador, user.screen_name)
            else:
                print '%s - Unfollow (%s) = WHITELIST!!!' % (contador, user.screen_name)
                        
            if contador == qtd:
                break
        else:
            friends = api.GetFriends(USER)

    f.close()
    
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

USER, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET = seleciona_conta_twitter()

api = get_api()

if opt == 1:
    do_follow(api)
elif opt == 2:
    do_unfollow(api)
elif opt == 3:
    do_whitelist(api)
