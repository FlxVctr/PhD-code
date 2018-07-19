# Usage: 
# insert consumer and app keys below
# run (eg in Terminal): python3 scriptname.py inputfile.csv outputfile.csv
# inputfile is a list of userids

import time
import csv
import io
import tweepy
from os import stat
from sys import argv

ckey = ''
csecret = ''
atoken = ''
asecret = ''

auth = tweepy.OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

userlistpath = argv[1]
friendlistpath = argv[2]

def get_friend_ids(userid):

    userid = int(userid)

    uids = tweepy.Cursor(api.friends_ids, id = userid).items()

    idlist = []
    idcount = 0
    
    try:
        for uid in uids:
            idlist.append(uid)
            idcount += 1
    except tweepy.TweepError as e:
        idlist.append(-int(e.reason[-3:]))
        print(e.reason + ' for %d' %(userid))
    
    print('%d friend ids collected for %d.' %(idcount,userid))
    
    return idlist


def get_screen_name_and_created_at(uids):
    
    friend_count = len(uids)
    
    i = 0
    
    results = []
    
    while i < friend_count:
        
        if uids[0] < 0:
            results.append([uids[i]]*3)
            break
        else:
            j = i + 100
            if j > friend_count:
                j = friend_count
            try:
                users = api.lookup_users(user_ids=uids[i:j])
                for user in users:
                    results.append([uids[i],user.screen_name,int(time.mktime(user.created_at.timetuple()))])
                    i += 1
            except tweepy.TweepError as e:
                code = int(e.reason[-3:])
                for uid in uids[i:j]:
                    results.append([uid, -code, -code])
                    i += 1        
    
    print('%d friend details collected.' %(i))
                          
    return results


def write_edge_list(readpath, writepath):
    with io.open(readpath,
                 encoding='utf_8', newline='') as userlist, io.open(writepath,
                                                                    mode='a',encoding='utf_8', newline='') as friendlist:
        users = csv.reader(userlist)
        friends = csv.writer(friendlist, delimiter = '\t', lineterminator = '\n')
        
        if stat(writepath).st_size == 0:
            friends.writerow(['user','friend_id','friend_name','friend_created'])
        
        n = 0
        
        for user in users:
            print('Friends of %d users gathered so far. Goin on.' %(n))
            friendids = get_friend_ids(user[0])
            frienddetails = get_screen_name_and_created_at(friendids)
            for details in frienddetails:
                friends.writerow([user[0],details[0],details[1],details[2]])
            n += 1
        
    print('Friends of %d users gathered. Pew. That was exciting.' %(n))



write_edge_list(userlistpath,friendlistpath)
