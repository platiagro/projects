import uuidv4 from 'uuid/v4';
import ExperimentComponents from './model';

const getById = async (req, res) => {
  const { uuid } = req.params;

  await ExperimentComponents.getById(uuid)
    .then(async (component) => {
      res.status(200).json({ payload: component });
    })
    .catch((err) => {
      console.error(err);
      if (err.message === 'Invalid UUID.') {
        res.status(400).json({ message: `Component UUID doesn't exists.` });
      } else {
        res.sendStatus(500);
      }
    });
  return res;
};

const getAll = async (req, res) => {
  const { experimentId } = req.params;

  await ExperimentComponents.getAll(experimentId)
    .then((components) => {
      res.status(200).json({ payload: components });
    })
    .catch((err) => {
      console.error(err);
      res.sendStatus(500);
    });
  return res;
};

const create = async (req, res) => {
  const { experimentId } = req.params;
  const { componentId, position } = req.body;

  const uuid = uuidv4();
  const createdAt = new Date();

  await ExperimentComponents.create(
    uuid,
    experimentId,
    componentId,
    createdAt,
    position
  )
    .then(async (component) => {
      res.status(200).json({
        message: 'Experiment Component created successfully.',
        payload: component,
      });
    })
    .catch((err) => {
      console.error(err);
      res.sendStatus(500);
    });
  return res;
};

const update = async (req, res) => {
  const { uuid } = req.params;

  const { experimentId, componentId, position } = req.body;

  await ExperimentComponents.getById(uuid)
    .then(async (component) => {
      await component
        .update(experimentId, componentId, position)
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
        res
          .status(400)
          .json({ message: `Experiment Component UUID doesn't exists.` });
      } else {
        res.sendStatus(500);
      }
    });
  return res;
};

const deleteComponent = async (req, res) => {
  const { uuid } = req.params;

  await ExperimentComponents.getById(uuid)
    .then(async (component) => {
      await component
        .delete(uuid)
        .then(() => {
          res.status(200).json({
            message: 'Deleted successfully',
          });
        })
        .catch((err) => {
          console.error(err);
          res.sendStatus(500);
        });
    })
    .catch((err) => {
      console.error(err);
      if (err.message === 'Invalid UUID.') {
        res.status(400).json({ message: `Component UUID doesn't exists.` });
      } else {
        res.sendStatus(500);
      }
    });

  return res;
};

module.exports = {
  getById,
  getAll,
  create,
  update,
  deleteComponent,
};
