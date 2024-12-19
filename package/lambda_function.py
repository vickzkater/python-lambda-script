import os
import csv
import boto3
import psycopg2
from datetime import datetime

# Environment Variables (konfigurasi di AWS Lambda)
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
S3_BUCKET = os.environ['S3_BUCKET']
S3_KEY_PREFIX = os.environ['S3_KEY_PREFIX']

def lambda_handler(event, context):
    try:
        schema_name = "vic_db"

        # Keterangan waktu
        date_label = datetime.now().strftime('%Y%m%d')
        datetime_label = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Daftar tabel yang ingin di-query
        table_names = ["customers", "orders", "order_details", "products", "order_confirmations"]

        # Koneksi ke database PostgreSQL
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()
        
        s3_client = boto3.client('s3')
        
        # Proses perulangan untuk setiap tabel
        for table_name in table_names:
            try:
                # Nama file CSV untuk setiap tabel
                file_name = f"{schema_name}.{table_name}_{datetime_label}.csv"
                temp_file_path = f"/tmp/{file_name}"
                
                # Tentukan query berdasarkan tabel
                if table_name == "order_confirmations":
                    query = f"SELECT id, order_id, created_at, created_by_id, updated_at, updated_by_id, status FROM {table_name}"
                else:
                    query = f"SELECT * FROM {table_name}"
                    
                # Eksekusi query
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]  # Kolom tabel
                
                # Menulis hasil query ke file CSV
                with open(temp_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(columns)  # Header kolom
                    writer.writerows(cursor.fetchall())  # Data rows
                
                print(f"File {file_name} successfully created in /tmp/")
                
                # Upload file ke AWS S3
                s3_key = f"{S3_KEY_PREFIX}/{date_label}/{file_name}"
                s3_client.upload_file(temp_file_path, S3_BUCKET, s3_key)
                print(f"File uploaded to S3: {S3_BUCKET}/{s3_key}")
            
            except Exception as table_error:
                print(f"Error processing table {table_name}: {str(table_error)}")
        
        # Response sukses untuk semua tabel
        return {
            "statusCode": 200,
            "body": f"All reports successfully uploaded to S3 under {S3_KEY_PREFIX}/{date_label}/"
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
    
    finally:
        # Tutup koneksi database
        if cursor:
            cursor.close()
        if connection:
            connection.close()
