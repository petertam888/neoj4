from flask import Flask, request, jsonify, redirect, render_template
from neo4j import GraphDatabase
import csv

# establish the connection
"""
with open("cred.txt") as fl:
    data = csv.reader(fl, delimiter=',')
    for row in data:
        username = row[0]  # account name:neo4j
        pwd = row[1]  # password:neo4j
        uri = row[2]
"""

#print(username, pwd, uri)
driver = GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "12345678"))
session = driver.session()
api = Flask(__name__)


@api.route("/create/<string:name>&<string:code>", methods=["GET", "POST"])
def create_node(name, code):
    query = """
    create (n:Stock{NAME:$name,CODE:$code})
    """
    map = {"name": name, "code": code}
    try:
        session.run(query, map)

        return (f"stock code is created with stock name={name} and code={code}")
    except Exception as e:
        return (str(e))

@api.route("/display", methods=["GET", "POST"])
def display_node():
    query = """
    match (n) return n.NAME as NAME, n.CODE as CODE
    """
    results=session.run(query)

    data = results.data()
    return (jsonify(data))

@api.route("/update/<string:name>", methods=["PUT"])
def update_node(name):
    code = request.json.get('code')
    session.run("MATCH (n:Stock {NAME: $name}) SET n.CODE = $code", name=name, code=code)
    session.close()
    return jsonify({'message': 'Stock info updated'})

"""
    guide = Guide.query.get(id)
    title = request.json['title']
    content = request.json['content']

    guide.title = title
    guide.content = content

    db.session.commit()
    return guide_schema.jsonify(guide)
"""

@api.route("/delete/<string:name>", methods=["DELETE"])
def delete_node(name):
    query = """
    MATCH (n:Stock {NAME:$name})
    DELETE n
    """

    try:
        session.run(query, name=name)

        return (f"stock code {name} is deleted in the list")
    except Exception as e:
        return (str('delete function can not be function'))

import json
@api.route("/processjson", methods=["POST"])
def create_node_by_file():

    query = """
    create (n:Stock{NAME:$name,CODE:$code})
    """

    data = request.get_json()

    for i in data:
        code = i['CODE']
        name = i['NAME']

        map = {"name": name, "code": code}

        session.run(query, map)

    return display_node()


if __name__ == "__main__":
    api.run(port=5050)
