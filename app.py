from flask import Flask, request, url_for, redirect, render_template, g, flash
import sqlite3
import pdb

app = Flask(__name__)
app.config["SECRET_KEY"] = "Something"

app_info = {
    'db_file' : r'C:\Users\marty\OneDrive\Pulpit\Programowanie\Zapisane_kody\coffee_machine\data\coffee.db'
}

class Transaction:
    def __init__(self, user_choice, budget, price):
        self.user_choice = user_choice
        self.budget = float(budget)
        self.price = price
    def budget_change(self, bc):
        self.bc = bc
        if self.bc == '':
            self.bc = 0
        self.budget += float(self.bc)
        return self.budget
    def reset(self):
        self.budget = 0
        return self.budget


transaction = Transaction("", 0, 0)

def get_db():
    if not hasattr(g, 'sqlite_db'):
        conn = sqlite3.connect(app_info['db_file'])
        conn.row_factory = sqlite3.Row
        g.sqlite_db = conn
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route("/", methods=['GET', 'POST'])
def coffee_machine():
    if request.method == 'GET':
        flash ('Stand by, please select coffee')
        return render_template("coffee_machine.html")
    else:
        report = request.form['report'] if 'report' in request.form else ''
        user_choice = request.form['user_choice'] if 'user_choice' in request.form else ''
        reset = request.form['reset'] if 'reset' in request.form else ''
        accept = request.form['accept'] if 'accept' in request.form else ''
        if report:
            if transaction.budget:
                flash("For view a report please \nreset coffee machine")
                return render_template("coffee_machine.html")
            else:
                db = get_db()
                sql_statement = 'select name from report;'
                cur = db.execute(sql_statement)
                num_of_espressoo = 0
                num_of_latte = 0
                num_of_cappuccino = 0
                data = cur.fetchall()
                for row in data:
                    if row[0] == 'espresso':
                        num_of_espressoo += 1
                    if row[0] == 'latte':
                        num_of_latte += 1
                    if row[0] == 'cappuccino':
                        num_of_cappuccino += 1
                sql_earn = 'select SUM(price) from report;'
                cur_earn = db.execute(sql_earn)
                earn = cur_earn.fetchone()
                flash(f"Number of espresso: {num_of_espressoo} \nNumber of latte: {num_of_latte} \nNumber of cappuccino: {num_of_cappuccino} \nEarn: {round(earn[0], 2)}")
                return render_template("coffee_machine.html")
        if reset:
            if transaction.budget > 0:
                rest = round(transaction.budget, 2)
                flash(f"Coffee machine reset, \nyour refund {rest}")
                transaction.reset()
                return render_template("coffee_machine.html")
            else:
                transaction.reset()
                flash('Stand by, \nplease select coffee')
                return render_template("coffee_machine.html")
        if accept:
            if transaction.budget >= transaction.price:
                refund = transaction.budget - transaction.price
                db = get_db()
                sql_command = 'insert into report (name, price) values (?, ?);'
                db.execute(sql_command, [transaction.user_choice, transaction.price])
                db.commit()
                if refund > 0:
                    rest = round(refund, 2)
                    flash(f"Your coffee {transaction.user_choice} \nis ready, \nrefund is {rest}, enjoy")
                    transaction.reset()
                    return render_template("coffee_machine.html")
                else:
                    flash(f"Your coffee {transaction.user_choice} \nis ready, enjoy")
                    transaction.reset()
                    return render_template("coffee_machine.html")
            else:
                lack = transaction.price - transaction.budget
                flash(f"{transaction.user_choice}. \nNot enough money, \nplease insert {round(lack, 2)} more")
                return render_template("prepare_coffee.html")
        if user_choice:
            db = get_db()
            sql_statement = 'select id, name, price from coffee where name =?;'
            cur = db.execute(sql_statement, [user_choice])
            coffee_data = cur.fetchone()
            transaction.user_choice = user_choice
            transaction.price = coffee_data[2]
            flash(f"Price: {transaction.price}zł; \nYour budget: {round(transaction.budget, 2)}zł")
            return render_template("prepare_coffee.html")
        else:
            budget_change = request.form['budget'] if 'budget' in request.form else ''
            transaction.budget_change(budget_change)
            flash(f"Price: {transaction.price}zł; \nYour budget: {round(transaction.budget, 2)}zł")
            return render_template("prepare_coffee.html")

if __name__ == "__main__":
    app.run()
