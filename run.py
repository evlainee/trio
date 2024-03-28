# файл: run.py
import os
from app_factory import create_app

app = create_app()
download_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
app.config['DOWNLOAD_FOLDER'] = download_folder


if __name__ == '__main__':
    app.run(debug=True)
