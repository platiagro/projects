import sinon from 'sinon';
import httpMocks from 'node-mocks-http';

import {
  ExperimentModel as Model,
  ExperimentController as Controller,
} from '../../../components/experiment';

describe('Test Experiment Controller methods', () => {
  const stubExperimentCreate = sinon.stub(Model, 'create');

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
