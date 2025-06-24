import argparse
from . import repo

#this file is used to parse command line 

def main():
    parser = argparse.ArgumentParser(description = "VCTRL - a version control system clone for my personal learning project")
    subparsers = parser,add_subparsers(dest = "command")
    
    #for parsing init
    init_parser = subparsers.add_parser("init", help = "initialise a new repo")

    #parsing
    if args.command == "init":
        repo.init_repo()
    

if __name__ == __main__:
    main()


    
        

