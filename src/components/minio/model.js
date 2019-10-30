import minioClient from '../../config/minio';

class Minio {
  static createBucketStore(bucketName) {
    return new Promise((resolve, reject) => {
      minioClient.makeBucket(bucketName, (err) => {
        if (err) reject(err);
        else resolve(true);
      });
    });
  }

  static bucketExistsStore(bucketName) {
    return new Promise((resolve, reject) => {
      minioClient.bucketExists(bucketName, (err, exists) => {
        if (err) reject(err);
        else resolve(exists);
      });
    });
  }

  static uploadFile(bucketName, path, file) {
    return new Promise((resolve, reject) => {
      minioClient
        .fPutObject(bucketName, path, file, {})
        .then((result) => {
          resolve(result);
        })
        .catch((error) => {
          reject(error);
        });
    });
  }

  static downloadStream(bucketName, path) {
    return new Promise((resolve, reject) => {
      minioClient.getObject(bucketName, path, (err, stream) => {
        if (err) reject(err);
        resolve(stream);
      });
    });
  }

  static getFiles(bucketName, prefix) {
    return new Promise((resolve, reject) => {
      const files = [];
      const stream = minioClient.listObjects(bucketName, prefix, true);
      stream.on('data', (obj) => {
        files.push(obj);
      });
      stream.on('end', () => {
        resolve(files);
      });
      stream.on('error', (err) => {
        reject(err);
      });
    });
  }

  static deleteFolder(bucketName, prefix) {
    return new Promise((resolve, reject) => {
      const files = [];
      const stream = minioClient.listObjects(bucketName, prefix, true);
      stream.on('data', (obj) => {
        files.push(obj.name);
      });
      stream.on('end', () => {
        minioClient.removeObjects(bucketName, files, (err) => {
          if (err) {
            reject(err);
          }
          resolve('Removed the objects successfully');
        });
      });
      stream.on('error', (err) => {
        reject(err);
      });
    });
  }

  static deleteFile(bucketName, prefix) {
    return new Promise((resolve, reject) => {
      minioClient.removeObject(bucketName, prefix, (err) => {
        if (err) {
          reject(err);
        }
        resolve('Removed the object successfully');
      });
    });
  }
}

export default Minio;
