import pymysql
from faker import Faker
import random

# Conexión a la base de datos MySQL
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='653489',
    db='test'
)

# Crear un cursor, permite ejecutar comando SQL a través de 'connection'
cursor = connection.cursor()

# Crear tabla
create_table_query = """CREATE TABLE IF NOT EXISTS DEVICE_DATA (
                            DeviceName varchar(50),
                            Id varchar(10),
                            CompanyId varchar(50),
                            NumberOfBottles int(10),
                            PRIMARY KEY (Id),
                            CONSTRAINT fk_device_data_companies FOREIGN KEY (CompanyId) REFERENCES companies(CompanyId)
                            );"""
cursor.execute(create_table_query)

# Generar datos aleatorios y guardarlos en la base de datos
fake = Faker()

for i in range(1000):
    device_name = random.choice(['Sidel Matrix', 'CA-LC', 'Trinean Xpose'])
    company_id = random.randint(1, 4)
    company_id_str = f"{company_id:04d}"
    id_str = f"{company_id:04d}{i+1:04d}"
    num_bottles = random.randint(1, 1000)

    insert_query = f"""INSERT INTO DEVICE_DATA (DeviceName, Id, CompanyId, NumberOfBottles)
                        VALUES ('{device_name}', '{id_str}', {company_id}, {num_bottles})"""
    cursor.execute(insert_query)

connection.commit()
connection.close()
cursor.close()