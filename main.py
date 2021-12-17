import csv
import datetime
import logging
import os
import sys

from datetime import datetime, timezone
from dotenv import load_dotenv
from splitwise import Splitwise, Expense
from splitwise.user import ExpenseUser


def main(file_path):
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    sw = Splitwise(
        consumer_key=os.getenv('CONSUMER_KEY'),
        consumer_secret=os.getenv('CONSUMER_SECRET'),
        api_key=os.getenv('API_KEY'))

    # create expenses using CSV
    created_expenses = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        count = 0
        for row in reader:
            expense = Expense()
            expense.setCost(row['cost'])
            expense.setDate(datetime.fromisoformat(row['date']).astimezone(timezone.utc))
            expense.setDescription(row['description'])

            user1 = ExpenseUser()
            user1.setId(row['user1_id'])
            user1.setPaidShare(row['user1_paid_share'])
            user1.setOwedShare(row['user1_owed_share'])
            user2 = ExpenseUser()
            user2.setId(row['user2_id'])
            user2.setPaidShare(row['user2_paid_share'])
            user2.setOwedShare(row['user2_owed_share'])
            expense.addUser(user1)
            expense.addUser(user2)

            created_expense, errors = sw.createExpense(expense)
            if errors:
                for msg in errors.errors['base']:
                    logging.error(msg)
            else:
                created_expenses.append(created_expense.getId())
                count += 1
                logging.info('created expense {} ({})'.format(created_expense.getId(), count))

        input('press enter to delete {} created expense(s)'.format(len(created_expenses)))
        for expense_id in created_expenses:
            success, errors = sw.deleteExpense(expense_id)
            if errors:
                logging.error('unable to delete expense id {}'.format(expense_id), errors)
            else:
                logging.info('deleted expense {}'.format(expense_id))


if __name__ == '__main__':
    file_path = 'example.csv'
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    main(file_path)
