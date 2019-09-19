import { Router } from 'express';
import controller from './controller';

const router = Router({ mergeParams: true });

router.post('/', controller.create);

export default router;
