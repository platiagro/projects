import sinon from 'sinon';
import { Knex } from '../../../config';

import { ComponentsModel } from '../../../components/components';
import { MinioModel } from '../../../components/minio';

describe('Test Components Model methods', () => {
  const stubKnex = sinon.stub(Knex, 'select');
  const stubMinio = sinon.stub(MinioModel, 'getFiles');
  const mockedFileList = [
    {
      name: 'components/9014c0e6-534b-4e7d-a8db-cd5c9d8ee540/Falha_Treino.csv',
      lastModified: '2019-11-05T11:50:45.815Z',
      etag: '2656720349be07d93bcd1d8b6622b51e-1',
      size: 541407,
    },
  ];
  stubMinio.resolves(mockedFileList);

  describe('Test Create method', () => {
    const stubKnexInsert = sinon.stub(Knex, 'insert');

    const createVerify = () => {
      ComponentsModel.create(
        '9014c0e6-534b-4e7d-a8db-cd5c9d8ee540',
        '2019-11-04T17:16:53.000Z',
        'Component Test'
      )
        .then((result) => {
          expect(result).not.toBeNull();
          expect(result).toEqual({
            createdAt: '2019-11-04T17:16:53.000Z',
            file: undefined,
            name: 'Component Test',
            parameters: undefined,
            updatedAt: undefined,
            uuid: '9014c0e6-534b-4e7d-a8db-cd5c9d8ee540',
          });
        })
        .catch((err) => {
          expect(err).toStrictEqual(Error('Forced error'));
        });
    };

    it('Resolves db query', () => {
      stubKnexInsert.callsFake(() => {
        return {
          into: sinon.stub().resolves([0]),
        };
      });

      createVerify();
    });

    it('Rejects db query', () => {
      stubKnexInsert.callsFake(() => {
        return {
          into: sinon.stub().rejects(Error('Forced error')),
        };
      });

      createVerify();
    });
  });

  describe('Test Update method', () => {
    const stubKnexUpdate = sinon.stub(Knex, 'update');

    const updateVerify = () => {
      const componentMocked = new ComponentsModel(
        '9014c0e6-534b-4e7d-a8db-cd5c9d8ee540',
        '2019-11-04T17:16:53.000Z',
        'Component Test'
      );

      componentMocked
        .update('2019-11-05T17:16:53.000Z', 'Component Test Update', null)
        .then((result) => {
          expect(result.name).toBe('Component Test Update');
          componentMocked.update().then((result_) => {
            expect(result_.name).toBe('Component Test Update');
          });
        })
        .catch((err) => {
          expect(err).toStrictEqual(Error('Forced error'));
        });
    };

    it('Resolves db query', () => {
      stubKnexUpdate.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().resolves(),
      });

      updateVerify();
    });

    it('Rejects db query', () => {
      stubKnexUpdate.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().rejects(Error('Forced error')),
      });

      updateVerify();
    });
  });

  describe('Test getById method', () => {
    const getByIdVerify = (expectedError) => {
      ComponentsModel.getById('9014c0e6-534b-4e7d-a8db-cd5c9d8ee540')
        .then((result) => {
          expect(result).not.toBeNull();
          expect(result).toEqual({
            uuid: '9014c0e6-534b-4e7d-a8db-cd5c9d8ee540',
            createdAt: '2019-11-04T17:16:53.000Z',
            parameters: undefined,
            updatedAt: undefined,
            name: 'Component Test',
            file:
              'components/9014c0e6-534b-4e7d-a8db-cd5c9d8ee540/Falha_Treino.csv',
          });
        })
        .catch((err) => {
          expect(err).toStrictEqual(Error(expectedError));
        });
    };

    it('Resolves db query', () => {
      stubKnex.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().returnsThis(),
        first: sinon.stub().resolves({
          uuid: '9014c0e6-534b-4e7d-a8db-cd5c9d8ee540',
          createdAt: '2019-11-04T17:16:53.000Z',
          name: 'Component Test',
        }),
      });

      getByIdVerify(null);
    });

    it('Resolves db query for invalid uuid', () => {
      stubKnex.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().returnsThis(),
        first: sinon.stub().resolves(undefined),
      });

      getByIdVerify('Invalid UUID.');
    });

    it('Rejects db query', () => {
      stubKnex.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().returnsThis(),
        first: sinon.stub().rejects(Error('Forced error.')),
      });

      getByIdVerify('Forced error.');
    });
  });

  describe('Test getAll method', () => {
    const getAllVerify = () => {
      ComponentsModel.getAll()
        .then((result) => {
          expect(result).not.toBeNull();
          expect(result).toEqual([
            {
              uuid: '9014c0e6-534b-4e7d-a8db-cd5c9d8ee540',
              createdAt: '2019-11-04T17:16:53.000Z',
              parameters: undefined,
              updatedAt: undefined,
              name: 'Component Test',
              file:
                'components/9014c0e6-534b-4e7d-a8db-cd5c9d8ee540/Falha_Treino.csv',
            },
          ]);
        })
        .catch((err) => {
          expect(err).toStrictEqual(Error('Forced error'));
        });
    };

    it('Resolves db query', () => {
      stubKnex.returns({
        from: sinon.stub().returnsThis(),
        orderBy: sinon.stub().resolves([
          {
            uuid: '9014c0e6-534b-4e7d-a8db-cd5c9d8ee540',
            createdAt: '2019-11-04T17:16:53.000Z',
            parameters: undefined,
            updatedAt: undefined,
            name: 'Component Test',
            file:
              'components/9014c0e6-534b-4e7d-a8db-cd5c9d8ee540/Falha_Treino.csv',
          },
        ]),
      });

      getAllVerify();
    });

    it('Rejects db query', () => {
      stubKnex.returns({
        from: sinon.stub().returnsThis(),
        orderBy: sinon.stub().rejects(Error('Forced error')),
      });

      getAllVerify();
    });
  });
});
