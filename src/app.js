import cors from 'cors';
import express from 'express';
import { ProjectRoutes } from './components/project';

const app = express();

app.use(cors());

app.use(express.json());

app.use('/projects', ProjectRoutes);

app.get('/', (req, res) => {
  res.status(200).send('PlatIAgro Projects Manager');
});

module.exports = app;
