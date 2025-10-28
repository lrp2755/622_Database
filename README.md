## Overview

Our program is based off of a fake financial investing institution that will help our group to 
determine how data security and privacy affects users private information. Our fake financial 
institution has 3 main roles, a Client who gives up information in order to invest their money
in a company and has 1 financial advisor, an Advisor who is involved in protecting their client 
data and has 1...n clients, and a Manager who has 1...n employees and can see the 1...n clients 
that their employees have. 

Our future goals for the program is to utilize this program to analyze how important data security
and privacy are for users. More specifically, this program will help us to view how chain of command
comes into play with data security and privacy with our programs ability to have managers view client
information. 

## Dependencies
    1.) pip install flask
    2.) pip install faker
    3.) pip install werkzeug
    4.) pip install cryptography
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
    2.) Generate the secret key
        python3
        >> import os, base64
        >> print(base64.b64encode(os.urandom(32)))
        $env:SECRET_KEY="the key from the print statement"
    3.) python create_data.py
    4.) python app.py

## Steps to utilize API
    Users:
        Manager: 
            email: manager@example.com
            password: password
        Advisor:
            email: advisor@example.com
            password: password
        Client:
            email: client@example.com
            password: password

Note: these passwords are temporarily "password" since this will just be utilized for this 
phase since this phase was more focused on the foundation of our project. The rest of our users
do have random passwords that are hashed and in the future our go-to baseline users will also 
have randomized passwords that are hashed.

## Authors
Lianna Pottgen, lrp2755@rit.edu

Samuel Roberts, svr9047@rit,edu