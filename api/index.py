
from flask import Flask, jsonify, request
from flask_cors import CORS
from Crypto.Cipher import AES
from werkzeug.urls import url_quote
import psycopg2
import base64
import sys

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS)

# Define PostgreSQL database connection credentials
POSTGRES_URL = "postgres://default:KurVLDch6jO4@ep-shiny-mode-a4xv53xr-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"
POSTGRES_USER = "default"
POSTGRES_HOST = "ep-shiny-mode-a4xv53xr-pooler.us-east-1.aws.neon.tech"
POSTGRES_PASSWORD = "KurVLDch6jO4"
POSTGRES_DATABASE = "verceldb"

# Attempt to connect to PostgreSQL database
try:    
    mydb = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DATABASE,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
except psycopg2.Error as e:
    print('Unable to connect with database due to ', e)
    sys.exit()

# Configure Flask app settings
app.config['SECRET_KEY'] = 'Infinicue'  # Set secret key for Flask app
app.config['SESSION_COOKIE_SECURE'] = True  # Set session cookie to be secure

@app.route('/')
def index():
    return 'Connected'

@app.route('/post', methods=['GET', 'POST'])
def qr_code():
    if request.method == 'POST':  # Handling "POST" request from the application front. Qr code scan and post the data to the server.
        df2 = request.get_json(force=True)  # In Json payload.
        df1 = df2['QRcode']
        ff = base64.b64decode(df1)  # decode data using base64 decoder
        key = 'helloworldhelloo'.encode('utf-8')  # unique key used for decryption [note: should be same at app end]
        text = 'helloworldhello'.encode('utf-8')  # text string used for aes decryption [note: should be same at app end]
        iv = 'helloworldhelloo'.encode('utf-8')  # IV string used for aes decryption [note: should be same at app end]
        aes = AES.new(key, AES.MODE_CBC, iv)  # syntax for aes decryption
        en = aes.decrypt(ff)
        en_str = en.decode('utf-8')
        QR_code = en_str.split(',')
        barcode_no = QR_code[2]
        version = QR_code[3]
        ble_mac_id = QR_code[1]
        qr_code = QR_code[0]
        device_idd = QR_code[5]
        product = QR_code[4]
        # Check Whether user already registered as a salvus user
        mycursor = mydb.cursor()
        mycursor.execute("ROLLBACK")
        mydb.commit()
        mycursor.execute('SELECT qrcode, device_id FROM infinicue_master_table WHERE qrcode=%s AND product=%s', [qr_code, product])
        existed_data = mycursor.fetchone()
        # First check if there is any existing barcode in the barcode table using barcode as a primary key.
        if not existed_data:
            mycursor.execute('SELECT barcodeno FROM barcode WHERE barcodeno=%s', [barcode_no])
            bar = mycursor.fetchone()
            # If it is not there, acknowledge the app that it is not existed.
            if not bar:
                return jsonify({"message": "unsuccessful"})
            else:
                # Check if the existing data is there in the qr code table using barcode as a primary key.
                mycursor.execute('SELECT barcodeno FROM qrcode WHERE barcodeno=%s', [barcode_no])
                barcodeno_qr = mycursor.fetchone()
                # If not existing QR code present
                if not barcodeno_qr:
                    return jsonify({"message": "unsuccessful"})
                else:
                    mycursor.execute('SELECT name, email, phone FROM retailer_user WHERE barcodeno = %s', [barcode_no])
                    res = mycursor.fetchone()
                    if not res:
                        return jsonify({'message': 'successful'})
                    else:
                        return jsonify({'name': res[0], 'email': res[1], 'phone': res[2], 'message': 'successful'})
        else:
            if existed_data[1] == device_idd:
                mycursor.execute('SELECT name, email, phone FROM retailer_user WHERE barcodeno = %s', [barcode_no])
                res = mycursor.fetchone()
                if not res:
                    return jsonify({'message': 'successful'})
                else:
                    return jsonify({'name': res[0], 'email': res[1], 'phone': res[2], 'message': 'successful'})
            else:
                return jsonify({'message': 'successful'})

# Run Flask app
if __name__ == '__main__':
    print("Connected")  # Print "Connected" to indicate successful connection
    app.run(debug=True)
