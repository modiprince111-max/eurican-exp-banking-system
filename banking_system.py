from abc import ABC, abstractmethod
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk


# ==========================
# Transaction Class
# ==========================

class Transaction:
    def __init__(self, transaction_type, amount, balance):
        self.transaction_type = transaction_type
        self.amount = amount
        self.timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.balance = balance

    def __str__(self):
        return (f"{self.timestamp} | "
                f"{self.transaction_type} | "
                f"Amount: ₹{self.amount:.2f} | "
                f"Balance: ₹{self.balance:.2f}")


# ==========================
# Bank Account (Abstract)
# ==========================

class BankAccount(ABC):

    def __init__(self, account_number, account_holder_name, balance=0):
        self.account_number = account_number
        self.account_holder_name = account_holder_name

        # Encapsulation
        self.__balance = balance
        self.__transaction_history = []

    def get_balance(self):
        return self.__balance

    def get_transactions(self):
        return self.__transaction_history

    def _set_balance(self, amount):
        self.__balance = amount

    def _add_transaction(self, transaction):
        self.__transaction_history.append(transaction)

    def deposit(self, amount):

        if amount <= 0:
            return False, "Invalid deposit amount."

        self.__balance += amount

        transaction = Transaction(
            "Deposit",
            amount,
            self.__balance
        )

        self.__transaction_history.append(transaction)

        return True, f"₹{amount:.2f} deposited successfully."

    @abstractmethod
    def withdraw(self, amount):
        pass

    @abstractmethod
    def monthly_update(self):
        pass

    def transfer(self, target_account, amount):

        success, message = self.withdraw(amount)

        if success:

            target_account.deposit(amount)

            return True, (
                f"₹{amount:.2f} transferred to Account "
                f"{target_account.account_number}"
            )

        return False, message

    def show_transactions(self):

        if not self.__transaction_history:
            print("No transactions found.")
            return

        print("\nTransaction History")

        for transaction in self.__transaction_history:
            print(transaction)

    # Magic Method
    def __str__(self):
        return (f"Account No: {self.account_number} | "
                f"Holder: {self.account_holder_name} | "
                f"Balance: ₹{self.__balance:.2f}")

    # Magic Method
    def __len__(self):
        return len(self.__transaction_history)


# ==========================
# Savings Account
# ==========================

class SavingsAccount(BankAccount):

    def __init__(
            self,
            account_number,
            account_holder_name,
            balance,
            interest_rate
    ):

        super().__init__(
            account_number,
            account_holder_name,
            balance
        )

        self.interest_rate = interest_rate

    def withdraw(self, amount):

        if amount <= 0:
            return False, "Invalid withdrawal amount."

        if amount <= self.get_balance():

            new_balance = self.get_balance() - amount

            self._set_balance(new_balance)

            self._add_transaction(
                Transaction(
                    "Withdraw",
                    amount,
                    new_balance
                )
            )

            return True, "Withdrawal successful."

        return False, "Insufficient balance."

    def monthly_update(self):

        interest = (
            self.get_balance() * self.interest_rate / 100
        )

        self.deposit(interest)

        return True, f"Interest of ₹{interest:.2f} added."


# ==========================
# Current Account
# ==========================

class CurrentAccount(BankAccount):

    def __init__(
            self,
            account_number,
            account_holder_name,
            balance,
            overdraft_limit
    ):

        super().__init__(
            account_number,
            account_holder_name,
            balance
        )

        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount):

        if amount <= 0:
            return False, "Invalid withdrawal amount."

        available_amount = (
            self.get_balance() +
            self.overdraft_limit
        )

        if amount <= available_amount:

            new_balance = self.get_balance() - amount

            self._set_balance(new_balance)

            self._add_transaction(
                Transaction(
                    "Withdraw",
                    amount,
                    new_balance
                )
            )

            return True, "Withdrawal successful."

        return False, "Overdraft limit exceeded."

    def monthly_update(self):

        fee = 100

        new_balance = self.get_balance() - fee

        self._set_balance(new_balance)

        self._add_transaction(
            Transaction(
                "Monthly Fee",
                fee,
                new_balance
            )
        )

        return True, "Monthly fee deducted."


# ==========================
# Customer Class
# ==========================

class Customer:

    def __init__(self, customer_id, name):

        self.customer_id = customer_id
        self.name = name

        self.accounts = []

    def add_account(self, account):
        self.accounts.append(account)

    def total_balance(self):

        total = 0

        for account in self.accounts:
            total += account.get_balance()

        return total

    def display_details(self):

        print("\nCustomer Details")
        print("ID:", self.customer_id)
        print("Name:", self.name)

        print("\nAccounts:")

        for account in self.accounts:
            print(account)


# ==========================
# Bank Class
# ==========================

class Bank:

    def __init__(self, bank_name):

        self.bank_name = bank_name

        self.customers = []

    def add_customer(self, customer):
        self.customers.append(customer)

    def get_total_accounts(self):
        total_accounts = 0

        for customer in self.customers:
            total_accounts += len(customer.accounts)

        return total_accounts

    def get_total_money(self):
        total_money = 0

        for customer in self.customers:
            for account in customer.accounts:
                total_money += account.get_balance()

        return total_money

    def bank_summary(self):

        print("\n===== BANK SUMMARY =====")
        print("Total Customers :", len(self.customers))
        print("Total Accounts  :", self.get_total_accounts())
        print("Total Money     : ₹", self.get_total_money())


# ==========================
# Desktop App
# ==========================

class BankingApp:
    def __init__(self, root, bank, customer, accounts):
        self.root = root
        self.bank = bank
        self.customer = customer
        self.accounts = accounts

        self.root.title(f"{self.bank.bank_name} Banking System")
        self.root.geometry("820x560")
        self.root.minsize(760, 520)

        self.selected_account = tk.StringVar()
        self.target_account = tk.StringVar()
        self.amount = tk.StringVar()
        self.status_message = tk.StringVar(value="Welcome to Eurican exp.")

        self.account_options = [
            f"{account_number} - {type(account).__name__}"
            for account_number, account in self.accounts.items()
        ]

        self.build_interface()
        self.refresh_account_details()

    def build_interface(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        header = tk.Frame(self.root, bg="#17324d", padx=20, pady=16)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        title = tk.Label(
            header,
            text=self.bank.bank_name,
            bg="#17324d",
            fg="white",
            font=("Segoe UI", 24, "bold")
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = tk.Label(
            header,
            text="Desktop Banking System",
            bg="#17324d",
            fg="#dbeafe",
            font=("Segoe UI", 11)
        )
        subtitle.grid(row=1, column=0, sticky="w")

        main = tk.Frame(self.root, padx=20, pady=18)
        main.grid(row=1, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        controls = ttk.LabelFrame(main, text="Actions", padding=14)
        controls.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        controls.columnconfigure(0, weight=1)

        ttk.Label(controls, text="Account").grid(row=0, column=0, sticky="w")
        account_menu = ttk.Combobox(
            controls,
            textvariable=self.selected_account,
            values=self.account_options,
            state="readonly"
        )
        account_menu.grid(row=1, column=0, sticky="ew", pady=(4, 12))
        account_menu.current(0)
        account_menu.bind("<<ComboboxSelected>>", self.refresh_account_details)

        ttk.Label(controls, text="Amount").grid(row=2, column=0, sticky="w")
        amount_entry = ttk.Entry(controls, textvariable=self.amount)
        amount_entry.grid(row=3, column=0, sticky="ew", pady=(4, 12))

        ttk.Label(controls, text="Transfer To").grid(row=4, column=0, sticky="w")
        target_menu = ttk.Combobox(
            controls,
            textvariable=self.target_account,
            values=self.account_options,
            state="readonly"
        )
        target_menu.grid(row=5, column=0, sticky="ew", pady=(4, 16))
        target_menu.current(1)

        ttk.Button(
            controls,
            text="Deposit",
            command=self.deposit
        ).grid(row=6, column=0, sticky="ew", pady=4)

        ttk.Button(
            controls,
            text="Withdraw",
            command=self.withdraw
        ).grid(row=7, column=0, sticky="ew", pady=4)

        ttk.Button(
            controls,
            text="Transfer",
            command=self.transfer
        ).grid(row=8, column=0, sticky="ew", pady=4)

        ttk.Button(
            controls,
            text="Monthly Update",
            command=self.monthly_update
        ).grid(row=9, column=0, sticky="ew", pady=4)

        ttk.Button(
            controls,
            text="Bank Summary",
            command=self.show_bank_summary
        ).grid(row=10, column=0, sticky="ew", pady=(16, 4))

        details = ttk.LabelFrame(main, text="Account Details", padding=14)
        details.grid(row=0, column=1, sticky="nsew")
        details.columnconfigure(0, weight=1)
        details.rowconfigure(1, weight=1)

        self.account_details = tk.Label(
            details,
            text="",
            anchor="w",
            justify="left",
            font=("Segoe UI", 11),
            padx=8,
            pady=8
        )
        self.account_details.grid(row=0, column=0, sticky="ew")

        self.transaction_list = tk.Listbox(
            details,
            font=("Consolas", 10),
            height=12
        )
        self.transaction_list.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        status = tk.Label(
            self.root,
            textvariable=self.status_message,
            anchor="w",
            bg="#eef2f7",
            fg="#1f2937",
            padx=20,
            pady=8
        )
        status.grid(row=2, column=0, sticky="ew")

    def get_account_number_from_menu(self, value):
        return int(value.split(" - ")[0])

    def get_selected_account(self):
        account_number = self.get_account_number_from_menu(
            self.selected_account.get()
        )
        return self.accounts[account_number]

    def get_target_account(self):
        account_number = self.get_account_number_from_menu(
            self.target_account.get()
        )
        return self.accounts[account_number]

    def get_amount(self):
        try:
            return float(self.amount.get())
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a number.")
            return None

    def deposit(self):
        amount = self.get_amount()

        if amount is None:
            return

        account = self.get_selected_account()
        success, message = account.deposit(amount)
        self.show_result(success, message)

    def withdraw(self):
        amount = self.get_amount()

        if amount is None:
            return

        account = self.get_selected_account()
        success, message = account.withdraw(amount)
        self.show_result(success, message)

    def transfer(self):
        amount = self.get_amount()

        if amount is None:
            return

        sender = self.get_selected_account()
        receiver = self.get_target_account()

        if sender.account_number == receiver.account_number:
            self.show_result(False, "Sender and receiver cannot be the same.")
            return

        success, message = sender.transfer(receiver, amount)
        self.show_result(success, message)

    def monthly_update(self):
        account = self.get_selected_account()
        success, message = account.monthly_update()
        self.show_result(success, message)

    def show_bank_summary(self):
        message = (
            f"Bank Name: {self.bank.bank_name}\n"
            f"Total Customers: {len(self.bank.customers)}\n"
            f"Total Accounts: {self.bank.get_total_accounts()}\n"
            f"Total Money: ₹{self.bank.get_total_money():.2f}"
        )
        messagebox.showinfo("Bank Summary", message)

    def show_result(self, success, message):
        self.status_message.set(message)

        if not success:
            messagebox.showwarning("Banking System", message)

        self.refresh_account_details()

    def refresh_account_details(self, event=None):
        account = self.get_selected_account()

        self.account_details.config(
            text=(
                f"Account Number: {account.account_number}\n"
                f"Holder Name: {account.account_holder_name}\n"
                f"Account Type: {type(account).__name__}\n"
                f"Balance: ₹{account.get_balance():.2f}\n"
                f"Transactions: {len(account)}"
            )
        )

        self.transaction_list.delete(0, tk.END)

        transactions = account.get_transactions()

        if not transactions:
            self.transaction_list.insert(tk.END, "No transactions found.")
            return

        for transaction in transactions:
            self.transaction_list.insert(tk.END, str(transaction))


def create_sample_bank():
    bank = Bank("Eurican exp")

    customer1 = Customer(101, "Prince")
    bank.add_customer(customer1)

    savings = SavingsAccount(1001, "Prince", 5000, 5)
    current = CurrentAccount(2001, "Prince", 3000, 1000)

    customer1.add_account(savings)
    customer1.add_account(current)

    accounts = {
        1001: savings,
        2001: current
    }

    return bank, customer1, accounts


if __name__ == "__main__":
    bank_data, customer_data, account_data = create_sample_bank()

    root_window = tk.Tk()
    app = BankingApp(
        root_window,
        bank_data,
        customer_data,
        account_data
    )
    root_window.mainloop()
