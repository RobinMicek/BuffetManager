# IMPORT LIBRARIES
import mysql.connector
import uvicorn
import requests
import json
import os

# IMPORT FROM LIBRARIES
from fastapi import FastAPI, Request, Form
from quickchart import QuickChart
from pprint import pprint
from datetime import datetime


# FROM OTHER FILES
from db import initialize_db, check_db
from random_string import generate_token


# MySQL DB INIT
db = mysql.connector.connect(
    host=str(os.environ.get("DB_HOST", "127.0.0.1")),
    user=str(os.environ.get("DB_USER", "root")),
    password=str(os.environ.get("DB_PASSWORD", "")),
    database="buffetdb"
)

cursor = db.cursor()

# FastAPI INIT
app = FastAPI()


# CURRENT AUTH TOKEN 
current_auth_token = ""


"""
API VIEWS START
"""

# FIRST TIME SETUP
# Check - See if 'config' table in DB
@app.get("/fts/check")
async def first_time_setup_check():
    return check_db()


# Create - Initializes the app with provided info
@app.post("/fts/create")
async def first_time_setup_create(
    request: Request,
    name: str = Form("name"), desc: str = Form("desc"), key: str = Form("key")):
    

    if check_db() == False:

        initialize_db()

        cursor.execute("INSERT INTO config (name, description, akey) VALUES (%s, %s, %s)", (name, desc, key))

        db.commit()


# AUTHORIZATION / LOGIN
@app.get("/auth/login")
async def handle_login(
    request: Request, code: str = "invalid_token"):

    if check_db() == True:
        auth_url = f"https://www.authenticatorApi.com/Validate.aspx?Pin={code}&SecretCode="

        cursor.execute("SELECT akey FROM config")
        auth_code = ()

        for x in cursor.fetchall():
            auth_code += x
        auth_code = auth_code[0]

        check_login = str(requests.get(f"{auth_url}{auth_code}").text)

        if check_login == "True":
            new_token = generate_token()
            
            global current_auth_token
            current_auth_token = new_token
            
            return {
                "token": new_token
            }

        else:
            return False


@app.get("/auth/check")
async def auth_check_status(
    request: Request):

    token = request.headers.get("token", None)

    global current_auth_token
    if token == current_auth_token:
        return True

    else:
        return False




# PRODUCTS
@app.post("/product/new")
async def new_product(
    request: Request, 
    name: str = Form("name"), price: float = Form("price"), category: str = Form("category"),
    stock: int = Form("stock"), visible: bool = Form("visible")):

    
    # CHECK AUTH
    token = request.headers.get("token", None)

    global current_auth_token
    if token == current_auth_token:
        
        # Add into table
        cursor.execute("INSERT INTO products (name, price, category) VALUES (%s, %s, %s)", (name, price, category))
        #cursor.execute(f"INSERT INTO products_images (image) VALUES ({})")
        cursor.execute(f"INSERT INTO products_stock (stock) VALUES ({stock})")
        cursor.execute(f"INSERT INTO products_visibility (visible) VALUES ({visible})")
        
        db.commit()

        print(name, price, category, stock)

        return "OK"


    else:
        return False




@app.get("/product/info/{product_id}")
async def get_product_info(
    product_id: int, 
    request: Request):

    # CHECK AUTH
    token = request.headers.get("token", None)

    global current_auth_token
    if token == current_auth_token:


        # Find product in DB
        cursor.execute("SELECT \
            products.id AS id, \
            products.name AS name, \
            products.category AS category, \
            products.price AS price, \
            \
            products_stock.stock AS stock, \
            products_stock.sold AS sold, \
            \
            products_visibility.visible AS visible \
            FROM products \
            INNER JOIN products_stock ON products.id = products_stock.id \
            INNER JOIN products_visibility ON products.id = products_visibility.id \
            ORDER BY products.category")

        product_info = []

        for x in cursor.fetchall():
            if x[0] == product_id:
                
                product_info = {
                    "id": x[0],
                    "name": x[1],
                    "category": x[2],
                    "price": x[3],
                    "stock": x[4],
                    "sold": x[5],
                    "visible": x[6]
                }

            pprint(x)
        

        return product_info
    
    else:
        return False





@app.post("/product/update")
async def update_product(
    request: Request, 
    name: str = Form("name"), price: float = Form("price"), category: str = Form("category"),
    stock: int = Form("stock"), visible: bool = Form("visible"), id: int = Form("id")):


    # CHECK AUTH
    token = request.headers.get("token", None)

    global current_auth_token
    if token == current_auth_token:

        print(visible," ", id)

        # UPDATE PRODUCT IN DB
        cursor.execute("UPDATE products \
            SET \
            name = %s, \
            price = %s, \
            category = %s \
            WHERE id = %s",
            (name, price, category, id))

        cursor.execute("UPDATE products_stock \
            SET \
            stock = %s \
            WHERE id = %s",
            (stock, id))

        cursor.execute("UPDATE products_visibility \
            SET \
            visible = %s \
            WHERE id = %s",
            (visible, id))

        db.commit()


    else:
        return False






@app.get("/product/all")
async def get_all_products(
    request: Request):

    # CHECK AUTH
    token = request.headers.get("token", None)

    global current_auth_token
    if token == current_auth_token:


        # Find product in DB
        cursor.execute("SELECT \
            products.id AS id, \
            products.name AS name, \
            products.category AS category, \
            products.price AS price, \
            \
            products_stock.stock AS stock, \
            products_stock.sold AS sold, \
            \
            products_visibility.visible AS visible \
            FROM products \
            INNER JOIN products_stock ON products.id = products_stock.id \
            INNER JOIN products_visibility ON products.id = products_visibility.id \
            ORDER BY products.category")

        products = []

        for x in cursor.fetchall():
            products += [{
                "id": x[0],
                "name": x[1],
                "category": x[2],
                "price": x[3],
                "stock": x[4],
                "sold": x[5],
                "visible": x[6]
            }]
        
        pprint(products)
        

        return products
    
    else:
        return False







# Transactions
@app.get("/transactions/all")
async def get_all_transactions(
    request: Request):

    # CHECK AUTH
    token = request.headers.get("token", None)

    global current_auth_token
    if token == current_auth_token:
        
        cursor.execute("\
        SELECT \
        transactions.id as TID, \
        transactions.price AS price, \
        transactions.date AS date, \
        transactions.time AS time, \
        \
        accounts.name AS account\
        \
        FROM transactions \
        INNER JOIN accounts \
        ON transactions.account = accounts.pin \
        \
        ORDER BY transactions.id DESC")

        transactions = []

        for x in cursor.fetchall():
            transactions += [{
                "tid": x[0],
                "price": x[1],
                "account": x[4],
                "date": x[2],
                "time": x[3]
            }]


        return transactions


# Accounts
@app.post("/account/new")
async def new_account(
    request: Request, 
    name: str = Form("name"), pin: int = Form("pin")):

    
    # CHECK AUTH
    token = request.headers.get("token", None)

    global current_auth_token
    if token == current_auth_token:
        
        # Add into table
        cursor.execute("INSERT INTO accounts (name, pin) VALUES (%s, %s)", (name, pin))
        
        db.commit()

        return "OK"


    else:
        return False





@app.get("/account/all")
async def get_accounts(
    request: Request):

    # CHECK AUTH
    token = request.headers.get("token", None)

    global current_auth_token
    if token == current_auth_token:

        cursor.execute("SELECT \
            accounts.pin AS pin, \
            accounts.name AS name \
            \
            FROM accounts")
        
        accounts = []

        for x in cursor.fetchall():
            # Check if this account is in 'accounts_opened' => Account is opened 
            cursor.execute(f"\
            SELECT * \
            FROM accounts_opened \
            WHERE account_pin = {x[0]}")

            if cursor.fetchall() == []:
                
                accounts += [{
                    "pin": x[0],
                    "name": x[1],
                    "status": "closed"
                }]

            else:

                accounts += [{
                    "pin": x[0],
                    "name": x[1],
                    "status": "opened"
                }]


        pprint(accounts)
        

        return accounts
    
    else:
        return False




























"""
CLIENT VIEWS
"""
@app.get("/client/product/all")
async def pos_get_all_products():
    
    products = []

    cursor.execute("SELECT \
    products.id AS id, \
    products.name AS name, \
    products.price AS price, \
    products.category AS category, \
    products_stock.stock AS stock, \
    products_visibility.visible AS visible \
    \
    FROM products \
    INNER JOIN products_stock \
    ON products.id = products_stock.id \
    \
    INNER JOIN products_visibility \
    ON products.id = products_visibility.id \
    \
    ORDER BY products.category")

    for x in cursor.fetchall():
        p = {
            "id": x[0],
            "name": x[1],
            "price": x[2],
            "category": x[3],
            "stock": x[4],
            "visible": x[5]
        }

        if p["visible"] != 0:
            products += [p]

    return products



@app.get("/client/product/cart")
async def pos_get_products_in_cart(
    request: Request):

    account_pin = int(request.headers.get("account-pin", None))

    if account_pin != None:
        cursor.execute(f"\
        SELECT \
        products.id AS id, \
        products.name AS name, \
        products.price AS price, \
        accounts_opened.product_id \
        \
        FROM products \
        INNER JOIN accounts_opened \
        ON products.id = accounts_opened.product_id \
        \
        WHERE accounts_opened.account_pin = {account_pin}")

        products = []

        
        for x in cursor.fetchall():
            
            """for y in products:    
                if int(x[0]) == int(y["id"]):
                    y["quantity"] += 1
                    y["price"] += x[2]
                    
                    # Round the price
                    # y["price"] = round(y["price"], 2)


                else:"""

            products += [{  
                "id": x[0],
                "name": x[1],
                "price": x[2],

                "quantity": 1
            }]

            

        print(products)
        return products




@app.get("/client/get-total")
async def post_get_total_price(
    request: Request):

    account_pin = int(request.headers.get("account-pin", None))

    cursor.execute(f"\
        SELECT \
        products.price AS price, \
        accounts_opened.product_id \
        \
        FROM products \
        INNER JOIN accounts_opened \
        ON products.id = accounts_opened.product_id \
        \
        WHERE accounts_opened.account_pin = {account_pin}")


    total = 0
    for x in cursor.fetchall():
        total += x[0] 

    total = round(total, 2)

    return total




@app.post("/client/add-to-cart")
async def pos_add_to_cart(
    request: Request, 
    id: int):

    account_pin = request.headers.get("account-pin", None)

    if account_pin != None:
        cursor.execute(" \
        INSERT INTO accounts_opened \
        (account_pin, product_id) \
        VALUES \
        (%s, %s)",
        (account_pin, id))

        db.commit()

        # Update stock
        cursor.execute(f"\
        SELECT stock \
        FROM products_stock \
        WHERE id = {id}")

        current_stock = 0
        for x in cursor.fetchall():
            current_stock = x

        updated_stock = current_stock[0] - 1
    

        cursor.execute(f"\
        UPDATE products_stock \
        SET stock = {updated_stock}  \
        WHERE id = {id}")

        db.commit()
















@app.get("/client/get-account")
async def pos_get_account(
    request: Request):

    account_pin = int(request.headers.get("account-pin", None))

    cursor.execute(f"\
    SELECT name \
    FROM accounts \
    \
    WHERE pin = {account_pin}")


    return cursor.fetchall()




















# HANDLE TRANSACTION
@app.post("/client/pay")
async def pos_pay(
    request: Request,
    price: float = Form("price"), products: str = Form("products")):


    account_pin = int(request.headers.get("account-pin", None))


    if account_pin != None:

        # CREATE TRASACTION RECORD
        cursor.execute("\
        INSERT \
        INTO transactions \
        (account, products, price, date, time) \
        VALUES \
        (%s, %s, %s, CURRENT_DATE(), CURRENT_TIME())",
        (account_pin, products, price))

        db.commit()



        # ADD 'SOLD' TO products_stock
        for x in json.loads(products):
            cursor.execute(f"\
            UPDATE products_stock \
            SET sold = sold + 1 \
            WHERE id = {x}")

            db.commit()

        
        # REMOVE ITEMS ASSIGNED TO ACCOUNT
        cursor.execute(f"\
        DELETE \
        FROM accounts_opened \
        WHERE account_pin = {account_pin}")





















"""
CHARTS
"""
# Transactions this month
@app.get("/chart/transactions")
async def chart_transactions(
    request: Request):
    
    # CHECK AUTH
    token = request.headers.get("token", None)

    global current_auth_token
    if token == current_auth_token:

        # Get data
        cursor.execute("\
        SELECT \
        transactions.date DATE, \
        transactions.price AS price \
        \
        FROM transactions")

        get_data = cursor.fetchall()

        data_total = []
        labels = []

        for x in get_data: 
            if f"{x[0]}" not in labels:
                labels += [f"{x[0]}"]

        for label in labels:
            value = 0

            for x in get_data:

                if label == str(x[0]):
                    value += float(x[1])

            data_total += [round(value, 2)]

        print(data_total)
        print(labels)

        chart_trans = QuickChart()
        chart_trans.width = 3000
        chart_trans.height = 700

        # Request chart
        chart_trans.config = {
            "type": 'line',
            "data": {
                "labels": labels,
                "datasets": [{
                    "data": data_total,
                    "label": "Total",
                    "fill": "false",
                    "borderColor": "#111",
                    "borderWidth": 10,
                    "pointRadius": 5,
                }]
            },
            "options": {
                "legend": {
                    "display": False,
                    "labels": {
                        "fontSize": 15,
                        "fontStyle": 'bold',
                    }
                },
                "title": {
                    "display": False,
                    "text": 'Transactions',
                    "fontSize": 50,
                },
                
                "scales": {
                    "xAxes": [{
                        "display": True,
                        "gridLines": {
                            "display": False,
                            },
                        "ticks": {
                            "beginAtZero": True,
                            "fontFamily": 'bold',
                            "fontSize": 30,
                        },
                    }],

                    "yAxes": [{
                        "display": True,
                        "gridLines": {
                            "display": False,
                            },
                        "ticks": {
                            "beginAtZero": True,
                            "fontFamily": 'bold',
                            "fontSize": 30,
                        },
                    }]
                },
            }
        }

        return chart_trans.get_url()



# Most sold products
@app.get("/chart/most-sold-products/all-time")
def chart_most_sold_products_all(
    request: Request):

    # CHECK AUTH
    token = request.headers.get("token", None)

    global current_auth_token
    if token == current_auth_token:
    
        # Get data
        cursor.execute("\
        SELECT \
        products.name AS name, \
        products_stock.sold AS sold \
        \
        FROM products \
        INNER JOIN products_stock \
        ON products.id = products_stock.id\
        \
        ORDER BY products_stock.sold DESC \
        LIMIT 5")

        data = []
        labels = []

        for x in cursor.fetchall(): 
            labels += [f"{x[0]}"]
            data += [f"{x[1]}"]

        chart = QuickChart()
        chart.width = 500
        chart.height = 700

        # Request chart
        chart.config = {
            "type": 'doughnut',
            "data": {
                "datasets": [
                {
                    "data": data,
                    "label": "Products"
                }
            ],
            "labels": labels,
            },
            "options": {
                "legend": {
                    "position": 'bottom',
                    "labels": {
                        "fontSize": 30,
                        "fontStyle": 'bold',
                    }
                },
                "title": {
                    "display": False,
                    "text": 'Most Sold All Time',
                    "fontSize": 30,
                },
                "plugins": {
                    "datalabels": {
                        "display": False,
                        "backgroundColor": '#ccc',
                        "borderRadius": 3,
                        "font": {
                            "color": 'red',
                            "weight": 'bold',
                        }
                    }
                }   
            }
        }
        x = chart.get_url()
        return str(x)
















# ANALYTICS
@app.get("/chart/analytics")
async def chart_analytics(
    request: Request):
    
    # CHECK AUTH
    token = request.headers.get("token", None)

    global current_auth_token
    if token == current_auth_token:

        today = datetime.today().strftime('%Y-%m-%d')

        # SALES
        cursor.execute("\
        SELECT \
        price, \
        date \
        FROM transactions")

        data = cursor.fetchall()

        sales_today = 0 
        sales_all = 0
        
        for x in data:
            sales_all += x[0]

            if x[1] == today:
                sales_today += x[0]


        # TRANSACTIONS
        trans_today = 0
        trans_all = 0
        
        for x in data:
            trans_all += 1

            if x[1] == today:
                trans_today += 1

        # SOLD (ITEMS)
        cursor.execute("\
        SELECT \
        products, \
        date \
        FROM transactions")

        sold_today = 0
        sold_all = 0

        for x in cursor.fetchall():
            prods = json.loads(x[0])

            sold_all += len(prods)

            if x[1] == today:
                sold_today += len(prods)


        return {
            "sales": {
                "today": round(sales_today, 2),
                "all-time": round(sales_all, 2),
            },
            "transactions": {
                "today": trans_today,
                "all-time": trans_all
            },
            "sold": {
                "today": sold_today,
                "all-time": sold_all
            }
        }












# RUN - CHANGE FOR PRODUCTION
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8181)
