import uuidv4 from 'uuid/v4';
import Project from './model';

const createProject = async (req, res) => {
  const { projectName } = req.body;

  const uuid = uuidv4();
  const createdAt = new Date();

  try {
    const result = await Project.create(uuid, projectName, createdAt);
    res
      .status(200)
      .json({ message: 'Project created successfully.', payload: result });
  } catch (err) {
    console.error(err);
    res.sendStatus(500);
  }
};

module.exports = {
  createProject,
};
