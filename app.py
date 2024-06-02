from flask import Flask, jsonify, request
from flask_cors import CORS
from solders.keypair import Keypair
from solana.rpc.api import Client
from solders.rpc.responses import GetAccountInfoResp,GetBalanceResp
import qrcode
import pymongo
from PIL import Image
import base64
import io,os
from dotenv import load_dotenv
# Initialize Flask app
load_dotenv()
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Initialize Solana client
solana_client = Client("https://api.devnet.solana.com")
DB=os.getenv("DB_URL")
# Initialize MongoDB client
mongo_client = pymongo.MongoClient(DB)
db = mongo_client["wallets_data"]
collection = db["wallets"]

# Route to create a new wallet
@app.route('/create_wallet', methods=['POST'])
def create_wallet():
    # Generate a new Solana wallet
    keypair = Keypair()
    public_key = keypair.pubkey()
    private_key = keypair.secret()

    # Log the public and private keys to the console
    print("Public Key:", public_key)
    print("Private Key:", private_key.hex())

    # Store private key in MongoDB
    collection.insert_one({"public_key": str(public_key), "private_key": private_key.hex()})

    # Generate QR code for the wallet address
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(public_key))
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Get balance of the new wallet
    balance_response = solana_client.get_balance(public_key)
    balance = balance_response.value if isinstance(balance_response, GetBalanceResp) else 0
  
   

    return jsonify({
        "public_key": str(public_key),
        "qr_code": img_str,
        "balance": balance
    })

# Main function to run the app
if __name__ == "__main__":
    app.run(debug=True)
