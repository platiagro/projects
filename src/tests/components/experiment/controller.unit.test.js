import sinon from 'sinon';
import httpMocks from 'node-mocks-http';

import {
  ExperimentModel as Model,
  ExperimentController as Controller,
} from '../../../components/experiments';

describe('Test Experiment Controller methods', () => {
  const ExperimentMocked = new Model(
    '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
    'Auto featuring experiment',
    'a214d8fc-639f-4088-a9fb-c30ba2a69146',
    '23266cfd-4ed6-43d6-b8a0-ca8440d251c6',
    '0a10c0ac-ff3b-42df-ab7a-dc2962a1750c',
    '3191a035-97a6-4e29-90d4-034cb1f87237',
    '{ price: 2, auto-featuring: true }',
    '2019-09-19T18:01:49.000Z'
  );

  const stubExperimentGetById = sinon.stub(Model, 'getById');
  const stubExperimentGetAll = sinon.stub(Model, 'getAllByProjectId');
  const stubExperimentCreate = sinon.stub(Model, 'create');
  const stubExperimentUpdate = sinon.stub(ExperimentMocked, 'update');
  const stubExperimentReorder = sinon.stub(ExperimentMocked, 'reorder');
  stubExperimentReorder.returns(true);

  describe('Test getById Experiment controller', () => {
    const experimentGetByIdVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'GET',
        url: '/projects/:projectId/experiments/:experimentId',
        params: {
          projectId: '70382be9-be20-4042-a351-31512376957b',
          experimentId: '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.getById(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves getById model', () => {
      stubExperimentGetById.resolves({
        uuid: '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
        name: 'AutoFeat Experiment',
        projectId: '70382be9-be20-4042-a351-31512376957b',
        pipelineId: null,
        datasetId: null,
        targetColumnId: null,
        parameters: null,
        createdAt: '2019-09-19T18:01:49.000Z',
      });

      experimentGetByIdVerify(200);
    });

    it('Rejects getById model, invalid uuid', () => {
      stubExperimentGetById.rejects(Error('Invalid UUID.'));

      experimentGetByIdVerify(400);
    });

    it('Rejects getById model, forced internal server error', () => {
      stubExperimentGetById.rejects(Error('Forced error'));

      experimentGetByIdVerify(500);
    });
  });

  describe('Test getAll Experiments controller', () => {
    const experimentGetAllVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'GET',
        url: '/projects/:projectId/experiments',
        params: {
          projectId: '70382be9-be20-4042-a351-31512376957b',
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.getAllByProjectId(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves getAll model', () => {
      stubExperimentGetAll.resolves([
        {
          uuid: '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
          name: 'AutoFeat Experiment',
          projectId: '70382be9-be20-4042-a351-31512376957b',
          pipelineId: null,
          datasetId: null,
          targetColumnId: null,
          parameters: null,
          createdAt: '2019-09-19T18:01:49.000Z',
        },
      ]);

      experimentGetAllVerify(200);
    });

    it('Rejects getAll model', () => {
      stubExperimentGetAll.rejects(Error('Forced error'));

      experimentGetAllVerify(500);
    });
  });

  describe('Test Create Experiment controller', () => {
    const experimentCreateVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'POST',
        url: '/projects/:projectId/experiments',
        params: {
          projectId: '70382be9-be20-4042-a351-31512376957b',
        },
        body: {
          name: 'Auto featuring experiment',
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.create(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves create model', () => {
      stubExperimentCreate.resolves({
        uuid: '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
        name: 'AutoFeat Experiment',
        projectId: '70382be9-be20-4042-a351-31512376957b',
        createdAt: '2019-09-19 18:01:49',
      });

      experimentCreateVerify(200);
    });

    it('Rejects create model', () => {
      stubExperimentCreate.rejects(Error('Forced error'));

      experimentCreateVerify(500);
    });
  });

  describe('Test Update Project controller', () => {
    const projectUpdateVerify = async (expectedCode, position) => {
      const req = httpMocks.createRequest({
        method: 'PATCH',
        url: '/projects/:projectId/experiments/:experimentId',
        params: {
          experimentId: '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
        },
        body: {
          name: 'Auto-featuring Experiment',
          pipelineId: '23266cfd-4ed6-43d6-b8a0-ca8440d251c6',
          datasetId: '0a10c0ac-ff3b-42df-ab7a-dc2962a1750c',
          targetColumnId: '3191a035-97a6-4e29-90d4-034cb1f87237',
          parameters: '{ price: 2, auto-featuring: true }',
          position,
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.update(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves update model, passing new position', () => {
      stubExperimentUpdate.resolves(ExperimentMocked);

      stubExperimentGetById.resolves(ExperimentMocked);

      projectUpdateVerify(200, 0);
    });

    it('Resolves update model', () => {
      stubExperimentUpdate.resolves(ExperimentMocked);

      stubExperimentGetById.resolves(ExperimentMocked);

      projectUpdateVerify(200, null);
    });

    it('Rejects update model', () => {
      stubExperimentUpdate.rejects(Error('Forced error'));

      stubExperimentGetById.resolves(ExperimentMocked);

      projectUpdateVerify(500);
    });

    it('Rejects getById model, forced internal server error', () => {
      stubExperimentGetById.rejects(Error('Forced error'));

      projectUpdateVerify(500);
    });

    it('Rejects getById model, invalid uuid', () => {
      stubExperimentGetById.rejects(Error('Invalid UUID.'));

      projectUpdateVerify(400);
    });
  });
});
