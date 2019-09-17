import { Router } from 'express';
import Controller from './controller';

const router = Router();

router.post('/', Controller.createProject);

export default router;
