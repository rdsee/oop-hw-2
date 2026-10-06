from abc import ABC, abstractmethod
import uuid

class AccountFrozenError(Exception):
    pass

class AccountClosedError(Exception):
    pass

class InvalidOperationError(Exception):
    pass

class InsufficientFundsError(Exception):
    pass


class AbstractAccount(ABC):
    def __init__(self, wallet_id, account_type, owner, balance, wallet_status="active", currency="USD"):
        self.wallet_id = wallet_id
        self.owner = owner
        self._balance = balance
        self.account_type = account_type
        self.wallet_status = wallet_status
        self.currency = currency

    @abstractmethod
    def __str__(self):
        ...

    @abstractmethod
    def deposit(self, amount):
        ...

    @abstractmethod
    def withdraw(self, amount):
        ...

    @abstractmethod
    def get_account_info(self):
        ...

class BankAccount(AbstractAccount):
    def __init__(self, wallet_id=None, account_type="bank account", owner=None, balance=0, wallet_status="active", currency="USD"):
        self.validate_balance(balance)
        super().__init__(wallet_id, account_type, owner, balance, wallet_status, currency)
        self.currency = currency

        allowed_currency = {"USD", "EUR", "GBP"}

        if self.owner is None:
            raise InvalidOperationError("Name cannot be empty")

        if self.currency not in allowed_currency:
            raise InvalidOperationError(f"Currency {currency} is not supported")

        if self.wallet_id is None:
            self.wallet_id = uuid.uuid4().hex[:6]

    def __str__(self):
        return (f"account type: {self.account_type} |"
                f" client: {self.owner} |"
                f" last 4 characters of the ID: ...{self.wallet_id[-4:]} |"
                f" wallet status: {self.wallet_status} |"
                f" balance: {self._balance} {self.currency} |"
                )

    def validate_balance(self, balance):
        if isinstance(balance, bool) or not isinstance(balance, (int, float)):
            raise InvalidOperationError("Balance must be a number.")
        elif balance != balance:
            raise InvalidOperationError("Balance cannot be NaN.")
        elif balance == float("inf") or balance == float("-inf"):
            raise InvalidOperationError("Balance cannot be inf or -inf.")
        elif balance < 0:
            raise InvalidOperationError("Balance cannot be negative.")

    def validate_amount(self, amount):
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise InvalidOperationError("Amount must be a number.")
        elif amount != amount:
            raise InvalidOperationError("Amount cannot be NaN.")
        elif amount == float("inf") or amount == float("-inf"):
            raise InvalidOperationError("Amount cannot be inf or -inf.")
        elif amount <= 0:
            raise InvalidOperationError("Amount cannot be negative.")

    def check_status(self):
        if self.wallet_status == "frozen":
            raise AccountFrozenError("Bank account is frozen")

        elif self.wallet_status == "closed":
            raise AccountClosedError("Bank account is closed")

        elif self.wallet_status != "active":
            raise InvalidOperationError(f"Invalid status")

    def deposit(self, amount):
        self.check_status()
        self.validate_amount(amount)

        self._balance += amount
        return f"Successfully deposited. Your balance now is {self._balance} {self.currency}"

    def withdraw(self, amount):
        self.check_status()
        self.validate_amount(amount)

        if amount <= 0:
            raise InvalidOperationError("You cannot withdraw zero money")
        if amount > self._balance:
            raise InsufficientFundsError("You cannot withdraw more than you have")
        else:
            self._balance -= amount
            return f"Successfully withdrawn. Your balance now is {self._balance} {self.currency}"

    def get_balance(self):
        return f"Your balance is {self._balance} {self.currency}"

    def get_account_info(self):
        return (f"Name: {self.owner}, "
                f"ID: {self.wallet_id}, "
                f"Balance: {self._balance} {self.currency}, "
                f"Account type: {self.account_type}, "
                f"Wallet status: {self.wallet_status}")

class SavingsAccount(BankAccount):
    def __init__(self, wallet_id=None, account_type="savings account", owner=None, balance=0, wallet_status="active", min_balance=100, monthly_interest_rate=2, currency="USD"):
        super().__init__(wallet_id, account_type, owner, balance, wallet_status, currency)
        self._min_balance = min_balance
        self._monthly_interest_rate = monthly_interest_rate

        if balance < min_balance:
            raise InsufficientFundsError(f"Your balance cant be less than {min_balance}")

        if account_type != "savings account":
            raise InvalidOperationError("Invalid account type")

    def __str__(self):
        return (f"account type: {self.account_type} |"
                f" client: {self.owner} |"
                f" last 4 characters of the ID: ...{self.wallet_id[-4:]} |"
                f" wallet status: {self.wallet_status} |"
                f" balance: {self._balance} {self.currency} |"
                f" min balance: {self._min_balance} |"
                f"monthly interest rate: {self._monthly_interest_rate}%"
                )

    def get_account_info(self):
        return (f"Name: {self.owner}, "
                f"ID: {self.wallet_id}, "
                f"Balance: {self._balance} {self.currency}, "
                f"Account type: {self.account_type}, "
                f"Wallet status: {self.wallet_status}, "
                f"Your interest rate: {self._monthly_interest_rate}%")

    def get_balance(self):
        return super().get_balance()

    def apply_monthly_interest(self):
        self.check_status()

        self._balance += self._balance * (self._monthly_interest_rate / 100)
        return f"Your balance including monthly interest is {self._balance} {self.currency}"

    def deposit(self, amount):
        self.check_status()
        self.validate_amount(amount)

        return super().deposit(amount)

    def withdraw(self, amount):
        self.check_status()
        self.validate_amount(amount)

        if amount <= 0:
            raise InvalidOperationError("Your withdrawal amount must be greater than zero")
        elif self._balance - amount < self._min_balance:
            raise InsufficientFundsError(f"Your balance cannot be less than {self._min_balance}")
        else:
            self._balance -= amount
            return f"Successfully withdrawn. Your balance now is {self._balance} {self.currency}"

class PremiumAccount(BankAccount):
    def __init__(self, wallet_id=None, account_type="premium account", owner=None, balance=0, wallet_status="active", withdraw_limit=3000, overdraft_limit=-1000, commission=10, currency="USD"):
        super().__init__(wallet_id, account_type, owner, balance, wallet_status, currency)
        self._withdraw_limit = withdraw_limit
        self._overdraft_limit = overdraft_limit
        self._commission = commission

        if account_type != "premium account":
            raise InvalidOperationError("Invalid account type")

    def __str__(self):
        return (f"account type: {self.account_type} | "
                f"client: {self.owner} | "
                f"last 4 characters of the ID: ...{self.wallet_id[-4:]} |"
                f"wallet status: {self.wallet_status} | "
                f"balance: {self._balance} {self.currency} | "
                f"withdraw limit: {self._withdraw_limit} | "
                f"overdraft limit (minimal balance): {self._overdraft_limit} | "
                f"commission: {self._commission}"
                )

    def get_account_info(self):
        return (f"Name: {self.owner}, "
                f"ID: {self.wallet_id}, "
                f"Balance: {self._balance} {self.currency}, "
                f"Account type: {self.account_type}, "
                f"wallet status: {self.wallet_status}, "
                f"withdraw limit: {self._withdraw_limit}, "
                f"overdraft limit: {self._overdraft_limit}, "
                f"commission: {self._commission}")

    def get_balance(self):
        return super().get_balance()

    def withdraw(self, amount):
        self.check_status()
        self.validate_amount(amount)

        if amount <= 0:
            raise InvalidOperationError("Your withdrawal amount must be greater than zero")

        elif amount > self._withdraw_limit:
            raise InvalidOperationError(f"You cannot withdraw more than {self._withdraw_limit}")

        elif self._balance - (amount + self._commission) < self._overdraft_limit:
            raise InsufficientFundsError(f"Your balance cannot be less than {self._overdraft_limit}")

        else:
            self._balance = self._balance - (amount + self._commission)
            return f"Successfully withdrawn. Your balance now is {self._balance} {self.currency}"

    def deposit(self, amount):
        self.check_status()
        self.validate_amount(amount)

        return super().deposit(amount)


class InvestmentAccount(BankAccount):
    ALLOWED_ASSETS = {"stocks", "bonds", "etf"}

    def __init__(self, wallet_id=None, account_type="investment account", owner=None, balance=0, wallet_status="active", portfolio=None, currency="USD"):
        super().__init__(wallet_id, account_type, owner, balance, wallet_status, currency)

        if account_type != "investment account":
            raise InvalidOperationError("Invalid account type")

        if portfolio is None:
            portfolio = {
                "stocks": self._balance / 2,
                "bonds": self._balance / 4,
                "etf": self._balance / 4,
            }

        self._portfolio = dict(portfolio)

        for asset_type, amount in self._portfolio.items():
            if asset_type not in self.ALLOWED_ASSETS:
                raise InvalidOperationError("Invalid asset type")
            if amount <= 0:
                raise InvalidOperationError("Investment amount must be positive")

        if sum(self._portfolio.values()) != self._balance:
            raise InvalidOperationError("Portfolio total must equal total balance")

    def __str__(self):
        return (f"last 4 characters of ID: ...{self.wallet_id[-4:]} | "
                f"account type: {self.account_type} | "
                f"wallet status: {self.wallet_status} | "
                f"owner: {self.owner} | "
                f"balance: {self._balance} {self.currency} | "
                f"portfolio: {self._portfolio}")

    def get_account_info(self):
        return (f"name: {self.owner}, id: {self.wallet_id}, "
                f"balance: {self._balance} {self.currency}, "
                f"account type: {self.account_type}, wallet status: {self.wallet_status}, "
                f"portfolio: {self._portfolio}")

    def get_balance(self):
        return super().get_balance()

    def withdraw(self, amount):
        self.check_status()
        self.validate_amount(amount)

        if amount <= 0:
            raise InvalidOperationError("Your withdrawal amount must be greater than zero")
        elif amount > self._balance:
            raise InsufficientFundsError("You cannot withdraw more than your balance")
        else:
            old_balance = self._balance
            self._balance -= amount

            ratio = self._balance / old_balance
            for asset_type in self._portfolio:
                self._portfolio[asset_type] *= ratio

            return f"Successfully withdrawn. Your balance now is {self._balance} {self.currency}"

    def deposit(self, amount):
        self.check_status()
        self.validate_amount(amount)

        old_balance = self._balance
        self._balance += amount

        ratio = self._balance / old_balance
        for asset_type in self._portfolio:
            self._portfolio[asset_type] *= ratio

    def project_yearly_growth(self, growth_rates):
        self.check_status()

        total_growth = 0

        for asset, amount in self._portfolio.items():
            if asset not in growth_rates:
                raise InvalidOperationError(f"Missing growth rate for {asset}")
            total_growth += amount * growth_rates[asset]

        return total_growth

if __name__ == "__main__":

    try:
        account1 = SavingsAccount(
            owner="Tim Cock",
            balance=150,
            wallet_status="frozen",
            currency = "USD"
        )
    except InvalidOperationError as e:
        print(e)


    print(account1)
    print(account1.get_account_info())
    print(account1.get_balance())
    try:
        print(account1.apply_monthly_interest())
    except AccountFrozenError as e:
        print(e)

    print(account1.get_balance())

    account1.wallet_status = "active"
    print(account1.get_account_info())
    print(account1.apply_monthly_interest())
    print(account1.get_balance())
    try:
        print(account1.deposit(float("nan")))
    except InvalidOperationError as e:
        print(e)

    try:
        print(account1.deposit(1000))
    except AccountFrozenError as e:
        print(e)

    try:
        print(account1.withdraw(5))
    except AccountFrozenError as e:
        print(e)

    print("\n")

    account2 = PremiumAccount(
        owner="Petr Blinov",
        balance=2000,
    )

    print(account2)
    print(account2.get_account_info())
    print(account2.get_balance())
    print(account2.withdraw(1000))
    print(account2.withdraw(700))

    try:
        account2.withdraw(5000)
    except (InvalidOperationError, InsufficientFundsError) as e:
        print(e)

    print(account2.withdraw(1200))

    try:
        account2.withdraw(100)
    except (InvalidOperationError, InsufficientFundsError) as e:
        print(e)

    print("\n")

    account3 = InvestmentAccount(
        owner="Bob",
        balance=1000,
        portfolio={
            "stocks": 500,
            "bonds": 250,
            "etf": 250
        }
    )

    try:
        account4 = InvestmentAccount(
            owner="Bob Anus",
            balance=1000,
            portfolio={
                "stocks": 500,
                "bonds": 250,
                "crypto": 250
            }
        )
    except InvalidOperationError as e:
        print(e)

    try:
        account5 = InvestmentAccount(
            owner="Bob Penis",
            balance=1000,
            portfolio={
                "stocks": -500,
                "bonds": 250,
                "etf": 250
            }
        )
    except InvalidOperationError as e:
        print(e)

    print(account3)

    try:
        print(f"Your total year growth: {account3.project_yearly_growth(
            {
                "stocks":0.10,
                "bonds":0.04,
                "crypto":0.07
            }
        )}")
    except InvalidOperationError as e:
        print(e)

    print(f"Your total year growth: {account3.project_yearly_growth(
        {
            "stocks": 0.10,
            "bonds": 0.04,
            "etf": 0.07
        }
    )}")

    try:
        print(account3.withdraw(1100))
    except (InsufficientFundsError) as e:
        print(e)

    print(account3.get_account_info())

    print("\n")
