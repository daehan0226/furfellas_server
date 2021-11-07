from app import create_app, set_db

if __name__ == "__main__":
    app = create_app()
    set_db(app)
    app.run(host="0.0.0.0", port=8080, debug=True)
