from abc import ABC, abstractmethod
import uuid

class Account(ABC):
    def __init__(self, wallet_id, wallet_status, owner, balance):
        self.wallet_id = wallet_id
        self.owner = owner
        self._balance = balance
        self._wallet_status = wallet_status

    @abstractmethod
    def withdraw(self, amount):
        ...

    @abstractmethod
    def get_account_info(self):
        ...

    @abstractmethod
    def __str__(self):
        ...

class SavingsAccount(Account):
    def __init__(self, wallet_id=None, wallet_status="savings account", owner=None, balance=0, min_balance=100, monthly_interest_rate=2):
        super().__init__(wallet_id, wallet_status, owner, balance)
        self._min_balance = min_balance
        self._monthly_interest_rate = monthly_interest_rate

        if self.wallet_id is None:
            self.wallet_id = uuid.uuid4().hex[:6]

        if balance < min_balance:
            raise ValueError(f"Your balance cant be less than {min_balance}")

        if owner is None:
            raise ValueError("Name cannot be empty")

        if wallet_status != "savings account":
            raise ValueError("Invalid wallet status")

    def __str__(self):
        return (f"account type: {self._wallet_status} |"
                f" client: {self.owner} |"
                f" last 4 characters of the ID: ...{self.wallet_id[-4:]} |"
                f" status: {self._wallet_status} |"
                f" balance: {self._balance} |"
                f" min balance: {self._min_balance} |"
                f"monthly interest rate: {self._monthly_interest_rate}%"
                )
    def get_account_info(self):
        print(f"Name: {self.owner}, "
              f"ID: {self.wallet_id}, "
              f"Balance: {self._balance}, "
              f"Status: {self._wallet_status}, "
              f"Your interest rate: {self._monthly_interest_rate}%"
              )

    def get_balance(self):
        print(f"Your balance is {self._balance}")

    def apply_monthly_interest(self):
        self._balance += self._balance * (self._monthly_interest_rate / 100)
        print(f"Your balance including monthly rate is: {self._balance}")

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Your withdraw cant be less than 0")
        elif self._balance - amount < self._min_balance:
            raise ValueError(f"Your balance cant be less than {self._min_balance}")
        else:
            self._balance -= amount
            print(f"Successfully withdrawn. Your balance now is: {self._balance}")

class PremiumAccount(Account):
    def __init__(self, wallet_id=None, wallet_status="premium account", owner=None, balance=0, withdraw_limit=3000, overdraft_limit=-1000, commission=10):
        super().__init__(wallet_id, wallet_status, owner, balance)
        self._withdraw_limit = withdraw_limit
        self._overdraft_limit = overdraft_limit
        self._commission = commission

        if self.wallet_id is None:
            self.wallet_id = uuid.uuid4().hex[:6]

        if balance <= 0:
            raise ValueError("Your balance can't be less than 0")

        if owner is None:
            raise ValueError("Name cannot be empty")

        if wallet_status != "premium account":
            raise ValueError("Invalid wallet status")

    def __str__(self):
        return (f"account type: {self._wallet_status}, | "
                f"client: {self.owner} | "
                f"last 4 characters of the ID: ...{self.wallet_id[-4:]} | "
                f"status: {self._wallet_status} | "
                f"balance: {self._balance} | "
                f"withdraw limit: {self._withdraw_limit} | "
                f"overdraft limit (minimal balance): {self._overdraft_limit} | "
                f"commission: {self._commission}"
                )

    def get_account_info(self):
        print(f"Name: {self.owner}, "
              f"ID: {self.wallet_id}, "
              f"Balance: {self._balance}, "
              f"withdraw limit: {self._withdraw_limit}, "
              f"overdraft limit: {self._overdraft_limit}, "
              f"commission: {self._commission}"
              )

    def get_balance(self):
        print(f"Your balance is {self._balance}")

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Your withdraw cant be less than 0")

        elif amount > self._withdraw_limit:
            raise ValueError(f"You cant withdraw more than {self._withdraw_limit}")

        elif self._balance - (amount + self._commission) < self._overdraft_limit:
            raise ValueError(f"Your balance after the withdrawal cant be less than {self._overdraft_limit}")

        else:
            self._balance = self._balance - (amount + self._commission)
            print(f"Successfully withdrawn. Your balance now is: {self._balance}")



class InvestmentAccount(Account):
    ALLOWED_ASSETS = {"stocks", "bonds", "etf"}

    def __init__(self, wallet_id=None, wallet_status="investment account", owner=None, balance=0, portfolio=None):
        super().__init__(wallet_id, wallet_status, owner, balance)

        if balance <= 0:
            raise ValueError("Your balance can't be less than 0")

        if owner is None:
            raise ValueError("Name cannot be empty")

        if wallet_status != "investment account":
            raise ValueError("Invalid wallet status")

        if self.wallet_id is None:
            self.wallet_id = uuid.uuid4().hex[:6]

        if portfolio is None:
            portfolio = {
                "stocks": self._balance / 2,
                "bonds": self._balance / 4,
                "etf": self._balance / 4,
            }

        self._portfolio = dict(portfolio)

        for asset_type, amount in self._portfolio.items():
            if asset_type not in self.ALLOWED_ASSETS:
                raise ValueError("Invalid asset type")
            if amount <= 0:
                raise ValueError("Investment amount must be positive")

        if sum(self._portfolio.values()) != self._balance:
            raise ValueError("Portfolio total must equal total balance")

    def __str__(self):
        return (f"last 4 characters of ID: ...{self.wallet_id[-4:]} | "
                f"wallet status: {self._wallet_status} | "
                f"owner: {self.owner} | "
                f"balance: {self._balance} | "
                f"portfolio: {self._portfolio}")

    def get_account_info(self):
        print(f"name: {self.owner}, id: {self.wallet_id}, balance: {self._balance}, "
              f"portfolio: {self._portfolio}, wallet status: {self._wallet_status}")

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("You cant withdraw negative amount")
        elif amount > self._balance:
            raise ValueError("You cant withdraw more than your balance")
        else:
            old_balance = self._balance
            self._balance -= amount

            ratio = self._balance / old_balance
            for asset_type in self._portfolio:
                self._portfolio[asset_type] *= ratio

            print(f"Successfully withdrawn. Your balance now is: {self._balance}")

    def project_yearly_growth(self, growth_rates):
        total_growth = 0

        for asset, amount in self._portfolio.items():
            if asset not in growth_rates:
                raise ValueError(f"Missing growth rate for {asset}")
            total_growth += amount * growth_rates[asset]

        return total_growth

if __name__ == "__main__":
    account1 = SavingsAccount(
        owner="Tim Cock",
        balance=150,
    )

    print(account1)
    account1.get_account_info()
    account1.get_balance()
    account1.apply_monthly_interest()
    account1.get_balance()
    account1.apply_monthly_interest()
    account1.get_balance()

    account1.get_account_info()
    try:
        account1.withdraw(160)
    except ValueError as e:
        print(e)
    account1.withdraw(55)

    print("\n")

    account2 = PremiumAccount(
        owner="Petr Blinov",
        balance=2000,
    )

    print(account2)
    account2.get_account_info()
    account2.get_balance()
    account2.withdraw(1000)
    account2.withdraw(700)

    try:
        account2.withdraw(5000)
    except ValueError as e:
        print(e)

    account2.withdraw(1200)

    try:
        account2.withdraw(100)
    except ValueError as e:
        print(e)

    print("\n")

    account3 = InvestmentAccount(
        owner="Bob Anus",
        balance=1000,
    )

    print(account3)

    try:
        print(f"Your total year growth: {account3.project_yearly_growth(
            {
                "stocks":0.10,
                "bonds":0.04,
                "crypto":0.07
            }
        )}")
    except ValueError as e:
        print(e)

    print(f"Your total year growth: {account3.project_yearly_growth(
        {
            "stocks": 0.10,
            "bonds": 0.04,
            "etf": 0.07
        }
    )}")


    account3.withdraw(100)
    account3.get_account_info()

    print("\n")
