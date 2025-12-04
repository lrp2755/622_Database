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
    Applications: 
        -This application utilized Microsoft Entra to act as the cloud database
        for our simulation. In our research, we determined that Microsoft Entra is one of
        the most commonly used cloud databases for large companies. Because of this, our 
        program uses a small cloud database that stores limited information. Our team 
        utilized this Entra database by using the RIT login, so it did not cost us money to
        store the data. 

    Systems:
        -This application utilized Flask in order to handle requests and help the API
        for the front end of our application. Flask is a microservice that will handle using 
        the routes of information from the backend and database into the front end API. 

        - This application also utilize SQLAlchemy as our tool to interact with the local 
        version of our database. Since we utilized SQL, this tool allowed us to analyze how 
        data was moving through our system by giving us direct access to our database

        - This application also utilizes the cryptography package from the python library.
        This package allowed us to encrypt the SSN and PII from users before they were stored
        in the database, and helped in creating our database access key. 

        - This applicationn utilizes the werkzeug.security package from the python library 
        as well to aid in security. This package allowed us to create random data (like 
        names, genders, birthdays, etc...) while we created our fake client, advisors, and 
        managers databases. This aided in our concept of data privacy as well.  
