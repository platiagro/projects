import { Router } from 'express';
import Project from './controller';
import { ExperimentRoutes } from '../experiment';

const router = Router();

router.use('/:projectId/experiments', ExperimentRoutes);

router.get('/:projectId', Project.getById);

router.get('/', Project.getAll);

router.patch('/', Project.update);

router.post('/', Project.create);

export default router;
