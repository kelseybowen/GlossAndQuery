# ########################################
# ########## SETUP

from flask import Flask, render_template, request, redirect
import database.db_connector as db

PROD_PORT = 8282
DEV_PORT = 6030

app = Flask(__name__)

# ########################################
# ########## ROUTE HANDLERS

# READ ROUTES
@app.route("/", methods=["GET"])

# polish types 
@app.route("/polish-types")
def polish_types():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT polishTypeID AS ID, name AS Name, description AS Description FROM PolishTypes;").fetchall()
    dbConnection.close()
    return render_template("polish-types.j2", types=rows)

# polishes
@app.route("/polishes")
def polishes():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT Polishes.polishID AS ID, Polishes.name AS Name, Polishes.color AS Color, Polishes.inventory as Inventory, Polishes.price AS Price, PolishTypes.name AS Type FROM Polishes JOIN PolishTypes ON Polishes.polishTypeID = PolishTypes.polishTypeID ORDER BY ID;").fetchall()
    dbConnection.close()
    return render_template("polishes.j2", polishes=rows)

#customers
@app.route("/customers")
def customers():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT customerID AS ID, fName AS `First Name`, lName AS `Last Name`, email AS Email, address AS Address FROM Customers;").fetchall()
    dbConnection.close()
    return render_template("customers.j2", customers=rows)

# orders
@app.route("/orders")
def orders():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT Orders.orderID AS ID, DATE_FORMAT(Orders.orderDate, '%%M %%d, %%Y %%H:%%i') AS Date, Orders.orderTotal AS `Order Total`, Orders.isFulfilled AS Fulfilled, CONCAT(Customers.fName, ' ', Customers.lName) AS Customer FROM Orders JOIN Customers ON Orders.customerID = Customers.customerID;").fetchall()
    for row in rows:
        row['Fulfilled'] = "Yes" if row['Fulfilled'] == 1 else "No"
    dbConnection.close()
    return render_template("orders.j2", orders=rows)

# CREATE order - form route
@app.route("/orders/new")
def create_order():
    return render_template("new-order.j2")

# CREATE order - submit route
@app.route("/orders/submit")
def submit_order(order_details):
    dbConnection = db.connectDB()
    # need 
    new_order = db.query(dbConnection, "INSERT INTO Orders (orderDate, orderTotal, isFulfilled, customerID) VALUES (NOW(), {order_details.price}, 0, {order_details.customerID});")
    order_items = db.query(dbConnection, "")
    dbConnection.close()

# polish orders
@app.route("/polish-orders")
def polish_orders():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT PolishOrders.polishOrderID AS ID, (SELECT CONCAT(Customers.fName, ' ', Customers.lName)) AS Customer, Polishes.name AS Name, Polishes.price as `Unit Price`, PolishOrders.quantity AS Quantity, PolishOrders.lineTotal AS `Line Total`, DATE_FORMAT(Orders.orderDate, '%%M %%d, %%Y %%H:%%i') AS Date FROM Polishes JOIN PolishOrders ON Polishes.polishID = PolishOrders.polishID JOIN Orders ON PolishOrders.orderID = Orders.orderID JOIN Customers ON Orders.customerID = Customers.customerID;").fetchall()
    pol_list = db.query(dbConnection, 
        "SELECT polishID, name FROM Polishes;"
    ).fetchall()
    dbConnection.close()
    return render_template(
      "polish-orders.j2", 
      polish_orders=rows, 
      all_polishes=pol_list
    )

# customer favorites 
@app.route("/customer-favorites")
def customer_favorites():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT (SELECT CONCAT(Customers.fName, ' ', Customers.lName)) AS Customer, Polishes.name AS Polish FROM Customers JOIN CustomerFavoritePolishes ON Customers.CustomerID = CustomerFavoritePolishes.customerID JOIN Polishes ON CustomerFavoritePolishes.polishID = Polishes.polishID;").fetchall()
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
        port=PROD_PORT, debug=True
    )  # debug is an optional parameter. Behaves like nodemon in Node.