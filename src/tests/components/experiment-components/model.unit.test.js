import sinon from 'sinon';

import { Knex } from '../../../config';
import { ExperimentComponentsModel as ExperimentComponents } from '../../../components/experiment-components';

describe('Test ExperimentComponents Model methods', () => {
  const experimentComponentMocked = new ExperimentComponents(
    'c96a617a-487f-4f6c-9fc4-528a9089e276',
    '2019-11-14T13:17:31.000Z',
    '322c538e-b99b-4929-bc32-41de3661cef8',
    'cf04a1b4-6f7f-4dd9-b246-e8cfd3fd3f81',
    0
  );

  const stubKnexSelect = sinon.stub(Knex, 'select');
  const stubKnexInsert = sinon.stub(Knex, 'insert');
  const stubKnexUpdate = sinon.stub(Knex, 'update');
  const stubKnexDelete = sinon.stub(Knex, 'delete');

  describe('Test getById ExperimentComponent method', () => {
    const experimentComponentsGetByIdVerify = (expectedError) => {
      ExperimentComponents.getById('c96a617a-487f-4f6c-9fc4-528a9089e276')
        .then((result) => {
          expect(result).not.toBeNull();
          expect(result).toEqual({
            uuid: 'c96a617a-487f-4f6c-9fc4-528a9089e276',
            createdAt: '2019-11-14T13:17:31.000Z',
            experimentId: '322c538e-b99b-4929-bc32-41de3661cef8',
            componentId: 'cf04a1b4-6f7f-4dd9-b246-e8cfd3fd3f81',
            position: 0,
          });
        })
        .catch((err) => {
          expect(err).toStrictEqual(Error(expectedError));
        });
    };

    it('Resolves db query', () => {
      stubKnexSelect.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().returnsThis(),
        first: sinon.stub().resolves({
          uuid: 'c96a617a-487f-4f6c-9fc4-528a9089e276',
          createdAt: '2019-11-14T13:17:31.000Z',
          experimentId: '322c538e-b99b-4929-bc32-41de3661cef8',
          componentId: 'cf04a1b4-6f7f-4dd9-b246-e8cfd3fd3f81',
          position: 0,
        }),
      });

      experimentComponentsGetByIdVerify(null);
    });

    it('Resolves db query for invalid uuid', () => {
      stubKnexSelect.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().returnsThis(),
        first: sinon.stub().resolves(undefined),
      });

      experimentComponentsGetByIdVerify('Invalid UUID.');
    });

    it('Rejects db query', () => {
      stubKnexSelect.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().returnsThis(),
        first: sinon.stub().rejects(Error('Forced error.')),
      });

      experimentComponentsGetByIdVerify('Forced error.');
    });
  });

  describe('Test getAll ExperimentComponents method', () => {
    const experimentComponentsGetAllVerify = () => {
      ExperimentComponents.getAll()
        .then((result) => {
          expect(result).not.toBeNull();
          expect(result).toEqual([
            {
              uuid: 'c96a617a-487f-4f6c-9fc4-528a9089e276',
              createdAt: '2019-11-14T13:17:31.000Z',
              experimentId: '322c538e-b99b-4929-bc32-41de3661cef8',
              componentId: 'cf04a1b4-6f7f-4dd9-b246-e8cfd3fd3f81',
              position: 0,
            },
          ]);
        })
        .catch((err) => {
          expect(err).toStrictEqual(Error('Forced error'));
        });
    };

    it('Resolves db query', () => {
      stubKnexSelect.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().returnsThis(),
        orderBy: sinon.stub().resolves([
          {
            uuid: 'c96a617a-487f-4f6c-9fc4-528a9089e276',
            createdAt: '2019-11-14T13:17:31.000Z',
            experimentId: '322c538e-b99b-4929-bc32-41de3661cef8',
            componentId: 'cf04a1b4-6f7f-4dd9-b246-e8cfd3fd3f81',
            position: 0,
          },
        ]),
      });

      experimentComponentsGetAllVerify();
    });

    it('Rejects db query', () => {
      stubKnexSelect.callsFake(() => {
        return {
          from: sinon.stub().returnsThis(),
          where: sinon.stub().returnsThis(),
          orderBy: sinon.stub().rejects(Error('Forced error')),
        };
      });

      experimentComponentsGetAllVerify();
    });
  });

  describe('Test create ExperimentComponents method', () => {
    const experimentComponentsCreateVerify = () => {
      ExperimentComponents.create(
        'c96a617a-487f-4f6c-9fc4-528a9089e276',
        '322c538e-b99b-4929-bc32-41de3661cef8',
        'cf04a1b4-6f7f-4dd9-b246-e8cfd3fd3f81',
        '2019-11-14T13:17:31.000Z',
        0
      )
        .then((result) => {
          expect(result).not.toBeNull();
          expect(result).toEqual({
            uuid: 'c96a617a-487f-4f6c-9fc4-528a9089e276',
            createdAt: '2019-11-14T13:17:31.000Z',
            experimentId: '322c538e-b99b-4929-bc32-41de3661cef8',
            componentId: 'cf04a1b4-6f7f-4dd9-b246-e8cfd3fd3f81',
            position: 0,
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

      experimentComponentsCreateVerify();
    });

    it('Rejects db query', () => {
      stubKnexInsert.callsFake(() => {
        return {
          into: sinon.stub().rejects(Error('Forced error')),
        };
      });

      experimentComponentsCreateVerify();
    });
  });

  describe('Test update ExperimentComponents method', () => {
    const experimentComponentsUpdateVerify = () => {
      experimentComponentMocked
        .update(
          '67a9ac84-f444-4400-8c2b-c50d7d503b12',
          'fe5205f5-7f76-4f57-84ca-ea6dd62670e8',
          1
        )
        .then((result) => {
          expect(result.experimentId).toBe(
            '67a9ac84-f444-4400-8c2b-c50d7d503b12'
          );
          expect(result.componentId).toBe(
            'fe5205f5-7f76-4f57-84ca-ea6dd62670e8'
          );
          expect(result.position).toBe(1);

          experimentComponentMocked.update().then((result_) => {
            expect(result_.experimentId).toBe(
              '67a9ac84-f444-4400-8c2b-c50d7d503b12'
            );
            expect(result_.componentId).toBe(
              'fe5205f5-7f76-4f57-84ca-ea6dd62670e8'
            );
            expect(result_.position).toBe(1);
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

      experimentComponentsUpdateVerify();
    });

    it('Rejects db query', () => {
      stubKnexUpdate.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().rejects(Error('Forced error')),
      });

      experimentComponentsUpdateVerify();
    });
  });

  describe('Test delete ExperimentComponent method', () => {
    const experimentComponentsDeleteVerify = (expectedError) => {
      experimentComponentMocked
        .delete()
        .then((result) => {
          expect(result).toBeTruthy();
        })
        .catch((err) => {
          expect(err).toStrictEqual(Error(expectedError));
        });
    };

    it('Resolves db query', () => {
      stubKnexDelete.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().resolves(true),
      });

      experimentComponentsDeleteVerify();
    });

    it('Rejects db query', () => {
      stubKnexDelete.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().rejects(Error('Forced error.')),
      });

      experimentComponentsDeleteVerify('Forced error.');
    });
  });
});
