import logging
import os
from flask import render_template, Blueprint, request, make_response, Flask
from werkzeug.utils import secure_filename
from flask import render_template

# STORAGE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
STORAGE_DIRECTORY = "storage"

log = logging.getLogger('pydrop')
app = Flask(__name__)

@app.route("/")
@app.route("/index/")
def index():
    # Route to serve the upload form
    return render_template('index.html')


@app.post("/upload")
def upload_chunk():
    file = request.files["file"]
    file_uuid = request.form["dzuuid"]
    # Generate a unique filename to avoid overwriting using 8 chars of uuid before filename.
    filename = f"{file_uuid[:8]}_{secure_filename(file.filename)}"
    if not os.path.exists(STORAGE_DIRECTORY):
        os.makedirs(STORAGE_DIRECTORY)
    save_path = os.path.join(STORAGE_DIRECTORY, secure_filename(filename))
    # save_path = Path("static", "img", filename)
    current_chunk = int(request.form["dzchunkindex"])

    try:
        with open(save_path, "ab") as f:
            f.seek(int(request.form["dzchunkbyteoffset"]))
            f.write(file.stream.read())
    except OSError:
        return "Error saving file.", 500

    total_chunks = int(request.form["dztotalchunkcount"])

    if current_chunk + 1 == total_chunks:
        # This was the last chunk, the file should be complete and the size we expect
        if os.path.getsize(save_path) != int(request.form["dztotalfilesize"]):
            return "Size mismatch.", 500

    return "Chunk upload successful.", 200


# @app.route('/upload', methods=['POST'])
# def upload():
#     file = request.files['file']
#     if not os.path.exists(STORAGE_DIRECTORY):
#         os.makedirs(STORAGE_DIRECTORY)
#     save_path = os.path.join(STORAGE_DIRECTORY, secure_filename(file.filename))
#     current_chunk = int(request.form['dzchunkindex'])
#
#     # If the file already exists it's ok if we are appending to it,
#     # but not if it's new file that would overwrite the existing one
#     if os.path.exists(save_path) and current_chunk == 0:
#         # 400 and 500s will tell dropzone that an error occurred and show an error
#         return make_response(('File already exists', 400))
#
#     try:
#         with open(save_path, 'ab') as f:
#             f.seek(int(request.form['dzchunkbyteoffset']))
#             f.write(file.stream.read())
#     except OSError:
#         # log.exception will include the traceback so we can see what's wrong
#         log.exception('Could not write to file')
#         return make_response(("Not sure why,"
#                               " but we couldn't write the file to disk", 500))
#
#     total_chunks = int(request.form['dztotalchunkcount'])
#
#     if current_chunk + 1 == total_chunks:
#         # This was the last chunk, the file should be complete and the size we expect
#         if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
#             log.error(f"File {file.filename} was completed, "
#                       f"but has a size mismatch."
#                       f"Was {os.path.getsize(save_path)} but we"
#                       f" expected {request.form['dztotalfilesize']} ")
#             return make_response(('Size mismatch', 500))
#         else:
#             log.info(f'File {file.filename} has been uploaded successfully')
#     else:
#         log.debug(f'Chunk {current_chunk + 1} of {total_chunks} '
#                   f'for file {file.filename} complete')
#
#     return make_response(("Chunk upload successful", 200))