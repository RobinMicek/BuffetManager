# IMPORT LIBRARIES
import requests
import json
import os


# IMPORT FROM LIBRARIES
from flask import Flask, redirect, render_template, request, abort, session
from pprint import pprint

# FROM OTHER FILES
from random_string import generate_token

# APP CONFIG
CONFIG = {
    "name": "BUFFET MANAGER"
}

# Flask INIT
app = Flask(__name__)
app.secret_key = generate_token()

# API URL
API_URL = str(os.environ.get("API_URL", "http://127.0.0.1:8181"))

"""
API VIEWS START
"""

# HOMEPAGE
@app.route("/")
def page_homepage():
    check = str(requests.get(f"{API_URL}/fts/check").text)
    if check == "false":
        
        return redirect("/fts")

    else:
        if "api_token" in session:

            # CHARTS
            transactions = requests.get(f"{API_URL}/chart/transactions", headers={"token": session["api_token"]}).text[1:]
            top_products_all = requests.get(f"{API_URL}/chart/most-sold-products/all-time", headers={"token": session["api_token"]}).text[1:]


            analytics = json.loads(requests.get(f"{API_URL}/chart/analytics", headers={"token": session["api_token"]}).text)

            return render_template("homepage.html", CONFIG=CONFIG,
            top_products_all=top_products_all,
            transactions=transactions,
            analytics=analytics)

        else:
            return redirect("/login")

# FIRST TIME SETUP
@app.route("/fts", methods=["POST", "GET"])
def page_first_time_setup():
    check = str(requests.get(f"{API_URL}/fts/check").text)
    if check == "false":

        if request.method == "POST":
            name = request.form["name"]
            desc = request.form["description"]
            key = request.form["key"]

            payload = {
                "name": str(name),
                "desc": str(desc),
                "key": str(key)
            }

            requests.post(f"{API_URL}/fts/create", data=payload)

            return redirect("/")

        else:
            auth_url = f"https://www.authenticatorApi.com/pair.aspx?AppName={CONFIG['name']}&AppInfo=Dashboard&SecretCode="
            auth_code = str(generate_token())

            auth_page = requests.get(f"{auth_url}{auth_code}").text

            auth_img = (auth_page.split("src='")[1]).split("'")[0]


            return render_template("fts.html", auth_url=auth_url, auth_code=auth_code, auth_img=auth_img, CONFIG=CONFIG)

    else:
        return redirect("/")


# LOGIN
@app.route("/login", methods=["POST", "GET"])
def page_login():
    check = str(requests.get(f"{API_URL}/fts/check").text)
    if check == "false":
        
        return redirect("/")

    else:
         
        if request.method == "POST":
            code = str(request.form["code"])

            make_request = str(requests.get(f"{API_URL}/auth/login?code={code}").text)

            if make_request != "false":
                api_token = json.loads(make_request)["token"]

                session["api_token"] = api_token

                return redirect("/")

            else:
                return redirect("/login")

        else:
            return render_template("login.html", CONFIG=CONFIG)

@app.route("/login/check")
def page_check_login():

    if "api_token" in session:
        check = str(requests.get(f"{API_URL}/auth/check", headers={"token": session["api_token"]}).text)

        print(check)

        if check == "true":

            return "Ur logged in <3"

        else:
            return redirect("/login")

    else:
        return abort(401)


    
# NEW PRODUCT
@app.route("/product/new", methods=["POST", "GET"])
def page_new_product():
    if "api_token" in session:

        if request.method == "POST":
            
            # Process image
            # img = request.files["image"]

            # processed_image = str(img.read())

            payload = {
                "name": request.form["name"],
                "category": request.form["category"],
                "price": request.form["price"],
                "stock": request.form["stock"],
                "visible": request.form["visible"]
                #"image": processed_image
            }
            
            make_request = requests.post(f"{API_URL}/product/new", data=payload, headers={"token": session["api_token"]})

            return redirect("/product/all")

        else:
            return render_template("new-product.html")

    else:
        return redirect("/")


# PRODUCT PAGE
@app.route("/product/info", methods=["POST", "GET"])
def page_product_info():
    if "api_token" in session:  

        if request.method == "POST":

            payload = {
                    "id": request.form["id"],
                    "name": request.form["name"],
                    "category": request.form["category"],
                    "price": request.form["price"],
                    "stock": request.form["stock"],
                    "visible": request.form["visible"]
                }

            pprint(payload)

            requests.post(f"{API_URL}/product/update", data=payload, headers={"token": session["api_token"]})

            return redirect(request.referrer)


        else:

            product_id = request.args.get("id", None)

            product = json.loads(requests.get(f"{API_URL}/product/info/{product_id}", headers={"token": session["api_token"]}).text)


            
            return render_template("product.html", product=product)

    else:
        return redirect("/")






            
# LIST OF PRODUCTS
@app.route("/product/all")
def page_all_products():
    if "api_token" in session:  

        products = json.loads(requests.get(f"{API_URL}/product/all", headers={"token": session["api_token"]}).text)

        return render_template("products-list.html", products=products)

    else:
        return redirect("/")




# LIST OF TRANSACTION
@app.route("/transactions/all")
def page_all_transactions():
    if "api_token" in session:  

        transactions = json.loads(requests.get(f"{API_URL}/transactions/all", headers={"token": session["api_token"]}).text)

        return render_template("transactions-list.html", transactions=transactions)

    else:
        return redirect("/")










   
# NEW PRODUCT
@app.route("/account/new", methods=["POST", "GET"])
def page_new_account():
    if "api_token" in session:

        if request.method == "POST":
            
            payload = {
                "name": request.form["name"],
                "pin": request.form["pin"]
            }
            
            make_request = requests.post(f"{API_URL}/account/new", data=payload, headers={"token": session["api_token"]})

            return redirect("/account/all")

        else:
            return render_template("new-account.html")

    else:
        return redirect("/")



# LIST OF ACCOUNTS
@app.route("/account/all")
def page_all_accounts():
    if "api_token" in session:  

        accounts = json.loads(requests.get(f"{API_URL}/account/all", headers={"token": session["api_token"]}).text)

        return render_template("accounts-list.html", accounts=accounts)

    else:
        return redirect("/")












# LOGOUT
@app.route("/logout")
def page_logout():

    session.pop("api_token", None)
    
    return redirect("/")


    



# RUN - USE AN ACTUAL SERVER FOR PRODUCTION
while __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
