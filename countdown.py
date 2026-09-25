import time

def countdown():
    for number in [3, 2, 1]:
        print(number)
        time.sleep(1)
    
    print("Go!")