import sinon from 'sinon';
import httpMocks from 'node-mocks-http';

import {
  ProjectModel as Model,
  ProjectController as Controller,
} from '../../../components/projects';

describe('Test Project Controller methods', () => {
  const stubProjectGetById = sinon.stub(Model, 'getById');

  describe('Test getById Project controller', () => {
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

  describe('Test Update Project controller', () => {
    const ProjectMocked = new Model(
      '70382be9-be20-4042-a351-31512376957b',
      'ML Example',
      '2019-09-17 13:41:18'
    );

    const stubProjectUpdate = sinon.stub(ProjectMocked, 'update');

    const projectUpdateVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'PATCH',
        url: '/projects',
        params: {
          projectId: '70382be9-be20-4042-a351-31512376957b',
        },
        body: {
          projectName: 'Auto featuring',
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.update(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves create model', () => {
      stubProjectUpdate.resolves(ProjectMocked);

      stubProjectGetById.resolves(ProjectMocked);

      projectUpdateVerify(200);
    });

    it('Resolves create model', () => {
      stubProjectUpdate.rejects(Error('Forced error'));

      stubProjectGetById.resolves(ProjectMocked);

      projectUpdateVerify(500);
    });

    it('Resolves create model', () => {
      stubProjectGetById.rejects(Error('Forced error'));

      projectUpdateVerify(500);
    });

    it('Resolves create model', () => {
      stubProjectGetById.rejects(Error('Invalid UUID.'));

      projectUpdateVerify(400);
    });
  });
});
