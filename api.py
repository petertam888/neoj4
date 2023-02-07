from flask import Flask, request, jsonify
from neo4j import GraphDatabase
import csv

# establish the connection

with open("cred.txt") as fl:
    data = csv.reader(fl, delimiter=',')
    for row in data:
        username = row[0]  # account name:neo4j
        pwd = row[1]  # password:neo4j
        uri = row[2]

driver = GraphDatabase.driver(uri=uri, auth=(username, pwd))
session = driver.session()
api = Flask(__name__)



@api.route("/company/<string:company_name>&<string:code>&<string:profit>", methods=["GET", "POST"])
def create_company_node(company_name, code, profit):
    query = """
    create (c:Company {Company: $company_name, Code: $code, Profit: $profit})
    """
    map = {"company_name": company_name, "code": code, "profit": profit}
    try:
        session.run(query, map)

        return (f"The data is imported : {company_name} , and {code} net profit is {profit}")
    except Exception as e:
        return (str(e))


@api.route("/processjson/company", methods=["POST"])
def create_company_node_by_file():
    query = """
    create (c:Company {Company: $company_name, Code: $code, Profit: $profit})
    """

    data = request.get_json()

    for i in data:
        company_name = i['Company']
        code = i['Code']
        profit = i['Profit']

        map = {"company_name": company_name, "code": code, "profit": profit}
        session.run(query, map)

    return "Success !!!"

@api.route("/person/<string:title>/<string:name>&<string:born>&<string:company_name>", methods=["GET", "POST"])
def create_person_node(name, born, title, company_name):
    query = """
    create (p:Person {Name: $name, Title: $title, Born: $born, Company: $company_name })
    """
    map = {"name": name, "title": title, "born": born, "company_name": company_name}
    try:
        session.run(query, map)

        return (f"The entity - {name} is created ! ")
    except Exception as e:
        return (str(e))

@api.route("/processjson/person", methods=["POST"])
def create_person_node_by_file():
    query = """
    create (p:Person {Name: $name, Title: $title, Born: $born, Company: $company_name })
    """

    data = request.get_json()

    for i in data:
        name = i['Name']
        title = i['Title']
        born = i['Born']
        company_name = i['Company']

        map = {"name": name, "title": title, "born": born, "company_name": company_name}
        session.run(query, map)

    return "Success !!!"


@api.route("/mkrelate/<string:title>/<string:name>&<string:company_name>", methods=["GET", "POST"])
def make_ceo_company_relationship(title, name, company_name):

    if title == "CEO" or "ceo":
        query = "MATCH (n:Person),(c:Company) WHERE n.Name = $name AND c.Company = $company_name CREATE (n)-[:CEO]->(c) RETURN n"
    elif title == "CFO" or "cfo":
        query = "MATCH (n:Person),(c:Company) WHERE n.Name = $name AND c.Company = $company_name CREATE (n)-[:CFO]->(c) RETURN n"
    else:
        return ("invalid input")

    map = {"name": name, "company_name": company_name}

    try:
        session.run(query, map)
        return(f"the {title}-relationship is made.")

    except Exception as e:
        return (str(e))


@api.route("/person/display", methods=["GET", "POST"])
def display_node():
    query = """
    match (p) WHERE p.Title IS NOT NULL return p.Name as Name, p.Born as Born, p.Title as Title, p.Company as Company
    """
    results = session.run(query)

    data = results.data()
    return (jsonify(data))

@api.route("/profit/<string:company_name>/update_to_<string:profit>", methods=["PUT"])
def update_node(company_name, profit):

    session.run("MATCH (c:Company {Company: $company_name}) SET c.Profit = $profit", company_name=company_name, profit=profit)
    return jsonify({'message': 'Company info updated'})


@api.route("/delete_relationship/<string:name>/<string:company>", methods=["DELETE"])
def delete_relationship(name, company):

    query = "MATCH (p:Person)-[rel:CEO]->(c:Company) WHERE p.Name = $name AND c.Company = $company DELETE rel "

    try:
        session.run(query, name=name, company=company)

        return (f" The relationship is deleted in the database")
    except Exception as e:
        return (str('delete function can not be function'))


@api.route("/delete_<string:var>/<string:name>", methods=["DELETE"])
def delete_node(var, name):

    if var == "ceo" or "cfo":
        query = "MATCH (n:Person {Name: $name}) DELETE n"

    elif var == "company":
        query = "MATCH (n:Company {Company: $name}) DELETE n "

    map = {"name": name}

    try:
        session.run(query, map)

        return (f" The {var} is deleted in the database")
    except Exception as e:
        return (str('delete function can not be function, please check the relationship have been deleted or not first'))



if __name__ == "__main__":
    api.run(port=5050)
