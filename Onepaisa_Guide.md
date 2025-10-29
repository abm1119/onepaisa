# Complete Layman's Guide to Using 1Paisa Personal Finance CLI

Welcome! 1Paisa is a simple, colorful command-line tool to track your personal money, especially when lending or borrowing money from friends/family. It's like a digital notebook for your finances, but runs in your computer's terminal. No internet needed—everything stays on your device. Let's get you started step by step.

## 📋 What You'll Need
- A computer with **Windows, macOS, or Linux**.
- **Python 3.10 or higher** installed (check by opening Command Prompt/Terminal and typing `python --version`. If not installed, download from [python.org](https://www.python.org/)).
- Basic knowledge of opening a terminal/command prompt (like typing commands).

## 🚀 Step 1: Install and Set Up 1Paisa

### 1.1 Download the App
- The app is a Python project. If you have the files (e.g., from a ZIP or Git), navigate to the folder in your terminal.
- Example: If the folder is `C:\Users\YourName\Desktop\personal-finance-tracker`, open Command Prompt and type:
  ```
  cd C:\Users\YourName\Desktop\personal-finance-tracker
  ```

### 1.2 Create a Virtual Environment (Optional but Recommended)
This keeps things tidy. In your terminal:
```
python -m venv .venv
```
- Activate it:
  - Windows: `.venv\Scripts\activate`
  - macOS/Linux: `source .venv/bin/activate`
- You'll see `(.venv)` in your prompt when activated.

### 1.3 Install the App
Run this in the terminal (in the app's folder):
```
pip install -e .
```
- This installs 1Paisa as a command you can run anywhere.

### 1.4 Verify Installation
Type:
```
onepaisa --help
```
- You should see a list of commands. If not, check for errors and ensure Python is installed.

## 💼 Step 2: Get Started with Basic Setup

### 2.1 Initialize the Database
- This creates a local file to store your data.
- Run:
  ```
  onepaisa init
  ```
- Output: A colorful logo, confirmation message, and footer. Your data is now stored in `C:\Users\YourName\.onepaisa\onepaisa_db.sqlite` (or similar on other OS).

### 2.2 Add Your First Account
- Accounts are like "wallets" or bank accounts where money comes from/goes to.
- Example: Add a "Wallet" account:
  ```
  onepaisa account-add --name Wallet
  ```
- Output: Green panel confirming "Account Wallet added successfully! 💳"
- Add more if needed, e.g., `onepaisa account-add --name BankAccount`.

### 2.3 Add Contacts
- Contacts are people you lend/borrow from (friends, family, etc.).
- Example: Add a friend named Ali:
  ```
  onepaisa contact-add --name Ali --relation friend --tags college football --note "My best buddy"
  ```
- Options:
  - `--name`: Required, their name.
  - `--relation`: e.g., friend, mother, cousin (default: other).
  - `--tags`: Comma-separated keywords (e.g., college, football).
  - `--note`: Extra details.
- Output: Magenta panel with details.

- List all contacts:
  ```
  onepaisa contact-list
  ```
- Output: A blue table showing ID, Name, Relation, Tags, Note.

## 💰 Step 3: Track Lending and Borrowing

### 3.1 Lend Money
- When you give money to someone.
- Example: Lend $500 to Ali from your Wallet, due in 3 months:
  ```
  onepaisa lend --contact Ali --account Wallet --amount 500 --date 2024-10-01 --due 2025-01-01 --note "For groceries"
  ```
- Output: Red panel confirming the loan.
- This records it as an outgoing transaction.

### 3.2 Borrow Money
- When someone gives you money.
- Example: Borrow $200 from Ali via Wallet:
  ```
  onepaisa borrow --contact Ali --account Wallet --amount 200 --date 2024-10-02 --note "Emergency cash"
  ```
- Output: Green panel confirming.

### 3.3 Repay Money
- Pay back what you owe or collect what others owe.
- Example 1: Repay $100 to Ali (auto-applies to oldest loan):
  ```
  onepaisa repay --contact Ali --amount 100 --date 2024-10-03 --note "Partial payment"
  ```
- Output: Blue panel showing applied/unapplied amounts.

- Example 2: Repay a specific loan (if you know the ID from reports):
  ```
  onepaisa repay --contact Ali --amount 50 --loan_id 1 --date 2024-10-03
  ```
- If loan ID is wrong, you'll get an error panel.

## 📊 Step 4: View Reports and Summaries

### 4.1 Check a Contact's Summary
- See what you owe/lent to one person.
- Example: Ali's summary:
  ```
  onepaisa contact-summary --contact Ali
  ```
- Output: Magenta table with open amounts and net balance (positive = they owe you).

### 4.2 Global Contacts Report
- Overview of all contacts.
- Run:
  ```
  onepaisa contacts-report
  ```
- Output: Green table with each contact's balances, plus a grand total.

### 4.3 Aging Report
- See how long loans have been open (buckets: 0-30 days, etc.).
- Run:
  ```
  onepaisa aging
  ```
- Output: Red table with amounts per bucket.

### 4.4 Ask Simple Questions
- Get quick answers based on your data.
- Examples:
  ```
  onepaisa ask "how much I gave others this month"
  onepaisa ask "how much I borrowed this month"
  onepaisa ask "outstanding"
  ```
- Output: Blue panel with answer and explanation.
- Note: Limited to a few queries; it's rule-based, not AI.

### 4.5 Summary Command
- Currently under development. Use the other reports instead.

## 🛠️ Step 5: Advanced Tips and Troubleshooting

### 5.1 Custom Database Location
- By default, data is in `~/.onepaisa/onepaisa_db.sqlite`.
- Change it: Set environment variable `ONEPAISA_DB_PATH` to a custom path (e.g., `C:\MyData\finance.db`).

### 5.2 Common Issues
- **Command not found**: Ensure you're in the virtual environment and the app is installed. Try `python -m onepaisa` instead of `onepaisa`.
- **Contact/Account not found**: Add them first with `contact-add` or `account-add`.
- **Errors**: Check dates (use YYYY-MM-DD format) and amounts (positive numbers).
- **No output**: Run with `--help` to see options.

### 5.3 Backing Up Data
- Copy the SQLite file (`onepaisa_db.sqlite`) to a safe place.
- To reset: Delete the file and run `onepaisa init` again (loses all data).

### 5.4 Updating/Extending
- The app is open-source. Check `README.md` for more.
- Future: May add LLM for smarter "ask" (requires API key).

### 5.5 Sample Workflow
1. `onepaisa init`
2. `onepaisa account-add --name Wallet`
3. `onepaisa contact-add --name Mom --relation mother`
4. `onepaisa lend --contact Mom --account Wallet --amount 1000 --note "Gift"`
5. `onepaisa contacts-report`
6. `onepaisa ask "how much I gave others this month"`

## 🎉 You're All Set!
1Paisa is now your personal finance buddy. Track loans easily, stay organized, and manage money with friends/family. Every command ends with a fun footer crediting the creator.

For help: Run `onepaisa --help` or check the code's README. Enjoy! 💸

If you have questions, feel free to ask! 🚀