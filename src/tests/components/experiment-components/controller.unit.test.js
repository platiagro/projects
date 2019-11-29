import sinon from 'sinon';
import httpMocks from 'node-mocks-http';

import {
  ExperimentComponentsModel as Model,
  ExperimentComponentsController as Controller,
} from '../../../components/experiment-components';

describe('Test Experiment Controller methods', () => {
  const ExperimentComponentMocked = new Model(
    'c96a617a-487f-4f6c-9fc4-528a9089e276',
    '2019-11-14T13:17:31.000Z',
    '322c538e-b99b-4929-bc32-41de3661cef8',
    'cf04a1b4-6f7f-4dd9-b246-e8cfd3fd3f81',
    0
  );

  const stubGetById = sinon.stub(Model, 'getById');
  const stubGetAll = sinon.stub(Model, 'getAll');
  const stubCreate = sinon.stub(Model, 'create');
  const stubUpdate = sinon.stub(ExperimentComponentMocked, 'update');
  const stubDelete = sinon.stub(ExperimentComponentMocked, 'delete');

  describe('Test getById ExperimentComponents controller', () => {
    const experimentGetByIdVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'GET',
        url:
          '/projects/:projectId/experiments/:experimentId/components/:componentId',
        params: {
          projectId: '70382be9-be20-4042-a351-31512376957b',
          experimentId: '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
          componentId: 'c96a617a-487f-4f6c-9fc4-528a9089e276',
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.getById(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves getById model', () => {
      stubGetById.resolves({
        uuid: 'c96a617a-487f-4f6c-9fc4-528a9089e276',
        createdAt: '2019-11-14T13:17:31.000Z',
        experimentId: '322c538e-b99b-4929-bc32-41de3661cef8',
        componentId: 'cf04a1b4-6f7f-4dd9-b246-e8cfd3fd3f81',
        position: 0,
      });

      experimentGetByIdVerify(200);
    });

    it('Rejects getById model, invalid uuid', () => {
      stubGetById.rejects(Error('Invalid UUID.'));

      experimentGetByIdVerify(400);
    });

    it('Rejects getById model, forced internal server error', () => {
      stubGetById.rejects(Error('Forced error'));

      experimentGetByIdVerify(500);
    });
  });

  describe('Test getAll ExperimentComponents controller', () => {
    const experimentComponentsGetAllVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'GET',
        url: '/projects/:projectId/experiments/:experimentId/components',
        params: {
          projectId: '70382be9-be20-4042-a351-31512376957b',
          experimentId: '322c538e-b99b-4929-bc32-41de3661cef8',
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.getAll(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves getAll model', () => {
      stubGetAll.resolves([
        {
          uuid: 'c96a617a-487f-4f6c-9fc4-528a9089e276',
          createdAt: '2019-11-14T13:17:31.000Z',
          experimentId: '322c538e-b99b-4929-bc32-41de3661cef8',
          componentId: 'cf04a1b4-6f7f-4dd9-b246-e8cfd3fd3f81',
          position: 0,
        },
      ]);

      experimentComponentsGetAllVerify(200);
    });

    it('Rejects getAll model', () => {
      stubGetAll.rejects(Error('Forced error'));

      experimentComponentsGetAllVerify(500);
    });
  });

  describe('Test Create Experiment controller', () => {
    const experimentComponentsCreateVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'POST',
        url: '/projects/:projectId/experiments/:experimentId/components',
        params: {
          projectId: '70382be9-be20-4042-a351-31512376957b',
          experimentId: '322c538e-b99b-4929-bc32-41de3661cef8',
        },
        body: {
          componentId: 'cf04a1b4-6f7f-4dd9-b246-e8cfd3fd3f81',
          position: '0',
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.create(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves create model', () => {
      stubCreate.resolves(ExperimentComponentMocked);

      experimentComponentsCreateVerify(200);
    });

    it('Rejects create model', () => {
      stubCreate.rejects(Error('Forced error'));

      experimentComponentsCreateVerify(500);
    });
  });

  describe('Test Update Project controller', () => {
    const experimentComponentUpdateVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'PATCH',
        url:
          '/projects/:projectId/experiments/:experimentId/components/:componentId',
        params: {
          projectId: '70382be9-be20-4042-a351-31512376957b',
          experimentId: '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
          componentId: 'c96a617a-487f-4f6c-9fc4-528a9089e276',
        },
        body: {
          experimentId: '322c538e-b99b-4929-bc32-41de3661cef8',
          componentId: 'cf04a1b4-6f7f-4dd9-b246-e8cfd3fd3f81',
          position: 0,
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.update(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves update model, passing new position', () => {
      stubUpdate.resolves(ExperimentComponentMocked);

      stubGetById.resolves(ExperimentComponentMocked);

      experimentComponentUpdateVerify(200, 0);
    });

    it('Resolves update model', () => {
      stubUpdate.resolves(ExperimentComponentMocked);

      stubGetById.resolves(ExperimentComponentMocked);

      experimentComponentUpdateVerify(200, null);
    });

    it('Rejects update model', () => {
      stubUpdate.rejects(Error('Forced error'));

      stubGetById.resolves(ExperimentComponentMocked);

      experimentComponentUpdateVerify(500);
    });

    it('Rejects getById model, forced internal server error', () => {
      stubGetById.rejects(Error('Forced error'));

      experimentComponentUpdateVerify(500);
    });

    it('Rejects getById model, invalid uuid', () => {
      stubGetById.rejects(Error('Invalid UUID.'));

      experimentComponentUpdateVerify(400);
    });
  });

  describe('Test Delete ExperimentComponent controller', () => {
    const experimentComponentsDeleteVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'DELETE',
        url:
          '/projects/:projectId/experiments/:experimentId/components/:componentId',
        params: {
          projectId: '70382be9-be20-4042-a351-31512376957b',
          experimentId: '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
          componentId: 'c96a617a-487f-4f6c-9fc4-528a9089e276',
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.deleteComponent(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves delete model', () => {
      stubDelete.resolves(ExperimentComponentMocked);

      stubGetById.resolves(ExperimentComponentMocked);

      experimentComponentsDeleteVerify(200);
    });

    it('Rejects delete model', () => {
      stubDelete.rejects(Error('Forced error'));

      stubGetById.resolves(ExperimentComponentMocked);

      experimentComponentsDeleteVerify(500);
    });

    it('Rejects getById model, forced internal server error', () => {
      stubGetById.rejects(Error('Forced error'));

      experimentComponentsDeleteVerify(500);
    });

    it('Rejects getById model, invalid uuid', () => {
      stubGetById.rejects(Error('Invalid UUID.'));

      experimentComponentsDeleteVerify(400);
    });
  });
});
