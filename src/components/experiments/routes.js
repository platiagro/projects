import { Router } from 'express';
import Experiment from './controller';
import { ExperimentComponentsRoutes } from '../experiment-components';

const router = Router({ mergeParams: true });

router.use('/:experimentId/components', ExperimentComponentsRoutes);

router.get('/:experimentId', Experiment.getById);

router.get('/', Experiment.getAllByProjectId);

router.patch('/:experimentId', Experiment.update);

router.post('/', Experiment.create);

export default router;
