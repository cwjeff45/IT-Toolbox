#toolbox main menu

#NOT WORKING. EXECUTES IPCONFIG ON RUN***************
from Tools.IPConfig import run_ipconfig

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

def test1():
    run_ipconfig()
    menu()

def test2():
    print("Test 2 Open")
    menu()

def test3():
    print("Test 3 Open")
    menu()

def main():
    while True:
        print("Toolbox")
        dir = input("""
1) test 1
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

if __name__ == "__main__":
    main()
