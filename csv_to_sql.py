import mysql.connector
import pandas as pd
import random
import csv
import uuid
from io import StringIO



def add_id(df):
    df['id'] = [uuid.uuid4() for _ in range(len(df))]
    return df

def add_fight_skills(df):
    martial_arts = [
    "Karate", "Taekwondo", "Judo", "Brazilian Jiu-Jitsu", "Muay Thai",
    "Kung Fu", "Aikido", "Krav Maga", "Capoeira", "Wing Chun",
    "Hapkido", "Jeet Kune Do", "Tai Chi", "Sambo", "Kickboxing",
    "Eskrima", "Savate", "Sambo", "Ninjutsu", "Wu Chu"
    ]
    df['fight_skills'] = df.apply(lambda row: random.sample(martial_arts,3), axis=1)
    return df

#have issues connecting to database:
#mysql.connector.errors.InterfaceError: 2003: Can't connect to MySQL server on '%-.100s:%u' (%s) (Warning: %u format: a real number is required, not str)
def csv_to_sql(csv_content, database, table_name):
    df = pd.read_csv(csv_content)
    
    #Connect to the MySQL database
    db = mysql.connector.connect(
        host="localhost:3306",
        user="username",
        password="password123",
        database=database
    )
    cursor = db.cursor()

    #Iterate over each row in the DataFrame and insert it into the MySQL table
    for _, row in df.iterrows():
        sql = "INSERT INTO {} (id, name, dob, fight_skills) VALUES (%s, %s, %s, %s)".format(table_name)
        val = (str(row['id']), row['name'], row['dob'], row['fight_skills'])
        cursor.execute(sql, val)
    
    #commit the changes and close the cursor and database connection
    db.commit()
    cursor.close()
    db.close()


def _main():
    csv_file = "warriors_csv.csv"
    database = "warriors_db.db"
    table_name = "warriors"
    #df = pd.read_csv("warriors_csv2.csv")
    #df["dob"] = df['dob'] = df['dob'].apply(lambda x: pd.to_datetime(x, format='%d/%m/%Y').strftime('%Y-%d-%m'))

    #print(df)
    #df.to_csv("warriors_csv.csv", index=False)

    csv_to_sql(csv_file, database, table_name)

#def _main():
#    csv_file = "warriors_csv.csv"
#    csv_string = ""
#    with open(csv_file, "r") as file:
#        csvreader = csv.reader(file)
#        for row in csvreader:
#            csv_string += ",".join(row) + "\n"
#    csv_stringIO = StringIO(csv_string)
    #df = pd.read_csv(csv_stringIO)

    #add_id(df)
    #add_fight_skills(df)

    #print(df.head(10))
    #df.to_csv("csv_file.csv", index=False)
#    csv_to_sql(csv_stringIO, "warriors_db.db", "warriors")

if __name__ == "__main__":
    _main()