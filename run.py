from flaskblog import app

if __name__ == '__main__':
    # Make the app accessible over LAN
    app.run(host='0.0.0.0', port=5000, debug=False)
