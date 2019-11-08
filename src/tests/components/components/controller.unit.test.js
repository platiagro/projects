import sinon from 'sinon';
import httpMocks from 'node-mocks-http';

import {
  ComponentsModel as Model,
  ComponentsController as Controller,
} from '../../../components/components';

import { MinioModel } from '../../../components/minio';

describe('Test Component Controller methods', () => {
  const stubGetById = sinon.stub(Model, 'getById');

  describe('Test create controller', () => {
    const stubCreate = sinon.stub(Model, 'create');

    const createVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'POST',
        url: '/components',
        body: {
          name: 'Component Test',
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.create(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves create model', () => {
      stubCreate.resolves({
        uuid: '9014c0e6-534b-4e7d-a8db-cd5c9d8ee540',
        createdAt: '2019-11-04T17:16:53.000Z',
        name: 'Component Test',
      });

      createVerify(200);
    });

    it('Rejects create model', () => {
      stubCreate.rejects(Error('Forced error'));

      createVerify(500);
    });
  });

  describe('Test Update controller', () => {
    const ComponentMocked = new Model(
      '9014c0e6-534b-4e7d-a8db-cd5c9d8ee540',
      '2019-11-04T17:16:53.000Z',
      'Component Test'
    );

    const stubUpdate = sinon.stub(ComponentMocked, 'update');

    const updateVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'PATCH',
        url: '/components',
        params: {
          uuid: '9014c0e6-534b-4e7d-a8db-cd5c9d8ee540',
        },
        body: {
          name: 'Component Test Update',
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.update(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves create and update model', () => {
      stubUpdate.resolves(ComponentMocked);

      stubGetById.resolves(ComponentMocked);

      updateVerify(200);
    });

    it('Rejects update model, forced internal server error', () => {
      stubUpdate.rejects(Error('Forced error'));

      stubGetById.resolves(ComponentMocked);

      updateVerify(500);
    });

    it('Rejects getById model, invalid uuid', () => {
      stubGetById.rejects(Error('Invalid UUID.'));

      updateVerify(400);
    });

    it('Rejects getById model, forced internal server error', () => {
      stubGetById.rejects(Error('Forced error'));

      updateVerify(500);
    });
  });

  describe('Test deleteById controller', () => {
    const stubMinioDeleteFolder = sinon.stub(MinioModel, 'deleteFolder');
    const stubDeleteById = sinon.stub(Model, 'deleteById');

    const deleteByIdVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'DELETE',
        url: '/components',
        params: {
          uuid: '9014c0e6-534b-4e7d-a8db-cd5c9d8ee540',
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.deleteById(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves Minio delete folder and deleteById model', () => {
      stubMinioDeleteFolder.resolves();

      stubDeleteById.resolves();

      deleteByIdVerify(200);
    });

    it('Rejects deleteById model, invalid uuid', () => {
      stubMinioDeleteFolder.resolves();

      stubDeleteById.rejects(Error('Invalid UUID.'));

      deleteByIdVerify(400);
    });

    it('Rejects deleteById model, forced internal server error', () => {
      stubMinioDeleteFolder.resolves();

      stubDeleteById.rejects(Error('Forced error'));

      deleteByIdVerify(500);
    });
  });

  describe('Test getAll controller', () => {
    const stubGetAll = sinon.stub(Model, 'getAll');

    const getAllVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'GET',
        url: '/components',
      });
      const res = httpMocks.createResponse();

      const result = await Controller.getAll(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves getAll model', () => {
      stubGetAll.resolves([
        {
          uuid: '9014c0e6-534b-4e7d-a8db-cd5c9d8ee540',
          createdAt: '2019-11-04T17:16:53.000Z',
          name: 'Component Test',
        },
      ]);

      getAllVerify(200);
    });

    it('Rejects getAll model, forced internal server error', () => {
      stubGetAll.rejects(Error('Forced error'));

      getAllVerify(500);
    });
  });

  describe('Test getById controller', () => {
    const getByIdVerify = async (expectedCode) => {
      const req = httpMocks.createRequest({
        method: 'GET',
        url: '/components',
        params: {
          uuid: '70382be9-be20-4042-a351-31512376957b',
        },
      });
      const res = httpMocks.createResponse();

      const result = await Controller.getById(req, res);

      expect(result.statusCode).toBe(expectedCode);
    };

    it('Resolves getById model', () => {
      stubGetById.resolves({
        uuid: '9014c0e6-534b-4e7d-a8db-cd5c9d8ee540',
        createdAt: '2019-11-04T17:16:53.000Z',
        name: 'Component Test',
      });

      getByIdVerify(200);
    });

    it('Rejects getById model, invalid uuid', () => {
      stubGetById.rejects(Error('Invalid UUID.'));

      getByIdVerify(400);
    });

    it('Rejects getById model, forced internal server error', () => {
      stubGetById.rejects(Error('Forced error'));

      getByIdVerify(500);
    });
  });
});
