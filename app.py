from flask import Flask, render_template, redirect, url_for
from flask import request as my_req
from bs4 import BeautifulSoup as bs
import datetime
import re
import json
import os
import requests

app = Flask(__name__)

@app.route("/")
@app.route("/index.html")
def home():
    name = "Smash"
    return render_template("index.html", name=name)

@app.route("/calculator.html", methods=["GET", "POST"])
def calculator():
    class Calculator:
        def __init__(self, num1, num2):
            self.num1 = float(num1)
            self.num2 = float(num2)
        def add(self):
            res = self.num1 + self.num2
            return res
        def subs(self):
            res = self.num1 - self.num2
            return res
        def mult(self):
            res = self.num1 * self.num2
            return res
        def div(self):
            try:
                res = self.num1 / self.num2
                rem = self.num1 % self.num2
                return f"{res} ({rem})"
            except ZeroDivisionError:
                return "<strong>CAN NOT DIVIDE BY ZERO!!!</strong>"

    operations = {
            "Add":"+",
            "Substract":"-",
            "Multiply":"*",
            "Divide":"/",
            }

    output = None

    if my_req.method == "POST":
        num1 = my_req.values.get('num1')
        num2 = my_req.values.get('num2')
        opr = my_req.values.get('opr')
        num_regex = r'^\d+$'
        if not re.match(num_regex, num1):
            errormsg = "Please enter correct value for the number. It should be a digit"
            output = None
            return render_template(url_for('calculator'), output=output, errormsg=errormsg, operations=operations)
        else:
            float(num1)
        if not re.match(num_regex, num2):
            errormsg = "Please enter correct value for the number. It should be a digit"
            output = None
            return render_template(url_for('calculator'), output=output, errormsg=errormsg, operations=operations)
        else:
            float(num2)
        calc = Calculator(num1, num2)
        match opr:
            case "+":
                output = calc.add()
                return render_template(url_for('calculator'), output=output, operations=operations)
            case "-":
                output = calc.subs()
                return render_template(url_for('calculator'), output=output, operations=operations)
            case "*":
                output = calc.mult()
                return render_template(url_for('calculator'), output=output, operations=operations)
            case "/":
                output = calc.div()
                return render_template(url_for('calculator'), output=output, operations=operations)
            case _:
                output = None
                errormsg = "Please enter correct value for the operation. It should be a mathematical sign of operation"
                return render_template(url_for('calculator'), output=output, errormsg=errormsg, operations=operations)

    return render_template("calculator.html", operations=operations, output=output)

@app.route("/converter.html", methods=["GET", "POST"])
def converter():
    file = "exchange_rate.json"
    class ExchangeRate:

        data = dict()

        def __init__(self, currency, rate):
            self.currency = currency
            self.rate = rate
            self.data.update({self.currency: self.rate})
            self.from_cur = None
            self.from_val = None
            self.to_cur = None

        def save_to(self):
            self.data.update({"azn": 1.0})
            with open(file, "w", encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)

        def show_all(self):
            try:
                with open(file, "r") as f:
                    self.data = json.load(f)
                return self.data
            except FileNotFoundError:
                return "<strong>Database File does not Exists. Check internet connection!!!</strong>"

        def converting(self, from_cur, from_val, to_cur):
            self.from_cur = from_cur
            self.from_val = float(from_val)
            self.to_cur = to_cur
            with open(file, "r") as f:
                self.data = json.load(f)
            if self.from_cur.lower() == "azn":
                to_val = self.from_val / self.data[self.to_cur]
            elif self.to_cur.lower() == "azn":
                to_val = self.from_val * self.data[self.from_cur]
            else:
                to_val = (self.from_val * self.data[self.from_cur]) / self.data[self.to_cur]
            return f"Your {self.from_val} {self.from_cur.upper()} makes => {to_val} {self.to_cur.upper()}"

    if os.path.exists(file) == False:
        url = "https://www.cbar.az/currency/rates"
        page = requests.get(url)

        soup = bs(page.content, "html.parser")

        results = soup.find("div", class_="table_content")
        rel_to_azn = results.find_all("div", class_="table_row")
        for cur in rel_to_azn:
            key = cur.find('div', class_='kod').text
            value = float(cur.find('div', class_='kurs').text)
            x = ExchangeRate(key, value)

        x.save_to()
    else:
        file_m_date = datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d')
        today = str(datetime.date.today())
        if file_m_date != today:
            url = "https://www.cbar.az/currency/rates"
            page = requests.get(url)

            soup = bs(page.content, "html.parser")

            results = soup.find("div", class_="table_content")
            rel_to_azn = results.find_all("div", class_="table_row")
            for cur in rel_to_azn:
                key = cur.find('div', class_='kod').text
                value = float(cur.find('div', class_='kurs').text)
                x = ExchangeRate(key, value)

            x.save_to()

    currency = ExchangeRate(None, None)
    curr_table = currency.show_all()
    
    if my_req.method == "POST":
            from_cur = my_req.values.get('from_cur')
            from_val = my_req.values.get('from_val')
            to_cur = my_req.values.get('to_cur')
            curr_regex = r'^[a-z]{1,3}$|^[A-Z]{1,3}$'
            num_regex = r'^\d+$'
            if not re.match(curr_regex, str(from_cur)):
                errormsg = "Please enter currency code in the format shown above!!!"
                output = None
                return render_template(url_for('converter'), curr_table=curr_table, output=output, errormsg=errormsg)
            else:
                str(from_cur)
            if not re.match(curr_regex, str(to_cur)):
                errormsg = "Please enter currency code in the format shown above!!!"
                output = None
                return render_template(url_for('converter'), curr_table=curr_table, output=output, errormsg=errormsg)
            else:
                str(to_cur)
            if not re.match(num_regex, from_val):
                errormsg = "Please enter value as number with only digits!!!"
                output = None
                return render_template(url_for('converter'), curr_table=curr_table, output=output, errormsg=errormsg)
            else:
                float(from_val)
            output = currency.converting(from_cur, from_val, to_cur)
            return render_template(url_for('converter'), curr_table=curr_table, output=output)

    return render_template("converter.html", curr_table=curr_table)

if __name__ == "__main__":
    app.run(debug=True, port=48800)
