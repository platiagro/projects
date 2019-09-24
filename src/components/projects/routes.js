import { Router } from 'express';
import Project from './controller';
import { ExperimentRoutes } from '../experiments';

const router = Router();

router.use('/:projectId/experiments', ExperimentRoutes);

router.get('/:projectId', Project.getById);

router.get('/', Project.getAll);

router.patch('/:projectId', Project.update);

router.post('/', Project.create);

export default router;
