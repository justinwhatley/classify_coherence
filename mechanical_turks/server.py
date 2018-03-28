from myapp import app

from flask import Flask


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=4000)
    #app.run()
    # app.run(debug=True, use_reloader=False)

    # To host from local machine
    # app.run(host='0.0.0.0')
