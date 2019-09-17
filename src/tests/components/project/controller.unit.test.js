import sinon from 'sinon';
import httpMocks from 'node-mocks-http';

import {
  ProjectModel as Model,
  ProjectController as Controller,
} from '../../../components/project';

describe('Test Project Controller methods', () => {
  describe('Test Create Project controller', () => {
    const stubProjectCreate = sinon.stub(Model, 'create');

    const projectCreateVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'POST',
        url: '/projects',
        body: {
          projectName: 'ML Example',
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.create(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves create model', () => {
      stubProjectCreate.resolves({
        uuid: '70382be9-be20-4042-a351-31512376957b',
        name: 'ML Example',
        createdAt: '2019-09-17 13:41:18',
      });

      projectCreateVerify(200);
    });

    it('Rejects create model', () => {
      stubProjectCreate.rejects(Error('Force error'));

      projectCreateVerify(500);
    });
  });
});
