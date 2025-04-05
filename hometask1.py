from typing import Callable
from datetime import datetime
import pickle


class Phone: # клас для телефонного номера
    def __init__(self, number: str):
        self.validate(number)
        self.value = number

    def validate(self, number):
        if not number.isdigit() or len(number) != 10: # перевірка на цифри та довжину 10 символів
            raise ValueError("Phone number must contain exactly 10 digits.")

    def __str__(self):
        return self.value


class Birthday: # клас для дати народження
    def __init__(self, date_str: str):
        self.value = self.validate(date_str)

    def validate(self, date_str): # перевірка формату дати
        try:
            return datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Birthday must be in format DD.MM.YYYY.")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record: # клас для запису контакту
    def __init__(self, name: str):
        self.name = name
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str): # додавання телефону
        self.phones.append(Phone(phone))

    def change_phone(self, phone: str): # зміна телефону
        self.phones = [Phone(phone)]

    def add_birthday(self, birthday_str: str): # додавання дати народження 
        self.birthday = Birthday(birthday_str)

    def __str__(self): 
        phones_str = ", ".join(str(p) for p in self.phones)
        bday = f", Birthday: {self.birthday}" if self.birthday else ""
        return f"{self.name} - Phones: {phones_str}{bday}"


class AddressBook: # клас для адресної книги
    def __init__(self):
        self.contacts = {}

    def add_record(self, record: Record): # додавання запису
        self.contacts[record.name] = record

    def find(self, name: str): # пошук контакту
        return self.contacts.get(name)

    def change(self, name: str, phone: str): # зміна контакту 
        if name in self.contacts:
            self.contacts[name] = phone
            return True
        return False

    def get(self, name: str): # отримання контакту
        return self.contacts.get(name)

    def get_all(self): # отримання всіх контактів
        return self.contacts.values()
    
def save_address_book(book: AddressBook, filename="address_book.pkl"):
        with open(filename, "wb") as file:
            pickle.dump(book, file)

def load_address_book(filename="address_book.pkl") -> AddressBook:
        try:
            with open(filename, "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return AddressBook()

def input_error(func: Callable): # створюємо декоратор для обробки помилок
    def wrapper(*args, **kwargs): # створюємо функцію-обгортку
        try:
            return func(*args, **kwargs) 
        except KeyError: # ключ не знайдено
            return "Contact not found."
        except ValueError: # некоректні дані
            return "Invalid data. Please check your input."
        except IndexError: # недостатньо аргументів
            return "Insufficient input. Please check your command."
    return wrapper

def parse_input(user_input):  #обробка команд користувача
    cmd, *args = user_input.split() # розділення команди та аргументів
    cmd = cmd.strip().lower() # нижній регістр
    return cmd, *args 

@input_error
def add_contact(args, book: AddressBook): # додавання контакту
    if len(args) < 2:
        raise IndexError("Name and phone are required.")

    name = args[0]
    phone = args[1]
    birthday = args[2] if len(args) > 2 else None

    record = book.find(name)
    if record:
        record.change_phone(phone)
        if birthday:
            record.add_birthday(birthday)
        return "Contact updated."
    else:
        record = Record(name)
        record.add_phone(phone)
        if birthday:
            record.add_birthday(birthday)
        book.add_record(record)
        return "Contact added."

@input_error
def change_contact(args, book: AddressBook): # зміна контакту
    name, phone = args
    record = book.find(name)
    if record:
        record.change_phone(phone)
        return "Phone changed."
    return "Contact not found."

@input_error
def show_contact(args, book: AddressBook): # показати контакт
    name = args[0]
    record = book.find(name)
    if record:
        return str(record)
    return "Contact not found."
    
def show_all(book: AddressBook): # показати всі контакти
    contacts = book.get_all()
    #if contacts:
    return "\n".join([str(record) for record in contacts]) or "No contacts."

@input_error
def add_birthday(args, book: AddressBook): # додавання дати народження
    name, bday = args
    record = book.find(name)
    if record:
        record.add_birthday(bday)
        return "Birthday added."
    return "Contact not found."

@input_error
def show_birthday(args, book: AddressBook): # показати дату народження
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is {record.birthday}"
    return "Birthday not found."

@input_error
def get_upcoming_birthdays(book: AddressBook): # отримати найближчі дати народження на 7 днів
    from datetime import datetime, timedelta
    today = datetime.today().date()
    upcoming_birthdays = []

    for record in book.get_all():
        if record.birthday:
            bday = record.birthday.value  
            bday_this_year = bday.replace(year=today.year)

            if bday_this_year < today:
                bday_this_year = bday_this_year.replace(year=today.year + 1)

            if bday_this_year.weekday() in (5, 6): # Переносимо привітання на понеділок, якщо на вихідний
                days_to_monday = 7 - bday_this_year.weekday()
                bday_this_year += timedelta(days=days_to_monday)

            if today <= bday_this_year <= today + timedelta(days=7):
                upcoming_birthdays.append(
                    f"{record.name}: {bday_this_year.strftime('%Y-%m-%d')}"
                )

    return "\n".join(upcoming_birthdays) if upcoming_birthdays else "No birthdays in the next 7 days."

def main():
    book = load_address_book()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ") 
        command, *args = parse_input(user_input) 

        if command in ["close", "exit"]:
            save_address_book(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_contact(args, book))
        elif command == "all": 
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(get_upcoming_birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__": # точка входу
    main()