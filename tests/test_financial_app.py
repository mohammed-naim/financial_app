import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

class FinancialAppTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(30)
        cls.driver.maximize_window()
        cls.driver.get("http://localhost:5000")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_01_create_and_login_user(self):
        driver = self.driver

        # Sign up
        driver.find_element(By.LINK_TEXT, "Create Account").click()
        driver.find_element(By.ID, "fullName").send_keys("Test User")
        driver.find_element(By.ID, "email").send_keys("testuser16@example.com")
        driver.find_element(By.ID, "password").send_keys("password")
        driver.find_element(By.ID, "confirm_password").send_keys("password")
        driver.find_element(By.ID, "btn-create-account").click()
        time.sleep(2)
        # Wait for redirection to dashboard
        WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))
        time.sleep(2)
        # Log out
        driver.find_element(By.LINK_TEXT, "Logout").click()
        time.sleep(2)
        # Log in
        driver.find_element(By.ID, "email").send_keys("testuser16@example.com")
        driver.find_element(By.ID, "password").send_keys("password")
        driver.find_element(By.ID, "btn-login").click()
        time.sleep(2)
        # Wait for redirection to dashboard
        WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))

    def test_02_crud_on_account(self):
        driver = self.driver

        # Navigate to Accounts
        driver.find_element(By.LINK_TEXT, "Accounts").click()
        time.sleep(2)
        # Create Account
        driver.find_element(By.ID, "btn-add-account").click()
        time.sleep(2)
        driver.find_element(By.ID, "accountName").send_keys("Test Account")
        driver.find_element(By.ID, "initialBalance").send_keys("1000")
        driver.find_element(By.ID, "currency").send_keys("USD")
        driver.find_element(By.ID, "btn-submit-add-account").click()
        time.sleep(2)

        # Edit Account
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='showEditAccountModal']").click()
        time.sleep(2)
        driver.find_element(By.ID, "editAccountName").clear()
        driver.find_element(By.ID, "editAccountName").send_keys("Updated Account")
        driver.find_element(By.ID, "btn-submit-edit-account").click()
        time.sleep(2)

        # Delete Account
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='confirmDeleteAccount']").click()
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, "#customConfirmOk").click()
        time.sleep(2)

    def test_03_croud_on_categories(self):
        driver = self.driver

        # Navigate to Categories
        driver.find_element(By.LINK_TEXT, "Categories").click()
        time.sleep(2)
        # Create Category
        driver.find_element(By.ID, "btn-add-category").click()
        time.sleep(2)
        driver.find_element(By.ID, "categoryName").send_keys("Test Category")
        driver.find_element(By.ID, "categoryType").send_keys("expense")
        driver.find_element(By.ID, "btn-submit-add-category").click()
        time.sleep(2)

        # Edit Category
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='openEditCategoryModal']").click()
        time.sleep(2)
        driver.find_element(By.ID, "editCategoryName").clear()
        driver.find_element(By.ID, "editCategoryName").send_keys("Updated Category")
        driver.find_element(By.ID, "btn-submit-edit-category").click()
        time.sleep(2)

        # Delete Category
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='confirmDeleteCategory']").click()
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, "#customConfirmOk").click()
        time.sleep(2)

    def test_04_crud_on_transactions_and_repeated_transactions(self):
        driver = self.driver

        # Navigate to Transactions
        driver.find_element(By.LINK_TEXT, "Transactions").click()
        time.sleep(2)
        # Create Transaction
        driver.find_element(By.ID, "btn-add-transaction").click()
        time.sleep(2)
        driver.find_element(By.ID, "transactionDescription").send_keys("Test Transaction")
        driver.find_element(By.ID, "transactionAmount").send_keys("100")
        driver.find_element(By.ID, "transactionCategory").send_keys("expense")
        driver.find_element(By.ID, "transactionAccount").send_keys("Test Account")
        driver.find_element(By.ID, "transactionDate").send_keys("03/02/2025")
        driver.find_element(By.ID, "btn-submit-add-transaction").click()
        time.sleep(2)

        # Edit Transaction
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='openEditTransactionModal']").click()
        time.sleep(2)
        driver.find_element(By.ID, "editTransactionDescription").clear()
        driver.find_element(By.ID, "editTransactionDescription").send_keys("Updated Transaction")
        driver.find_element(By.ID, "btn-submit-edit-transaction").click()
        time.sleep(2)

        # Delete Transaction
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='confirmDeleteTransaction']").click()
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, "#customConfirmOk").click()
        time.sleep(2)

        # Create Repeated Transaction
        driver.find_element(By.ID, "repeated-transactions-tab").click()
        time.sleep(2)
        driver.find_element(By.ID, "btn-add-repeated-transaction2").click()
        time.sleep(2)
        driver.find_element(By.ID, "repeatedDescription").send_keys("Test Repeated Transaction")
        driver.find_element(By.ID, "repeatedAmount").send_keys("100")
        driver.find_element(By.ID, "repeatedCategory").send_keys("expense")
        driver.find_element(By.ID, "repeatedAccount").send_keys("Test Account")
        driver.find_element(By.ID, "repeatedStartDate").send_keys("03/02/2025")
        driver.find_element(By.ID, "repeatedEndDate").send_keys("03/02/2026")
        driver.find_element(By.ID, "btn-submit-add-repeated-transaction").click()
        time.sleep(2)
        driver.refresh()
        time.sleep(1)
        driver.find_element(By.ID, "repeated-transactions-tab").click()
        time.sleep(1)

        # Edit Repeated Transaction
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='openEditRepeatedTransactionModal']").click()
        time.sleep(2)
        driver.find_element(By.ID, "repeatedDescription").clear()
        driver.find_element(By.ID, "repeatedDescription").send_keys("Updated Repeated Transaction")
        driver.find_element(By.ID, "btn-submit-add-repeated-transaction").click()
        time.sleep(2)

        # Delete Repeated Transaction
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='confirmDeleteRepeatedTransaction']").click()
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, "#customConfirmOk").click()
        time.sleep(2)

    def test_05_crud_on_debts_and_debt_payments(self):
        driver = self.driver

        # Navigate to Debts
        driver.find_element(By.LINK_TEXT, "Debts").click()
        time.sleep(2)
        # Create Debt
        driver.find_element(By.ID, "btn-add-debt").click()
        time.sleep(2)
        driver.find_element(By.ID, "personName").send_keys("John Doe")
        driver.find_element(By.ID, "amount").send_keys("500")
        driver.find_element(By.ID, "type").send_keys("creditor")
        driver.find_element(By.ID, "accountSelect").send_keys("Test Account")
        driver.find_element(By.ID, "btn-submit-add-debt").click()
        time.sleep(2)

        # Edit Debt
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='editDebt']").click()
        time.sleep(2)
        driver.find_element(By.ID, "personName").clear()
        driver.find_element(By.ID, "personName").send_keys("Jane Doe")
        driver.find_element(By.ID, "btn-submit-add-debt").click()
        time.sleep(2)
        

        # Delete Debt
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='confirmDeleteDebt']").click()
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, "#customConfirmOk").click()
        time.sleep(2)
        
        # Create Debt with Payment
        driver.find_element(By.ID, "btn-add-debt").click()
        time.sleep(2)
        driver.find_element(By.ID, "personName").send_keys("John Doe")
        driver.find_element(By.ID, "amount").send_keys("500")
        driver.find_element(By.ID, "type").send_keys("creditor")
        driver.find_element(By.ID, "accountSelect").send_keys("Test Account")
        driver.find_element(By.ID, "btn-submit-add-debt").click()
        time.sleep(2)

        # Create Debt Payment
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='showPayments']").click()
        time.sleep(2)
        driver.find_element(By.ID, "paymentAmount").send_keys("100")
        driver.find_element(By.ID, "paymentDate").send_keys("03/02/2025")
        driver.find_element(By.ID, "paymentAccountSelect").send_keys("Test Account")
        driver.find_element(By.ID, "btn-submit-add-payment").click()
        time.sleep(2)

        # Edit Debt Payment
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='openEditPaymentModal']").click()
        time.sleep(2)
        driver.find_element(By.ID, "editPaymentAmount").clear()
        driver.find_element(By.ID, "editPaymentAmount").send_keys("150")
        driver.find_element(By.ID, "btn-submit-edit-payment").click()
        time.sleep(2)

        # Delete Debt Payment
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='confirmDeletePayment']").click()
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, "#customConfirmOk").click()
        time.sleep(2)

    def test_06_crud_on_investments(self):
        driver = self.driver

        # Navigate to Investments
        driver.get("http://localhost:5000/investments")
        # driver.find_element(By.LINK_TEXT, "Investments").click()
        time.sleep(2)
        # Create Investment
        driver.find_element(By.ID, "btn-add-investment").click()
        time.sleep(2)
        driver.find_element(By.ID, "investmentAccount").send_keys("Test Account")
        driver.find_element(By.ID, "investmentCurrency").send_keys("USD")
        driver.find_element(By.ID, "amountInvested").send_keys("1000")
        driver.find_element(By.ID, "purchasePrice").send_keys("0.3")
        driver.find_element(By.ID, "investmentDescription").send_keys("Test Investment")
        driver.find_element(By.ID, "btn-submit-add-investment").click()
        time.sleep(2)

        # Edit Investment
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='editInvestment']").click()
        time.sleep(2)
        driver.find_element(By.ID, "editDescription").clear()
        driver.find_element(By.ID, "editDescription").send_keys("Updated Investment")
        driver.find_element(By.ID, "btn-submit-edit-investment").click()
        time.sleep(2)

        # Delete Investment
        driver.find_element(By.CSS_SELECTOR, "button[onclick*='confirmDeleteInvestment']").click()
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, "#customConfirmOk").click()
        time.sleep(2)

if __name__ == "__main__":
    unittest.main()