from app import create_app, set_db, run_schedulers

if __name__ == "__main__":
    app = create_app()
    set_db(app)
    run_schedulers()
    app.run(host="0.0.0.0", port=8080, debug=True)
