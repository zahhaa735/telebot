
import telebot
from telebot import types
import json

bot = telebot.TeleBot('6260583908:AAFxl3PryrpRwFu9_XnkxanbttCkfWhPvr8')

# Hardcoded categories
categories = ['Food', 'Transport', 'Entertainment', 'Bills', 'Other']

# Load data from file
try:
    with open('data.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    data = {'income': [], 'expenses': []}


# Save data to file
def save_data():
    with open('data.json', 'w') as f:
        json.dump(data, f)


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    bot.send_message(user_id, "Привіт! Я телеграмбот для ведення доходів і витрат. "
                              "Я можу допомогти вам контролювати свої фінанси. Ось що я вмію:\n"
                              "/add_expense - додати витрати, вказуючи категорію\n"
                              "/add_income - додати доходи, вказуючи категорію доходів\n"
                              "/view_expenses - переглянути всі витрати\n"
                              "/view_income - переглянути всі доходи\n"
                              "/delete_expense - видалити витрати\n"
                              "/delete_income - видалити доходи\n"
                              "/view_statistics - переглянути статистику доходів та витрат за категоріями за день, "
                              "місяць, тиждень та рік.\n"
                              "/help - показати цю інструкцію")


# /help
@bot.message_handler(commands=["help"])
def help(message):

    user_id = message.from_user.id

    bot.send_message(user_id, "Ось що я вмію:\n"
                              "/add_expense - додати витрати, вказуючи категорію\n"
                              "/add_income - додати доходи, вказуючи категорію доходів\n"
                              "/view_expenses - переглянути всі витрати\n"
                              "/view_income - переглянути всі доходи\n"
                              "/delete_expense - видалити витрати\n"
                              "/delete_income - видалити доходи\n"
                              "/view_statistics - переглянути статистику доходів та витрат за категоріями за день, "
                              "місяць, тиждень та рік.\n"
                              "/help - показати цю інструкцію")


# Add expense
@bot.message_handler(commands=['add_expense'])
def add_expense(message):
    msg = bot.send_message(message.chat.id, 'Enter the amount and category (e.g. 10 Food)')
    bot.register_next_step_handler(msg, process_expense)


def process_expense(message):
    try:
        amount, category = message.text.split()
        amount = float(amount)
        if category not in categories:
            bot.send_message(message.chat.id, 'Invalid category. Available categories: ' + ', '.join(categories))
            return
        data['expenses'].append({'amount': amount, 'category': category})
        save_data()
        bot.send_message(message.chat.id, 'Expense added successfully')
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid format. Please enter the amount and category (e.g. 10 Food)')


# Add income
@bot.message_handler(commands=['add_income'])
def add_income(message):
    msg = bot.send_message(message.chat.id, 'Enter the amount and category (e.g. 100 Salary)')
    bot.register_next_step_handler(msg, process_income)


def process_income(message):
    try:
        amount, category = message.text.split()
        amount = float(amount)
        data['income'].append({'amount': amount, 'category': category})
        save_data()
        bot.send_message(message.chat.id, 'Income added successfully')
    except ValueError:
        bot.send_message(message.chat.id, 'Invalid format. Please enter the amount and category (e.g. 100 Salary)')


# View expenses
@bot.message_handler(commands=['view_expenses'])
def view_expenses(message):
    if not data['expenses']:
        bot.send_message(message.chat.id, 'No expenses recorded')
        return
    expenses = '\n'.join([f"{expense['amount']} {expense['category']}" for expense in data['expenses']])
    bot.send_message(message.chat.id, f"Expenses:\n{expenses}")


# View income
@bot.message_handler(commands=['view_income'])
def view_income(message):
    if not data['income']:
        bot.send_message(message.chat.id, 'No income recorded')
        return
    income = '\n'.join([f"{income['amount']} {income['category']}" for income in data['income']])
    bot.send_message(message.chat.id, f"Income:\n{income}")


# Delete expense
@bot.message_handler(commands=['delete_expense'])
def delete_expense(message):
    if not data['expenses']:
        bot.send_message(message.chat.id, 'No expenses recorded')
        return
    keyboard = types.InlineKeyboardMarkup()
    for i, expense in enumerate(data['expenses']):
        keyboard.add(types.InlineKeyboardButton(text=f"{expense['amount']} {expense['category']}", callback_data=f"delete_expense_{i}"))
    bot.send_message(message.chat.id, "Select an expense to delete", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_expense_'))
def process_delete_expense(call):
    index = int(call.data.split('_')[2])
    del data['expenses'][index]
    save_data()
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Expense deleted successfully")


# Delete income
@bot.message_handler(commands=['delete_income'])
def delete_income(message):
    if not data['income']:
        bot.send_message(message.chat.id, 'No income recorded')
        return
    keyboard = types.InlineKeyboardMarkup()
    for i, income in enumerate(data['income']):
        keyboard.add(types.InlineKeyboardButton(text=f"{income['amount']} {income['category']}", callback_data=f"delete_income_{i}"))
    bot.send_message(message.chat.id, "Select an income to delete", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_income_'))
def process_delete_income(call):
    index = int(call.data.split('_')[2])
    del data['income'][index]
    save_data()
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Income deleted successfully")


# View statistics
@bot.message_handler(commands=['view_statistics'])
def view_statistics(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Income", callback_data="view_statistics_income"))
    keyboard.add(types.InlineKeyboardButton(text="Expenses", callback_data="view_statistics_expenses"))
    bot.send_message(message.chat.id, "Select a category to view statistics", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('view_statistics_'))
def process_view_statistics(call):
    category = call.data.split('_')[2]
    if category == 'income':
        if not data['income']:
            bot.send_message(call.message.chat.id, 'No income recorded')
            return
        total_income = sum([income['amount'] for income in data['income']])
        income_by_category = {}
        for income in data['income']:
            if income['category'] not in income_by_category:
                income_by_category[income['category']] = 0
            income_by_category[income['category']] += income['amount']
        income_by_category_str = '\n'.join([f"{category}: {amount}" for category, amount in income_by_category.items()])
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Total income: {total_income}\nIncome by category:\n{income_by_category_str}")
    elif category == 'expenses':
        if not data['expenses']:
            bot.send_message(call.message.chat.id, 'No expenses recorded')
            return
        total_expenses = sum([expense['amount'] for expense in data['expenses']])
        expenses_by_category = {}
        for expense in data['expenses']:
            if expense['category'] not in expenses_by_category:
                expenses_by_category[expense['category']] = 0
            expenses_by_category[expense['category']] += expense['amount']
        expenses_by_category_str = '\n'.join([f"{category}: {amount}" for category, amount in expenses_by_category.items()])
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Total expenses: {total_expenses}\nExpenses by category:\n{expenses_by_category_str}")


def run():
    bot.polling()


if __name__ == '__main__':
    run()
