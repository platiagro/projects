import uuidv4 from 'uuid/v4';
import Experiment from './model';

const getById = async (req, res) => {
  const { experimentId } = req.params;

  await Experiment.getById(experimentId)
    .then((experiment) => {
      res.status(200).json({ payload: experiment });
    })
    .catch((err) => {
      console.error(err);
      if (err.message === 'Invalid UUID.') {
        res.status(400).json({ message: `Experiment UUID doesn't exists.` });
      } else {
        res.sendStatus(500);
      }
    });
  return res;
};

const getAllByProjectId = async (req, res) => {
  const { projectId } = req.params;

  await Experiment.getAllByProjectId(projectId)
    .then((experiments) => {
      res.status(200).json({ payload: experiments });
    })
    .catch((err) => {
      console.error(err);
      res.sendStatus(500);
    });
  return res;
};

const update = async (req, res) => {
  const { experimentId } = req.params;

  const {
    newName,
    newPipelineId,
    newDatasedId,
    newTargetColumnId,
    newParameters,
  } = req.body;

  await Experiment.getById(experimentId)
    .then((experiment) => {
      experiment
        .update(
          newName,
          newPipelineId,
          newDatasedId,
          newTargetColumnId,
          newParameters
        )
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
        res.status(400).json({ message: `Experiment UUID doesn't exists.` });
      } else {
        res.sendStatus(500);
      }
    });
  return res;
};

const create = async (req, res) => {
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
  getById,
  getAllByProjectId,
  update,
  create,
};
