import sinon from 'sinon';
import httpMocks from 'node-mocks-http';

import {
  ProjectModel as Model,
  ProjectController as Controller,
} from '../../../components/project';

describe('Test Project Controller methods', () => {
  describe('Test getById Project controller', () => {
    const stubProjectGetById = sinon.stub(Model, 'getById');

    const projectGetByIdVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'GET',
        url: '/projects',
        params: {
          projectId: '70382be9-be20-4042-a351-31512376957b',
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.getById(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves getById model', () => {
      stubProjectGetById.resolves({
        uuid: '70382be9-be20-4042-a351-31512376957b',
        name: 'ML Example',
        createdAt: '2019-09-17 13:41:18',
      });

      projectGetByIdVerify(200);
    });

    it('Rejects getById model, invalid uuid', () => {
      stubProjectGetById.rejects(Error('Invalid UUID.'));

      projectGetByIdVerify(400);
    });

    it('Rejects getById model, forced internal server error', () => {
      stubProjectGetById.rejects(Error('Forced error'));

      projectGetByIdVerify(500);
    });
  });

  describe('Test getAll Projects controller', () => {
    const stubProjectGetAll = sinon.stub(Model, 'getAll');

    const projectGetAllVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'GET',
        url: '/projects',
      });
      const res = httpMocks.createResponse();

      const result = await Controller.getAll(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves getAll model', () => {
      stubProjectGetAll.resolves([
        {
          uuid: '70382be9-be20-4042-a351-31512376957b',
          name: 'ML Example',
          createdAt: '2019-09-17 13:41:18',
        },
      ]);

      projectGetAllVerify(200);
    });

    it('Rejects getAll model', () => {
      stubProjectGetAll.rejects(Error('Forced error'));

      projectGetAllVerify(500);
    });
  });

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
      stubProjectCreate.rejects(Error('Forced error'));

      projectCreateVerify(500);
    });
  });
});
