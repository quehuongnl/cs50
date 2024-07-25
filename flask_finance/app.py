import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Get list of dictionaries of stocks by id
    id = session.get("user_id")
    list = db.execute("SELECT symbol, SUM(shares) FROM transactions WHERE id = ? GROUP BY symbol ORDER BY symbol", id)
    rows = db.execute("SELECT cash FROM users WHERE id = ?", id)
    cash = rows[0]["cash"]
    total = cash
    index = []

    # Iterate through list to get current price and total
    for stock in list:
        symbol = stock["symbol"]
        shares = int(stock["SUM(shares)"])
        quote = lookup(symbol)
        price = quote["price"]
        total_each = shares * price
        total += total_each
        row = {"symbol": symbol, "shares": shares, "price": price, "total": total_each}
        index.append(row)

    # Redirect user to quoted page
    return render_template("index.html", index=index, cash=cash, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure symbol was submitted
        input_symbol = request.form.get("symbol")
        if not input_symbol:
            return apology("missing symbol", 400)

        # Ensure shares was submitted
        shares = request.form.get("shares")
        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("invalid shares", 400)

        # Lookup by symbol
        quote = lookup(input_symbol)
        if quote is None:
            return apology("invalid symbol", 400)

        symbol = quote["symbol"]
        price = quote["price"]

        # Get current cash balance
        id = session.get("user_id")
        rows = db.execute("SELECT * FROM users WHERE id = ?", id)
        cash = rows[0]["cash"]

        # Check if buy is affordable
        shares = int(shares)
        amount = shares * price
        if amount > cash:
            return apology("cant afford", 400)

        # Buy shares and update tables
        transacted = datetime.now()
        cash -= amount

        db.execute("INSERT INTO transactions (id, symbol, shares, price, transacted, amount) VALUES(?, ?, ?, ?, ?, ?)",
                   id, symbol, shares, price, transacted, amount)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, id)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Get list of dictionaries of stocks by id
    id = session.get("user_id")
    list = db.execute("SELECT symbol, shares, price, transacted FROM transactions WHERE id = ? GROUP BY symbol ORDER BY symbol", id)

    # Redirect user to quoted page
    return render_template("history.html", list=list)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # User submit via POST
    if request.method == "POST":
        input_symbol = request.form.get("symbol")
        if not input_symbol:
            return apology("missing symbol", 400)

        # Lookup by symbol
        quote = lookup(input_symbol)
        if not quote:
            return apology("invalid symbol", 400)

        # Redirect user to quoted page
        return render_template("quoted.html", quote=quote)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        checkusername = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username and password were submitted
        if not username or not password or not confirmation:
            return apology("missing username or password", 400)

        # Ensure username does not exist
        elif len(checkusername) != 0:
            return apology("username already exists", 400)

        # Ensure password and confirmation match
        elif password != confirmation:
            return apology("passwords do not match", 400)

        hash = generate_password_hash(password, method='pbkdf2', salt_length=16)
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        id = session.get("user_id")

        # Lookup by symbol
        quote = lookup(request.form.get("symbol"))
        symbol = quote["symbol"]
        price = quote["price"]

        shares = request.form.get("shares")

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("missing symbol", 400)

        # Ensure symbol exists
        elif quote is None:
            return apology("invalid symbol", 400)

        # Ensure shares was submitted
        elif not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("invalid shares", 400)

        # Get list of dictionaries of stocks by id and symbol
        list = db.execute("SELECT symbol, SUM(shares) FROM transactions WHERE id = ? AND symbol = ?", id, symbol)

        # Check if symbol is valid
        if len(list) != 1:
            return apology("symbol not owned", 400)

        # Check if sell is affordable
        if int(shares) > list[0]["SUM(shares)"]:
            return apology("too many shares", 400)

        # Current cash balance
        rows = db.execute("SELECT * FROM users WHERE id = ?", id)
        cash = rows[0]["cash"]

        # Buy shares and update tables
        shares = int(shares)
        amount = shares * price
        cash += amount
        transacted = datetime.now()

        db.execute("INSERT INTO transactions (id, symbol, shares, price, transacted, amount) VALUES(?, ?, ?, ?, ?, ?)",
                   id, symbol, -shares, price, transacted, amount)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, id)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get list of dictionaries of stocks by id
        list_id = db.execute(
            "SELECT symbol, SUM(shares) FROM transactions WHERE id = ? GROUP BY symbol ORDER BY symbol", session.get("user_id"))
        return render_template("sell.html", list_id=list_id)
