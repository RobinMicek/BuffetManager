# IMPORT LIBRARIES
import requests
import json
import os

# IMPORT FROM LIBRARIES
from flask import Flask, redirect, render_template, request, abort, session
from pprint import pprint


# Flask INIT
app = Flask(__name__)
app.secret_key = "SECRET KEY"

# API URL
API_URL = str(os.environ.get("API_URL", "127.0.0.1:8181"))

"""
API VIEWS START
"""

# HOMEPAGE
@app.route("/")
def page_pos():
    if "pin" in session and "pin" != None:
        print(session["pin"])
        # Get products
        products = json.loads(requests.get(f"{API_URL}/client/product/all").text)
        
        # Get cart
        cart = json.loads(requests.get(f"{API_URL}/client/product/cart", headers={"account-pin": str(session["pin"])}).text)

        # Get total
        total = requests.get(f"{API_URL}/client/get-total", headers={"account-pin": str(session["pin"])}).text

        # Get kiosk name
        name = json.loads(requests.get(f"{API_URL}/client/get-account", headers={"account-pin": str(session["pin"])}).text)[0][0]

        return render_template("pos.html", products=products, cart=cart, total=total, name=name, pin=session["pin"], API_URL=API_URL)

    else:
        return redirect("/login")

# LOGIN
@app.route("/login", methods=["POST", "GET"])
def page_login():
    if request.method == "POST":

        make_request = json.loads(requests.get(f"{API_URL}/client/get-account", headers={"account-pin": str(request.form["pin"])}).text)


        if make_request != []:
            session["pin"] = int(request.form["pin"])
            
            return redirect("/")

        else:
            return redirect("/login")
    else:

        return render_template("login.html")







"""
ACTIONS
"""
# ADD TO CART
@app.route("/action/add-to-cart")
def page_add_to_cart():

    if "pin" in session:
        product_id = request.args.get("product-id", None)
        print(product_id)

        if product_id != None:

            data = {
                "product-id": "hello world"
            }

            requests.post(f"{API_URL}/client/add-to-cart?id={product_id}", data=data, headers={"account-pin": str(session["pin"])})

            print(product_id.upper())

        return redirect("/")


    else:
        return redirect("/login")











# PAY
@app.route("/action/pay")
def page_pay():
    if "pin" in session:

        # Get cart
        cart = json.loads(requests.get(f"{API_URL}/client/product/cart", headers={"account-pin": str(session["pin"])}).text)

        products = []
        for x in cart:
            products += [int(x["id"])]
        
        # Get total
        total = requests.get(f"{API_URL}/client/get-total", headers={"account-pin": str(session["pin"])}).text

        payload = {
            "products": f"{products}",
            "price": str(total)
        }

        requests.post(f"{API_URL}/client/pay", data=payload, headers={"account-pin": str(session["pin"])})

        return redirect("/")

    return redirect("/login")






# LOGOUT
@app.route("/logout")
def logout():
    if "pin" in session:
        session.pop("pin")

    return redirect("/login")

# RUN - USE AN ACTUAL SERVER FOR PRODUCTION
while __name__ == "__main__":
    app.run(host="10.0.1.16", port=8010, debug=False)
