import formidable from 'formidable';
import fs from 'fs';
import rimraf from 'rimraf';
import uuidv4 from 'uuid/v4';
import config from '../../config/config';
import Component from './model';
import { MinioModel } from '../minio';

const create = async (req, res) => {
  const { name } = req.body;

  if (!name) {
    res.status(400).json({ message: 'Name is required.' });
    return res;
  }

  const uuid = uuidv4();
  const createdAt = new Date();

  await Component.create(uuid, createdAt, name)
    .then((result) => {
      res
        .status(200)
        .json({ message: 'Created successfully.', payload: result });
    })
    .catch((err) => {
      console.error(err);
      res.sendStatus(500);
    });
  return res;
};

const update = async (req, res) => {
  const { uuid } = req.params;
  const { name } = req.body;
  const updatedAt = new Date();

  await Component.getById(uuid)
    .then((result) => {
      result
        .update(updatedAt, name)
        .then(() => {
          res.status(200).json({ message: 'Updated successfully.' });
        })
        .catch((err) => {
          console.error(err);
          res.sendStatus(500);
        });
    })
    .catch((err) => {
      console.error(err);
      if (err.message === 'Invalid UUID.') {
        res.status(400).json({ message: `UUID doesn't exists.` });
      } else {
        res.sendStatus(500);
      }
    });
  return res;
};

const deleteById = async (req, res) => {
  const { uuid } = req.params;
  const prefix = `components/${uuid}`;
  await MinioModel.deleteFiles(config.MINIO_BUCKET, prefix)
    .then(() => {
      Component.deleteById(uuid)
        .then(() => {
          res.status(200).json({ message: 'Deleted successfully.' });
        })
        .catch((err) => {
          console.error(err);
          if (err.message === 'Invalid UUID.') {
            res.status(400).json({ message: `UUID doesn't exists.` });
          } else {
            res.sendStatus(500);
          }
        });
    })
    .catch((err) => {
      console.error(err);
      res.sendStatus(500);
    });
  return res;
};

const getAll = async (req, res) => {
  await Component.getAll()
    .then((results) => {
      res.status(200).json({ payload: results });
    })
    .catch((err) => {
      console.error(err);
      res.sendStatus(500);
    });
  return res;
};

const getById = async (req, res) => {
  const { uuid } = req.params;

  await Component.getById(uuid)
    .then((result) => {
      res.status(200).json({ payload: result });
    })
    .catch((err) => {
      console.error(err);
      if (err.message === 'Invalid UUID.') {
        res.status(400).json({ message: `UUID doesn't exists.` });
      } else {
        res.sendStatus(500);
      }
    });
  return res;
};

const upload = async (req, res) => {
  const { uuid } = req.params;

  await Component.getById(uuid)
    .then(() => {
      const dirUploads = `./uploads`;
      if (!fs.existsSync(dirUploads)) {
        fs.mkdirSync(dirUploads);
      }

      const dirComponent = `${dirUploads}/${uuid}`;
      if (!fs.existsSync(dirComponent)) {
        fs.mkdirSync(dirComponent);
      }

      const files = [];
      const form = new formidable.IncomingForm();
      form
        .parse(req)
        .on('fileBegin', (name, file) => {
          file.path = `${dirComponent}/${file.name}`;
        })
        .on('file', (name, file) => {
          files.push(file);
        })
        .on('end', () => {
          if (files.length === 0) {
            res.write(`Uploaded successfully.`);
            res.end();
          } else {
            let itemsProcessed = 0;
            files.forEach(async (file) => {
              await MinioModel.uploadFile(
                config.MINIO_BUCKET,
                `components/${uuid}/${file.name}`,
                file.path
              )
                .then(() => {
                  itemsProcessed += 1;
                  if (itemsProcessed === files.length) {
                    rimraf.sync(dirComponent);
                    res.write(`Uploaded successfully.`);
                    res.end();
                  }
                })
                .catch((err) => {
                  console.error(err);
                  res.sendStatus(500);
                });
            });
          }
        });
    })
    .catch((err) => {
      console.error(err);
      if (err.message === 'Invalid UUID.') {
        res.status(400).json({ message: `UUID doesn't exists.` });
      } else {
        res.sendStatus(500);
      }
    });
};

const download = async (req, res) => {
  const { uuid } = req.params;
  const { fileName } = req.body;

  await MinioModel.downloadStream(
    config.MINIO_BUCKET,
    `components/${uuid}/${fileName}`
  )
    .then((stream) => {
      res.set('Content-disposition', `attachment; filename=${fileName}`);
      stream.on('data', (chunk) => {
        res.write(chunk);
      });
      stream.on('end', () => {
        res.end();
      });
      stream.on('error', (err) => {
        console.error(err);
        res.sendStatus(500);
      });
    })
    .catch((err) => {
      console.error(err);
      if (err.code === 'NoSuchKey') {
        res.status(400).json({ message: `File not exist.` });
      } else {
        res.sendStatus(500);
      }
    });
};

module.exports = {
  create,
  update,
  deleteById,
  getAll,
  getById,
  upload,
  download,
};
