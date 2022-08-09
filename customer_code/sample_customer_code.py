import argparse
import random

def argparse_func():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--name", dest='user_name', type=str, help='Add user_name')
    args = parser.parse_args()

    if args.user_name:
        print("------------------------------------------------")
        print("Hello!!! Mr.% s nice to meeet you" % args.user_name.upper())
        a = random.randint(0,10)

        print("Hey Do you know!! your got number as %i" % a)
        return True

    else:
        print("you forgot to enter your Name") 
        return False

if __name__ == '__main__':
    argparse_func()
