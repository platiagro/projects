import uuidv4 from 'uuid/v4';
import Project from './model';

const getById = async (req, res) => {
  const { projectId } = req.params;

  await Project.getById(projectId)
    .then((project) => {
      res.status(200).json({ payload: project });
    })
    .catch((err) => {
      console.error(err);
      if (err.message === 'Invalid UUID.') {
        res.status(400).json({ message: `Project UUID doesn't exists.` });
      } else {
        res.sendStatus(500);
      }
    });
  return res;
};

const getAll = async (req, res) => {
  await Project.getAll()
    .then((projects) => {
      res.status(200).json({ payload: projects });
    })
    .catch((err) => {
      console.error(err);
      res.sendStatus(500);
    });
  return res;
};

const update = async (req, res) => {
  const { projectId, projectNewName } = req.body;

  await Project.getById(projectId)
    .then((project) => {
      project
        .update(projectNewName)
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
        res.status(400).json({ message: `Project UUID doesn't exists.` });
      } else {
        res.sendStatus(500);
      }
    });
  return res;
};

const create = async (req, res) => {
  const { projectName } = req.body;

  const uuid = uuidv4();
  const createdAt = new Date();

  await Project.create(uuid, projectName, createdAt)
    .then((result) => {
      res
        .status(200)
        .json({ message: 'Project created successfully.', payload: result });
    })
    .catch((err) => {
      console.error(err);
      res.sendStatus(500);
    });
  return res;
};

module.exports = {
  getById,
  getAll,
  update,
  create,
};
