from flask import Flask, request, jsonify, redirect, render_template
from neo4j import GraphDatabase
import csv

# establish the connection
with open("cred.txt") as fl:
    data = csv.reader(fl, delimiter=',')
    for row in data:
        username = row[0]  # account name:neo4j
        pwd = row[1]  # password:neo4j
        uri = row[2]

print(username, pwd, uri)
driver = GraphDatabase.driver(uri=uri, auth=(username, pwd))
session = driver.session()
api = Flask(__name__)


@api.route("/create/<string:name>&<string:code>", methods=["GET", "POST"])
def create_node(name, code):
    q1 = """
    create (n:Stock{NAME:$name,CODE:$code})
    """
    map = {"name": name, "code": code}
    try:
        session.run(q1, map)

        return (f"stock code is created with stock name={name} and code={code}")
    except Exception as e:
        return (str(e))

@api.route("/display", methods=["GET", "POST"])
def display_node():
    q2 = """
    match (n) return n.NAME as NAME, n.CODE as CODE
    """
    results=session.run(q2)

    data = results.data()
    return (jsonify(data))

@api.route("/delete/<string:name>", methods=["GET", "POST"])
def delete_node(name):
    q3 = """
    MATCH (n:Stock {NAME:$name})
    DELETE n
    """

    try:
        session.run(q3)

        return (f"stock code {name}is deleted in the list")
    except Exception as e:
        return (str('delete function can not be function'))


if __name__ == "__main__":
    api.run(port=5050)
