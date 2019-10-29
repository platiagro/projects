import config from '../../config/config';
import Minio from './model';

const verifyBucket = async (req, res, next) => {
  const bucketName = config.MINIO_BUCKET;
  await Minio.bucketExistsStore(bucketName)
    .then((exists) => {
      if (exists) {
        next();
      } else
        Minio.createBucketStore(bucketName)
          .then(() => {
            next();
          })
          .catch((error) => {
            console.log(error);
            res.sendStatus(500);
          });
    })
    .catch((error) => {
      console.log(error);
      res.sendStatus(500);
    });
};

const getFiles = async (req, res) => {
  const { uuid } = req.params;
  const prefix = `components/${uuid}`;
  await Minio.getFiles(config.MINIO_BUCKET, prefix)
    .then((result) => {
      res.status(200).json({ payload: result });
    })
    .catch((err) => {
      console.error(err);
      res.sendStatus(500);
    });
  return res;
};

module.exports = {
  verifyBucket,
  getFiles,
};
