import uuidv4 from 'uuid/v4';
import Experiment from './model';

const create = async (req, res) => {
  console.log(req.params);
  const { projectId } = req.params;
  const { experimentName } = req.body;

  const uuid = uuidv4();
  const createdAt = new Date();

  await Experiment.create(uuid, experimentName, projectId, createdAt)
    .then((result) => {
      res
        .status(200)
        .json({ message: 'Experiment created successfully.', payload: result });
    })
    .catch((err) => {
      console.error(err);
      res.sendStatus(500);
    });
  return res;
};

module.exports = {
  create,
};
