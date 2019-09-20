import sinon from 'sinon';
import httpMocks from 'node-mocks-http';

import {
  ExperimentModel as Model,
  ExperimentController as Controller,
} from '../../../components/experiments';

describe('Test Experiment Controller methods', () => {
  const stubExperimentGetAll = sinon.stub(Model, 'getAllByProjectId');
  const stubExperimentCreate = sinon.stub(Model, 'create');

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
          experimentName: 'Auto featuring experiment',
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
});
