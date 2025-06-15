import csv
import mysql.connector


class MySQLHelper:
    def __init__(self, host='127.0.0.1', user='root', password='1234', database='mars_db'):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS mars_weather (
            weather_id INT PRIMARY KEY,
            mars_date DATETIME NOT NULL,
            temp FLOAT,
            stom INT
        )
        '''
        self.cursor.execute(query)
        self.connection.commit()

    def insert_data(self, csv_file_path):
        with open(csv_file_path, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                query = '''
                INSERT IGNORE INTO mars_weather (weather_id, mars_date, temp, stom)
                VALUES (%s, %s, %s, %s)
                '''
                values = (
                    int(row['weather_id']),
                    row['mars_date'],
                    float(row['temp']),
                    int(row['stom'])
                )
                self.cursor.execute(query, values)
            self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()


if __name__ == '__main__':
    helper = MySQLHelper()
    helper.create_table()
    helper.insert_data('mars_weathers_data.CSV')  
    helper.close()
