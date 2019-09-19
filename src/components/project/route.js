import { Router } from 'express';
import Project from './controller';

const router = Router();

router.get('/:projectId', Project.getById);

router.get('/', Project.getAll);

router.patch('/', Project.update);

router.post('/', Project.create);

export default router;
