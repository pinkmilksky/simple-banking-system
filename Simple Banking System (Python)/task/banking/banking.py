import sqlite3
import random

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
conn.commit()

start_menu_text = """1. Create an account
2. Log into account
0. Exit"""

account_menu_text = """1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
"""

next_id = 0


def luhn_algorithm(full_number):
    for i in range(0, len(full_number), 2):
        full_number[i] *= 2
        if full_number[i] > 9:
            full_number[i] -= 9

    total = sum(full_number)
    check_digit = (10 - (total % 10)) % 10
    return check_digit


def generate_card_number():
    card_number = random.randint(0, 999999999)
    bin = [4, 0, 0, 0, 0, 0]
    numbers = [int(x) for x in f"{card_number:09}"]
    full_number = bin + numbers
    check_digit = luhn_algorithm(full_number)
    full_number = bin + numbers
    full_number.append(check_digit)
    result = ''.join(map(str, full_number))
    return int(result)


def generate_pin():
    pin = random.randint(0, 9999)
    return f"{pin:04}"


def create_account():
    global next_id
    card_number = generate_card_number()
    pin = generate_pin()
    id = next_id
    next_id += 1

    cur.execute(f'INSERT INTO card VALUES ({id}, {card_number}, {pin}, 0)')
    conn.commit()

    print("Your card has been created")
    print(f"Your card number:\n{card_number}\nYour card PIN:\n{pin}")


def log_into_account():
    card_number_to_check = int(input("\nEnter your card number:"))
    pin_to_check = input("\nEnter your PIN:")

    cur.execute(f'SELECT * FROM card WHERE number = {card_number_to_check}')
    user = cur.fetchone()

    if user is None:
        print("Wrong card number or PIN!")
        return None

    actual_pin = f"{int(user[2]):04}"
    if pin_to_check == actual_pin:
        print("\nYou have successfully logged in!")
        return user
    else:
        print("Wrong card number or PIN!")
        return None


def add_income(user_card_number):
    income = int(input("Enter income:"))
    balance = get_balance(user_card_number) + income
    cur.execute(f'UPDATE card SET balance = {balance} WHERE number = {user_card_number}')
    conn.commit()
    print("Income was added!")
    return


def close_account(user_card_number):
    cur.execute(f'DELETE FROM card WHERE "number" = {user_card_number};')
    conn.commit()
    print("The account has been closed!")
    return


def try_read_recipient(user_card_number):
    recipient_card_number = input("Enter card number:")

    recipient_card_number_array = [int(x) for x in recipient_card_number]
    if int(luhn_algorithm(recipient_card_number_array[:15])) != int(recipient_card_number[15]):
        print("Probably you made a mistake in the card number. Please try again!")
        return None

    if recipient_card_number == user_card_number:
        print("You can't transfer money to the same account!")
        return None

    cur.execute(f'SELECT * FROM card WHERE number = {recipient_card_number}')
    recipient = cur.fetchone()
    if recipient is None:
        print("Such a card does not exist")
        return None

    print("recipient " + str(recipient))
    return recipient


def do_transfer(card_number):
    valid_recipient = try_read_recipient(card_number)
    if valid_recipient is None:
        return

    money_to_transfer = int(input("Enter how much money you want to transfer:"))
    source_balance = get_balance(card_number)
    print(f"my balance {source_balance}")
    if money_to_transfer > source_balance or money_to_transfer < 0:
        print("Not enough money!")
        return

    dest_balance = get_balance(valid_recipient[1])
    cur.execute(f'UPDATE card SET "balance" = {dest_balance + money_to_transfer} WHERE "number" = {valid_recipient[1]}')
    cur.execute(f'UPDATE card SET "balance" = {source_balance - money_to_transfer} WHERE "number" = {card_number}')
    conn.commit()
    print("Success!")
    return


def get_balance(card_number):
    cur.execute(f'SELECT * FROM card WHERE number = {card_number}')
    user_current = cur.fetchone()
    print(f'user current ' + str(user_current))
    if user_current is None:
        return None
    return user_current[3]


def account_menu(card_number):
    while True:
        user_selection = int(input(account_menu_text))
        if user_selection == 1:
            balance = get_balance(card_number)
            print(f"Balance: {balance}")

        elif user_selection == 2:
            add_income(card_number)

        elif user_selection == 3:
            do_transfer(card_number)

        elif user_selection == 4:
            close_account(card_number)

        elif user_selection == 5:
            print("You have successfully logged out!")
            return

        elif user_selection == 0:
            print("Bye!")
            exit()


def start_menu():
    while True:
        user_choice = int(input(start_menu_text))
        if user_choice == 1:
            create_account()
        elif user_choice == 2:
            user = log_into_account()
            if user is not None:
                account_menu(user[1])
        elif user_choice == 0:
            print("\nBye!")
            return


start_menu()
