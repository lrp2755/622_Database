## Authors
Lianna Pottgen, lrp2755@rit.edu
Samuel Roberts, svr9047@rit,edu
Eton Mu, ym5445@rit.edu

## Application Overview

Our program is based off of a fake financial investing institution that will help our group to
determine how data security and privacy affects users private information. Our fake financial
institution has 3 main roles, a Client who gives up information in order to invest their money
in a company and has 1 financial advisor, an Advisor who is involved in protecting their client
data and has 1...n clients, and a Manager who has 1...n employees and can see the 1...n clients
that their employees have.

Additionally, our program runs on Microsoft AD. This allows for users information to be stored in a 
cloud database. This gives the advantage of having consistent data between different runs of our 
program. In the begginging of our program, our database was local which gave us the advantage of 
having data be a bit more efficient in retaining and accessiblity. However, it did change on 
all occurances of create_database.py since it utilized randomly generated data. 

Our future goals for the program is to utilize this program to analyze how important data security
and privacy are for users. More specifically, this program will help us to view how chain of command
comes into play with data security and privacy with our programs ability to have managers view client
information.

## Dependencies
    1.) pip install flask
    2.) pip install faker
    3.) pip install werkzeug
Flask is our API handler and helps us to start up our API and website portion of our program.

Faker is a small import that simply helps us to randomize data for random data generation. We
utilize this in order to create information like fake phone numbers, fake names, fake ssn,
etc..

Werkzeug is an addition that helps with our security hashing for passwords and ssn.

## Steps to Start The Program
    1.) Install dependencies
        a.) pip install flask
        b.) pip install faker
        c.) pip install werkzeug
        d.) pip install cryptography
        e.) pip install psycopg2-binary
        f.) pip install sqlalchemy psycopg2-binary
    2.) psql "host=ritfinanceserver622.postgres.database.azure.com port=5432 dbname=postgres user=LiannaPottgen@ritfinanceserver622 password=Test1234! sslmode=require"
    3.) python create_data.py
        a.) note the passwords given for each account, they are randomly created. 
    4.) python app.py

## Steps to utilize API
    Users:
        Manager:
            email: manager@example.com
            password is given via python create_data.py
        Advisor:
            email: advisor@example.com
            password is given via python create_data.py
        Client:
            email: client@example.com
            password is given via python create_data.py

## Systems & Applications Used
