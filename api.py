import  os
import  sqlite3

from flask import Flask, request, Response
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename
from minio import Minio
from minio.error import ResponseError

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
UPLOAD_FOLDER = '/tmp'
BUCKET_NAME = 'scaleway'

app = Flask(__name__)
api = Api(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Image(Resource):
    def get(self, id = None):
        """
            Endpoint  : GET /images || GET /images/<int:id>
            Desc1     : List all images like data[id] = {name, description, URI}
            Desc2     : Get image
            Error     : Error if 'id' doesn't exist
        """
        if id == None:
            cursor = bdd.cursor()
            cursor.execute("SELECT * FROM images")
            result = {'data': {}}
            for row in cursor:
                result['data'][row[0]] = {'name': row[2], 'description': row[3], 'uri': "http://127.0.0.1:5000/image/" + str(row[0])}
            return result
        cursor = bdd.cursor()
        req = cursor.execute("SELECT imagename FROM images where id = ?", (id,))
        data = cursor.fetchone()
        if data == None:
            return {'error': "This id doesn't match with any image"}
        stream = minioClient.get_object(BUCKET_NAME, data[0])
        extension = data[0].rsplit('.', 1)[1].lower()
        response = app.make_response(stream.read())
        response.mimetype = "image/" + extension
        return response

    def post(self):
        """
            Endpoint : POST /image
            Desc     : Add image, name, description (optional) in database and in bucket
            Error    : Error if filename exist or bad filename or bad extention
        """
        if 'image' not in request.files or 'name' not in request.form:
            return {'error': "No file part or No 'name' paramters"}
        else:
            image = request.files['image']
            name = request.form['name']
            description = None if 'description' not in request.form else request.form['description']
            if image and allowed_file(image.filename):
                imagename = secure_filename(image.filename)
                try:
                    minioClient.stat_object(BUCKET_NAME, imagename)
                    return {'error': 'The filename is already used'}
                except:
                    image.save(os.path.join(UPLOAD_FOLDER, imagename))
                    data = open(os.path.join(UPLOAD_FOLDER, imagename), 'rb')
                    size = os.stat(os.path.join(UPLOAD_FOLDER, imagename)).st_size
                    minioClient.put_object(BUCKET_NAME, imagename, data, size, image.content_type)
                    os.remove(os.path.join(UPLOAD_FOLDER, imagename))
                    cursor = bdd.cursor()
                    cursor.execute("INSERT INTO images (imagename, name, description) VALUES (?, ?, ?)", (imagename, name, description))
                    last_id = cursor.lastrowid
                    bdd.commit()
                    return {'success': 'http://127.0.0.1:5000/image/' + str(last_id)}
            return {'error': 'Format allowed is .png .jpg .jpeg .gif or bad filename'}

    def delete(self, id):
        """
            Endpoint : DELETE /image/<int:id>
            Desc     : Delete image from 'id' in database and in bucket
            Error    : Error if 'id' doesn't exist
        """
        cursor = bdd.cursor()
        req = cursor.execute("SELECT imagename FROM images where id = ?", (id,))
        data = cursor.fetchone()
        if data == None:
            return {'error': "This id doesn't match with any image"}
        cursor.execute("DELETE FROM images where id = ?", (id,))
        bdd.commit()
        minioClient.remove_object(BUCKET_NAME, data[0])
        return {'success': 'Image has successfully deleted'}

api.add_resource(Image, '/image', '/image/<int:id>', endpoint="image_get_delete")

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    bdd = sqlite3.connect('s3.db', check_same_thread=False)
    bdd.execute("""
    CREATE TABLE IF NOT EXISTS images(
            `id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `imagename` TEXT  NOT NULL,
            `name` TEXT  NOT NULL,
            `description` TEXT DEFAULT NULL
        );
    """)
    minioClient = Minio(
        '127.0.0.1:9000',
        access_key='SCALEWAYS3LIKE',
        secret_key='424242424242',
        secure=False
    )
    if minioClient.bucket_exists(BUCKET_NAME) == False:
        minioClient.make_bucket(BUCKET_NAME)
    app.run(debug=True)
