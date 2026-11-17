"""
Expense Tracker
A simple command-line app to track daily expenses.
Built with Python and SQLite.

Features: add, view, edit, delete expenses,
category-wise totals and monthly totals.
"""

import sqlite3
from datetime import date, datetime

DB_NAME = "expenses.db"


# ---------- Database setup ----------

def create_table(conn):
    """Create the expenses table if it does not exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT
        )
        """
    )
    conn.commit()


# ---------- Input helpers (validation) ----------

def get_amount(prompt="Amount: "):
    """Keep asking until the user enters a valid positive number."""
    while True:
        try:
            amount = float(input(prompt))
            if amount <= 0:
                print("Amount must be greater than 0.")
                continue
            return amount
        except ValueError:
            print("Please enter a valid number.")


def get_category(prompt="Category (food/travel/etc): "):
    """Keep asking until the user enters a non-empty category."""
    while True:
        category = input(prompt).strip().lower()
        if category:
            return category
        print("Category cannot be empty.")


def get_expense_id(conn, prompt="Enter expense ID: "):
    """Ask for an ID and check that it exists. Returns None if invalid."""
    try:
        expense_id = int(input(prompt))
    except ValueError:
        print("ID must be a number.")
        return None

    row = conn.execute(
        "SELECT id FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()
    if row is None:
        print("No expense found with that ID.")
        return None
    return expense_id


# ---------- Main features ----------

def add_expense(conn):
    """Add a new expense with today's date."""
    amount = get_amount()
    category = get_category()
    note = input("Note (optional): ").strip()
    today = date.today().strftime("%Y-%m-%d")

    conn.execute(
        "INSERT INTO expenses (amount, category, date, note) VALUES (?, ?, ?, ?)",
        (amount, category, today, note),
    )
    conn.commit()
    print("Expense added!")


def view_expenses(conn):
    """Show all expenses."""
    rows = conn.execute(
        "SELECT id, amount, category, date, note FROM expenses ORDER BY id"
    ).fetchall()

    if not rows:
        print("No expenses yet.")
        return

    print("\nID | Amount | Category | Date | Note")
    print("-" * 45)
    for expense_id, amount, category, exp_date, note in rows:
        print(f"{expense_id} | Rs.{amount:.2f} | {category} | {exp_date} | {note or ''}")


def category_totals(conn):
    """Show the total spent in each category."""
    rows = conn.execute(
        "SELECT category, SUM(amount) FROM expenses GROUP BY category"
    ).fetchall()

    if not rows:
        print("No expenses yet.")
        return

    print("\nCategory-wise total:")
    for category, total in rows:
        print(f"{category}: Rs.{total:.2f}")


def monthly_total(conn):
    """Show the total spent in a given month."""
    month = input("Month (YYYY-MM, e.g. 2026-11): ").strip()

    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid format. Please use YYYY-MM, like 2026-11.")
        return

    total = conn.execute(
        "SELECT SUM(amount) FROM expenses WHERE date LIKE ?", (month + "%",)
    ).fetchone()[0]

    if total is None:
        total = 0
    print(f"Total for {month}: Rs.{total:.2f}")


def edit_expense(conn):
    """Edit an existing expense. Press Enter to keep the old value."""
    view_expenses(conn)
    expense_id = get_expense_id(conn)
    if expense_id is None:
        return

    old_amount, old_category, old_note = conn.execute(
        "SELECT amount, category, note FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()

    print("Press Enter to keep the old value.")

    amount_text = input(f"New amount [{old_amount}]: ").strip()
    if amount_text == "":
        amount = old_amount
    else:
        try:
            amount = float(amount_text)
            if amount <= 0:
                print("Amount must be greater than 0. Edit cancelled.")
                return
        except ValueError:
            print("Invalid number. Edit cancelled.")
            return

    category = input(f"New category [{old_category}]: ").strip().lower()
    if category == "":
        category = old_category

    note = input(f"New note [{old_note or ''}]: ").strip()
    if note == "":
        note = old_note

    conn.execute(
        "UPDATE expenses SET amount = ?, category = ?, note = ? WHERE id = ?",
        (amount, category, note, expense_id),
    )
    conn.commit()
    print("Expense updated!")


def delete_expense(conn):
    """Delete an expense after asking for confirmation."""
    view_expenses(conn)
    expense_id = get_expense_id(conn)
    if expense_id is None:
        return

    confirm = input("Are you sure you want to delete it? (y/n): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        return

    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    print("Expense deleted!")


# ---------- Program start ----------

def main():
    conn = sqlite3.connect(DB_NAME)
    create_table(conn)

    while True:
        print("\n===== Expense Tracker =====")
        print("1. Add expense")
        print("2. View expenses")
        print("3. Category-wise total")
        print("4. Monthly total")
        print("5. Edit expense")
        print("6. Delete expense")
        print("7. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            add_expense(conn)
        elif choice == "2":
            view_expenses(conn)
        elif choice == "3":
            category_totals(conn)
        elif choice == "4":
            monthly_total(conn)
        elif choice == "5":
            edit_expense(conn)
        elif choice == "6":
            delete_expense(conn)
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-7.")

    conn.close()


if __name__ == "__main__":
    main()