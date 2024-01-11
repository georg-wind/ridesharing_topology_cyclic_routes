# Import required libraries

from dashboard import app

if __name__ == '__main__':
    app.run_server(debug=False)  # set true, um fehler in der app zu catchen - NB: läuft NICHT im IDE-debug mode
