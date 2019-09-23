import { Router } from 'express';
import Experiment from './controller';

const router = Router({ mergeParams: true });

router.get('/:projectId', Experiment.getById);

router.get('/', Experiment.getAllByProjectId);

router.post('/', Experiment.create);

export default router;
