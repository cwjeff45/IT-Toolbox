#toolbox main menu

#ORIGINAL CMD PROMPT MENU CONCEPT***
import os
import sys
import time
from Tools.IPConfig import run_ipconfig
from Tools.PCHealth import HealthCheck
from Tools.SysInfo import run_SI
import tkinter as tk
from tkinter import messagebox

greeted = False
version = '1.1'

#reutrn to menu - asks the user if they want to return to main Toolbox Menu
def menu():
    print("Return to main menu? (y/n)")
    ans = input().lower()
    if ans == 'y':
        clear()
        main()
    elif ans == 'n':
        print("Goodbye")
        quit()
    else:
        print("Invalid input (y/n)")
        return

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def greeting(dur = 3, length = 30):
    print(f"""
    v {version}
*      . +    o. '    . +.  +*   +  .    * '. +.
' _|_ .+    . + .  + +++.    +      ''  '+  .
 . | o'      . |  IT TOOLBOX  .'   o           ++
    .        - o -  o ' .    +_|_ '+ '+       /
'   +  +' +.  . |        '   '  |       .   ' *
        """)
    print("Loading: ", end=' ', flush=True)
    for i in range(length + 1):
        percent = int((i / length) * 100)
        bar = '█' * i + '-' * (length - i)
        sys.stdout.write(f'\rLoading: |{bar}| {percent}%')
        sys.stdout.flush()
        time.sleep(dur / length)
    print()


#Menu that asks for input and options
def main():
    global greeted
    if not greeted:
        greeting()
        greeted = True
    clear()

    while True:
        dir = input("""
1) IPConfig
2) PC Health Check
3) System Information
~
x) Exit
""")
        if dir == '1':
            test1()
            break
        elif dir == '2':
            test2()
            break
        elif dir == '3':
            test3()
            break
        elif dir == 'x':
            bye()
        else:
            print("Invalid input. Please enter '1, 2, 3 or x'")

def bye():
    clear()
    print("""
    *      . +    o. '    . +.  +*   +  .    * '. +.
' _|_ .+    . + .  + +++.    +      ''  '+  .
 . | o'      . |  IT TOOLBOX .'   o           ++
    .        - o - GOODBYE o ' .    +_|_ '+ '+
'   +  +' +.  . |        '   '  |       .   ' *

    """)
    time.sleep(3)
    exit()
    
#menu options that call to 
def test1():
    run_ipconfig()
    menu()

def test2():
    HealthCheck()
    menu()

def test3():
    run_SI()
    menu()

if __name__ == "__main__":
    main()
