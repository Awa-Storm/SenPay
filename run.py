import os
os.environ["SENPAY_KEY"] = "7228a50ffb3ee0abb0c80b73f4fa3f792949b93261833099825ae08872fe8608"
os.environ["SECRET_KEY"] = "dev_secret_key_123456"
os.environ["DB_PATH"] = "senpay.db"

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=False)
