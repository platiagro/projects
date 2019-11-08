import cors from 'cors';
import express from 'express';
import { ComponentsRoutes } from './components/components';
import { ProjectRoutes } from './components/projects';

const app = express();

app.use(cors());

app.use(express.json());

app.use('/components', ComponentsRoutes);

app.use('/projects', ProjectRoutes);

app.get('/', (req, res) => {
  res.status(200).send('PlatIAgro Projects Manager');
});

module.exports = app;
