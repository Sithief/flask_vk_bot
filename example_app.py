from bot_core import main
import database

if __name__ == "__main__":
    database.migration()
    main.app.run(host='0.0.0.0')
