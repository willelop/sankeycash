
from decimal import Decimal
from math import log10
from datetime import date, datetime, timedelta
from gnucash import Session,Split, GncNumeric, Account, ACCT_TYPE_TRADING, ACCT_TYPE_EXPENSE, ACCT_TYPE_INCOME

ZERO = Decimal(0)

class SankeyAccount():

    """Documentation for ClassName

    """
    def __init__(self,file):
        self.deep_level = 1
        self.income_name = "Income"
        self.expense_name = "Expenses"
        self.equity_name = "Equity"
        self.session = Session(file, True, False, False)
        self.root = self.session.book.get_root_account()
        self.book = self.session.book
        self.id_map = {}
        self.id_names = []
        self.generate_ids()

    def generate_ids(self):
        cnt = 0
        self.id_map[self.root.get_full_name()] = cnt
        self.id_names.append(self.root.get_full_name())
        desc = self.root.get_descendants()
        for test in desc:
            cnt += 1
            self.id_map[test.get_full_name()] = cnt
            self.id_names.append(test.get_full_name())

    def get_account_names(self):
        return self.id_names

    def get_root_commodity(self):
        return self.root.GetCommodity()

    def gnc_numeric_to_python_Decimal(self,numeric):
        negative = numeric.negative_p()
        if negative:
            sign = 1
        else:
            sign = 0
        copy = GncNumeric(numeric.num(), numeric.denom())
        result = copy.to_decimal(None)
        if not result:
            raise Exception("gnc numeric value %s can't be converted to decimal" %
                            copy.to_string() )
        digit_tuple = tuple( int(char)
                             for char in str(copy.num())
                             if char != '-' )
        denominator = copy.denom()
        exponent = int(log10(denominator))
        assert (10 ** exponent) == denominator
        return float(Decimal( (sign, digit_tuple, -exponent) ))

    """ get_flow """
    def get_flow(self, account):
        return self.gnc_numeric_to_python_Decimal(Account.GetBalanceChangeForPeriod(account,datetime(2021,2,1),datetime(2021,3,1),True))

    def get_balance(self, account):
        return self.gnc_numeric_to_python_Decimal(Account.GetBalanceInCurrency(account,self.get_root_commodity(),True))

    def get_childrenflows(self, account):
        sk_flows = []
        acc_names = []
        chlds = account.get_children()
        for acc in chlds:
            total = self.get_flow(acc)
            sk_flows.append(-total)
            acc_names.append(acc.get_full_name())
        return sk_flows,acc_names

    def set_deeplevel(self, level):
        self.deep_leve = level

    def get_account_id(self,account):
        return self.id_map[account.get_full_name()]

    def close_file(self):
        self.session.end()
        self.session.destroy()

    def get_all_accounts(self):
        incomes = root.lookup_by_name(self.income_name)
        chlds_inc = incomes.get_children()
        expenses = root.lookup_by_name(self.expense_name)
        chlds_exp = expenses.get_children()
        all_accounts = chlds_inc + chlds_exp

    def get_account_level(self,account,level):
        out_val = []
        if level == 0:
            return []
        chlds_inc = account.get_children()
        for acc in chlds_inc:
            flow = self.get_flow(acc)
            if flow != 0:
                out_val.append(acc)
                out_chld = self.get_account_level(acc, level-1)
                if len(out_chld) > 0:
                    out_val = out_val + out_chld
        return out_val

    def get_expenses(self):
        return self.get_account_level(self.root.lookup_by_name(self.expense_name),4)

    def get_income(self):
        return self.get_account_level(self.root.lookup_by_name(self.income_name),4)

    def get_income_account(self):
        return self.root.lookup_by_name(self.income_name)

    def get_expense_account(self):
        return self.root.lookup_by_name(self.expense_name)

    def get_all_accounts(self,depth_level):
        accounts = self.root.get_descendants()
        output = []
        for acc in accounts:
            if (acc.GetType() != ACCT_TYPE_TRADING and
                acc.GetType() != ACCT_TYPE_EXPENSE and
                acc.GetType() != ACCT_TYPE_INCOME  and
                acc.get_current_depth() <= depth_level) :
                output.append(acc)       
        return output
