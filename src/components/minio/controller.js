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

const deleteFiles = async (req, res) => {
  const { uuid } = req.params;
  const { files } = req.body;
  const prefix = `components/${uuid}`;

  if (files && files.length > 0) {
    let itemsProcessed = 0;
    files.forEach(async (file) => {
      await Minio.deleteFile(config.MINIO_BUCKET, `${prefix}/${file}`)
        .then(() => {
          res.write(`Successfully delete file ${file}.\n`);
        })
        .catch((err) => {
          console.error(err);
          res.write(`Failed to delete file ${file}.\n`);
        });

      itemsProcessed += 1;
      if (itemsProcessed === files.length) {
        res.end();
      }
    });
  } else {
    res.status(400).json({
      message: `No files send to delete.`,
    });
  }
};

module.exports = {
  verifyBucket,
  getFiles,
  deleteFiles,
};
