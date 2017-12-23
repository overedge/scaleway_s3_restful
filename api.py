import  os
import  sqlite3
from    flask          import Flask, request
from    flask_restful  import Resource, Api
from    werkzeug.utils import secure_filename
from    minio          import Minio
from    minio.error    import ResponseError


ALLOWED_EXTENSIONS  = ['png', 'jpg', 'jpeg', 'gif']
UPLOAD_FOLDER       = '/tmp'
BUCKET_NAME         = 'scaleway'

app = Flask(__name__)
api = Api(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Image(Resource):
    def get(self):
        return "ICI JE LISTE TOUT LES UPLOAD"
    def post(self):
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
                    cursor.execute("INSERT INTO images (name, description) VALUES (?, ?)", (name, description))
                    last_id = cursor.lastrowid
                    bdd.commit()
                    return {'success': 'http://localhost:5000/' + str(last_id)}
            else:
                return {'error': 'Format allowed is .png .jpg .jpeg .gif or bad filename'}
    def delete(self):
        return "ICI JE SUPRIME UNE PHOTO"

api.add_resource(Image, '/')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    bdd = sqlite3.connect('s3.db', check_same_thread=False)
    bdd.execute("CREATE TABLE IF NOT EXISTS images ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `name` TEXT  NOT NULL, `description` TEXT DEFAULT NULL);")
    minioClient =   Minio('127.0.0.1:9000',
                    access_key='SCALEWAYS3LIKE',
                    secret_key='424242424242',
                    secure=False)
    if minioClient.bucket_exists(BUCKET_NAME) == False:
        minioClient.make_bucket(BUCKET_NAME)
    app.run(debug=True)
