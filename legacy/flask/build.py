import src
from flask_frozen import Freezer
import sys
import os
from src import blog_update_url_generator
import shutil


if __name__ == "__main__":
    app = src.create_app()
    build_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build')


    app.config['FREEZER_REMOVE_EXTRA_FILES'] = False # Set to True if you want to clean up old files
    app.config['FREEZER_DESTINATION'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build')
    app.config['FREEZER_DEFAULT_MIMETYPE'] = 'text/html'
    app.config['FREEZER_RELATIVE_URLS'] = True
    app.config['FREEZER_RELATIVE_URLS_PRETTY'] = True

    app.config['FREEZER_DESTINATION_IGNORE_LIST'] = [
        '.git*',
        '.venv*',
        '__pycache__*',
        '*.pyc',
        '*.sqlite',
        'instance/*' # Prevent freezing the instance folder if it contains sensitive files
    ]
    app.config['FREEZER_FREEZING_OPTIONS'] = {
        'force_extension': True, # This will try to add .html to HTML files
        'html_root_index': False  # Set to True if you want 'url/foo' to be 'url/foo/index.html'
                                 # Set to False if you prefer 'url/foo.html'
    }

    freezer = Freezer(app, with_no_argument_rules=False, log_url_for=False)
    freezer.register_generator(blog_update_url_generator)
    if os.path.exists(build_dir):
        print(f"Removing existing build directory: {build_dir}")
        shutil.rmtree(build_dir)
    print(f"Starting build to: {build_dir}")
    # ----------------------------------------------------
    freezer.freeze()
    print("Build complete!")
