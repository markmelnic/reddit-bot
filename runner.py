
from redditBot import *


def procedure():
    dv = boot()
    loginProc(dv, username, password)
    upvoter(dv, action_link)
    rds.med()
    killb(dv)

if __name__ == '__main__':
    creds = credentials()
    inst = 0
    print(len(creds))

    while inst < len(creds):
        username = creds[inst]
        password = creds[inst + 1]
        print(username)
        print(password)
    
        procedure()

        inst += 3