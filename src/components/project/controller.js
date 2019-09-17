import uuidv4 from 'uuid/v4';
import model from './model';

const create = async (req, res) => {
  const { projectName } = req.body;

  const uuid = uuidv4();
  const createdAt = new Date();

  model
    .create(uuid, projectName, createdAt)
    .then((result) => {
      res
        .status(200)
        .json({ message: 'Project created successfully.', payload: result });
    })
    .catch((err) => {
      console.error(err);
      res.sendStatus(500);
    });
};

module.exports = {
  create,
};
