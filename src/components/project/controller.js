import uuidv4 from 'uuid/v4';
import Project from './model';

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
  getAll,
  create,
};
