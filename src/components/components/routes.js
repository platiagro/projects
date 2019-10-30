import { Router } from 'express';
import { MinioController } from '../minio';
import Component from './controller';

const router = Router();

// Verifies if bucket already exists, otherwise create it
router.use(MinioController.verifyBucket);

router.post('/', Component.create);

router.patch('/:uuid', Component.update);

router.delete('/:uuid', Component.deleteById);

router.get('/', Component.getAll);

router.get('/:uuid', Component.getById);

router.post('/upload/:uuid', Component.upload);

router.get('/download/:uuid', Component.download);

router.get('/getFiles/:uuid', MinioController.getFiles);

export default router;
