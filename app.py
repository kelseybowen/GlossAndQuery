# ########################################
# ########## SETUP

from flask import Flask, render_template, request, redirect
import database.db_connector as db

PORT = 8282

app = Flask(__name__)

# ########################################
# ########## ROUTE HANDLERS

# READ ROUTES
@app.route("/", methods=["GET"])

# polish types 
@app.route("/polish-types")
def polish_types():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT * FROM PolishTypes;").fetchall()
    dbConnection.close()
    return render_template("polish-types.j2", types=rows)

# polishes
@app.route("/polishes")
def polishes():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT * FROM Polishes;").fetchall()
    dbConnection.close()
    return render_template("polishes.j2", polishes=rows)

#customers
@app.route("/customers")
def customers():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT * FROM Customers;").fetchall()
    dbConnection.close()
    return render_template("customers.j2", customers=rows)

# orders
@app.route("/orders")
def orders():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT * FROM Orders;").fetchall()
    dbConnection.close()
    return render_template("orders.j2", orders=rows)

# polish orders
@app.route("/polish-orders")
def polish_orders():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT PolishOrders.polishOrderID, Orders.orderID, Polishes.name, Polishes.price, PolishOrders.quantity, PolishOrders.lineTotal, Orders.orderDate FROM Polishes JOIN PolishOrders ON Polishes.polishID = PolishOrders.polishID JOIN Orders ON PolishOrders.orderID = Orders.orderID;").fetchall()
    dbConnection.close()
    return render_template("polish-orders.j2", polish_orders=rows)

# customer favorites 
@app.route("/customer-favorites")
def customer_favorites():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT Customers.fName, Customers.lName, Polishes.name FROM Customers JOIN CustomerFavoritePolishes ON Customers.CustomerID = CustomerFavoritePolishes.customerID JOIN Polishes ON CustomerFavoritePolishes.polishID = Customers.customerID;").fetchall()
    dbConnection.close()
    return render_template("customer-favorites.j2", favorites=rows)

#home
def home():
    try:
        return render_template("home.j2")

    except Exception as e:
        print(f"Error rendering page: {e}")
        return "An error occurred while rendering the page.", 500



# ########################################
# ########## LISTENER

if __name__ == "__main__":
    app.run(
        port=PORT, debug=True
    )  # debug is an optional parameter. Behaves like nodemon in Node.