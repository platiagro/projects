import { Router } from 'express';
import controller from './controller';

const router = Router();

router.get('/', controller.getAll);

router.post('/', controller.create);

export default router;
