from app import app, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This will create the tables in the database
    app.run(debug=True)
