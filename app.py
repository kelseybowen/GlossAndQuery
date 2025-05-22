# ############# SETUP #####################

from flask import Flask, render_template, request, redirect, url_for


import database.db_connector as db

DEV_PORT = 8976
PROD_PORT =  9007

app = Flask(__name__)

# ########## ROUTE HANDLERS ##############

# home
@app.route("/", methods=["GET"])
def home():
    try:
        return render_template("home.j2")

    except Exception as e:
        print(f"Error rendering page: {e}")
        return "An error occurred while rendering the page.", 500


# READ polish types 
@app.route("/polish-types")
def polish_types():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT polishTypeID AS ID, name AS Name, description AS Description FROM PolishTypes;").fetchall()
    dbConnection.close()
    return render_template("polish-types.j2", types=rows)

# READ polishes
@app.route("/polishes")
def polishes():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT Polishes.polishID AS ID, Polishes.name AS Name, Polishes.color AS Color, Polishes.inventory as Inventory, Polishes.price AS Price, PolishTypes.name AS Type FROM Polishes JOIN PolishTypes ON Polishes.polishTypeID = PolishTypes.polishTypeID ORDER BY ID;").fetchall()
    dbConnection.close()
    return render_template("polishes.j2", polishes=rows)

# READ customers
@app.route("/customers")
def customers():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT customerID AS ID, fName AS `First Name`, lName AS `Last Name`, email AS Email, address AS Address FROM Customers;").fetchall()
    dbConnection.close()
    return render_template("customers.j2", customers=rows)

# READ orders
@app.route("/orders")
def orders():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT Orders.orderID AS ID, DATE_FORMAT(Orders.orderDate, '%%M %%d, %%Y %%H:%%i') AS Date, Orders.orderTotal AS `Order Total`, Orders.isFulfilled AS Fulfilled, CONCAT(Customers.fName, ' ', Customers.lName) AS Customer FROM Orders JOIN Customers ON Orders.customerID = Customers.customerID;").fetchall()
    for row in rows:
        row['Fulfilled'] = "Yes" if row['Fulfilled'] == 1 else "No"
    dbConnection.close()
    return render_template("orders.j2", orders=rows)

# READ polish orders
@app.route("/polish-orders")
def polish_orders():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT PolishOrders.polishOrderID AS ID, (SELECT CONCAT(Customers.fName, ' ', Customers.lName)) AS Customer, Polishes.name AS Name, Polishes.price as `Unit Price`, PolishOrders.quantity AS Quantity, PolishOrders.lineTotal AS `Line Total`, DATE_FORMAT(Orders.orderDate, '%%M %%d, %%Y %%H:%%i') AS Date FROM Polishes JOIN PolishOrders ON Polishes.polishID = PolishOrders.polishID JOIN Orders ON PolishOrders.orderID = Orders.orderID JOIN Customers ON Orders.customerID = Customers.customerID;").fetchall()
    pol_list = db.query(dbConnection, 
        "SELECT polishID, name FROM Polishes;"
    ).fetchall()
    customer_list = db.query(dbConnection, 
        "SELECT customerID, fName, lName FROM Customers;"
    ).fetchall()
    # for row in rows:
    #     print(row['ID'])
    dbConnection.close()
    return render_template(
      "polish-orders.j2", 
      polish_orders=rows, 
      customer_list = customer_list,
      all_polishes=pol_list
    )

# CREATE polish order - submit route
@app.route("/polish-orders/create", methods=['POST'])
def create_polish_order(order_details):
    # ==========================================================
    # NEED FROM FRONTEND: customer_id, polish_id, quantity
    # ==========================================================
    dbConnection = db.connectDB()
    # create new order
    new_order = db.query(dbConnection, "CALL sp_create_order(%s);", [customer_id]).fetchall()
    # create polish order 
    new_polish_order = db.query(dbConnection, "CALL sp_create_polish_order(%s, %s, %s, %s, NOW());", [customer_id, new_order, polish_id, quantity])
    dbConnection.close()
    return redirect('/polish-orders')


@app.route("/polish-orders/update", methods=['PUT'])
def update_polish_order():
    # ==========================================================
    # NEED FROM FRONTEND: polish_order_id, new_quantity
    # ==========================================================
    dbConnection = db.connectDB()
    updated_polish_order = db.query(dbConnection, "CALL sp_update_polish_order(polish_order_id, new_quantity)")
    dbConnection.close()
    return redirect('/polish-orders')


# DELETE polish order
@app.route("/polish-orders/delete/<int:polish_order_id>", methods=['DELETE']) 
def delete_polish_order(polish_order_id):
    dbConnection = db.connectDB()
    db.query(dbConnection,"CALL sp_delete_polish_order(%s);",[polish_order_id])    
    dbConnection.close()
    return redirect("/polish-orders")


#customer favorites 
@app.route("/customer-favorites")
def customer_favorites():
    dbConnection = db.connectDB()
    rows = db.query(dbConnection, "SELECT (SELECT CONCAT(Customers.fName, ' ', Customers.lName)) AS Customer, Polishes.name AS Polish FROM Customers JOIN CustomerFavoritePolishes ON Customers.CustomerID = CustomerFavoritePolishes.customerID JOIN Polishes ON CustomerFavoritePolishes.polishID = Polishes.polishID;").fetchall()

    polishes_dropdown = db.query(dbConnection, """
      SELECT
        polishID   AS ID,
        name       AS name
      FROM Polishes
      ORDER BY name;
    """).fetchall()
    dbConnection.close()
    return render_template("customer-favorites.j2", favorites=rows, polishes_dropdown = polishes_dropdown)


@app.route("/customer-favorites/add", methods=['POST'])
def create_customer_favorite():
    # ==========================================================
    # NEED FROM FRONTEND: customer_id, polish_id
    # ==========================================================
    dbConnection = db.connectDB()
    query = db.query(dbConnection, "CALL sp_create_customer_favorite(%s, %s);", [customer_id, polish_id])
    dbConnection.close()
    return redirect("/customer-favorites")


@app.route("/customer-favorites/delete", methods=['DELETE'])
def delete_customer_favorite():
    # ==========================================================
    # NEED FROM FRONTEND: customer_id, polish_id
    # ==========================================================
    dbConnection = db.connectDB()
    query = db.query(dbConnection, "CALL sp_delete_customer_favorite(%s, %s);", [customer_id, polish_id])
    dbConnection.close()
    return redirect("/customer-favorites")


# reset
@app.route("/reset")
def reset_db():
    dbConnection = db.connectDB()
    query = db.query(dbConnection, "CALL sp_reset_db;")
    dbConnection.close()
    return redirect(request.referrer or url_for('home'))


# ########## LISTENER ##########

if __name__ == "__main__":
    app.run(
        port=DEV_PORT , debug=True
    ) 