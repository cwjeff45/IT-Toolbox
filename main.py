#toolbox main menu

from Tools.IPConfig import run_ipconfig
from Tools.PCHealth import HealthCheck

#reutrn to menu - asks the user if they want to return to main Toolbox Menu
def menu():
    print("Return to main menu? (y/n)")
    ans = input().lower()
    if ans == 'y':
        main()
    elif ans == 'n':
        print("Goodbye")
        quit()
    else:
        print("Invalid input (y/n)")
        return

#Menu that asks for input and options
def main():
    while True:
        print("Toolbox")
        dir = input("""
1) IPConfig
2) test 2
3) test 3

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
            exit()
        else:
            print("Invalid input. Please enter '1, 2, 3 or x'")

#menu options that call to 
def test1():
    run_ipconfig()
    menu()

def test2():
    HealthCheck()
    menu()

def test3():
    print("Test 3 Open")
    menu()

if __name__ == "__main__":
    main()
