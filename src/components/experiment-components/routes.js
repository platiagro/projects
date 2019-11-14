import { Router } from 'express';
import ExperimentComponents from './controller';

const router = Router({ mergeParams: true });

router.get('/:uuid', ExperimentComponents.getById);

router.get('/', ExperimentComponents.getAll);

router.post('/', ExperimentComponents.create);

router.patch('/:uuid', ExperimentComponents.update);

router.delete('/:uuid', ExperimentComponents.deleteComponent);

export default router;
