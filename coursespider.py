import scrapy
import json
import mysql.connector
import pymongo
import logging
import boto3
from io import BytesIO
from reportlab.pdfgen import canvas

class Course:
    def __init__(self, title, description):
        self.title = title
        self.description = description

class CourseSpider(scrapy.Spider):
    name = "course_spider"
    start_urls = ["https://ineuron.ai/courses"]

    headers = {
        "accept" : "*/*",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50"
        }

    def parse(self, response):
        # Extract the URL of the courses JSON file
        courses_url = "https://ineuron.ai/_next/data/7pSHwtHY9vvg6WTd3kBvC/courses.json"

        # Send a request to the courses JSON file
        yield scrapy.Request(courses_url, callback=self.parse_courses, headers=self.headers)

    def parse_courses(self, response):
        # Parse the JSON response and extract the course details
        courses_json = json.loads(response.body)

        try:
            # Connect to the MySQL database
            cnx = mysql.connector.connect(user='<USER>', password='<PASSWORD>',
                                          host='<HOST>', database='<DB_NAME>')
            cursor = cnx.cursor()

            # Create the table to hold the scraped data
            create_table_query = """
            CREATE TABLE IF NOT EXISTS courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                description TEXT
            )
            """
            cursor.execute(create_table_query)

            for course in courses_json["pageProps"]["initialState"]["filter"]["initCourses"]:
                # Extract the course name, description
                title = course["title"]
                description = course["description"]

                # Insert the data into the MySQL table
                insert_query = "INSERT INTO courses (title, description) VALUES (%s, %s)"
                values = (title, description)
                cursor.execute(insert_query, values)
                cnx.commit()

            logging.info("Data has been successfully inserted into the MySQL database.")

            # Close the database connection
            cursor.close()
            cnx.close()

        except mysql.connector.Error as error:
            logging.error(f"Error while connecting to MySQL: {error}")

        try:
            # Connect to the MongoDB Atlas cluster
            client = pymongo.MongoClient("mongodb+srv://<USER>:<PASSWORD>@<CLUSTER>/?retryWrites=true&w=majority")

            # Create a new database and collection
            db = client["ineuron"]
            collection = db["courses"]

            # Insert the scraped course data into the collection
            for course in courses_json["pageProps"]["initialState"]["filter"]["initCourses"]:
                document = {
                    "title": course["title"],
                    "description": course["description"]
                }
                collection.insert_one(document)

            logging.info("Data has been successfully inserted into the MongoDB Atlas cluster.")

            # Close the MongoDB connection
            client.close()

        except pymongo.errors.ConnectionFailure as error:
            logging.error(f"Error while connecting to MongoDB Atlas: {error}")

        
        try:
            # Create a PDF of the scraped course data
            pdf_data = self.create_pdf(courses_json)

            # Upload the PDF to the S3 bucket
            self.upload_to_s3(pdf_data)

        except Exception as error:
            logging.error(f"Error while creating or uploading PDF: {error}")

        
        def create_pdf(self, courses_json):
            try:
                # Generate a PDF report
                report_buffer = BytesIO()
                c = canvas.Canvas(report_buffer)
                c.drawString(50, 800, "Course Report")
                c.drawString(50, 750, "Title\t\tDescription")
                c.drawString(50, 700, "-" * 100)
                y = 650
                for course in courses_json["pageProps"]["initialState"]["filter"]["initCourses"]:
                    title = course["title"]
                    description = course["description"]
                    c.drawString(50, y, f"{title}\t\t{description}")
                    y -= 50
                c.save()

                return report_buffer.getvalue()

            except Exception as e:
                logging.error(f"Failed to generate PDF: {e}")

        def upload_to_s3(self, data):
            try:
                # Upload the PDF report to S3
                s3 = boto3.client('s3', aws_access_key_id='<AWS_KEY_ID>', aws_secret_access_key='<AWS_SECRET_KEY>')
                s3.put_object(Body=data, Bucket='preetipdfs', Key='course-report.pdf')
                logging.info("PDF has been successfully uploaded to S3.")
            except Exception as e:
                logging.error(f"Failed to upload PDF to S3: {e}")