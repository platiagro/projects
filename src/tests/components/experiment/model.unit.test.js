import sinon from 'sinon';

import { Knex } from '../../../config';
import { ExperimentModel as Experiment } from '../../../components/experiments';

describe('Test Experiment Model methods', () => {
  const experimentMocked = new Experiment(
    '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
    'Auto featuring experiment',
    'a214d8fc-639f-4088-a9fb-c30ba2a69146',
    '23266cfd-4ed6-43d6-b8a0-ca8440d251c6',
    '1042cbad-e021-4777-ac25-7b096d6023aa',
    '0a10c0ac-ff3b-42df-ab7a-dc2962a1750c',
    '482b603f-23c1-4a10-9b79-8c5b91c6c0cb',
    '3191a035-97a6-4e29-90d4-034cb1f87237',
    '{ price: 2, auto-featuring: true }',
    '2019-09-19T18:01:49.000Z',
    0
  );

  const stubKnexSelect = sinon.stub(Knex, 'select');
  const stubKnexInsert = sinon.stub(Knex, 'insert');
  const stubKnexUpdate = sinon.stub(Knex, 'update');
  const stubExperimentReorder = sinon.stub(experimentMocked, 'reorder');

  describe('Test getById Experiment method', () => {
    const experimentGetByIdVerify = (expectedError) => {
      Experiment.getById('33f56c0f-12f9-4cf0-889f-29b3b424fd4e')
        .then((result) => {
          expect(result).not.toBeNull();
          expect(result).toEqual({
            uuid: '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
            name: 'AutoFeat Experiment',
            projectId: '70382be9-be20-4042-a351-31512376957b',
            pipelineIdTrain: null,
            pipelineIdDeploy: null,
            datasetId: null,
            headerId: null,
            targetColumnId: null,
            parameters: null,
            createdAt: '2019-09-19T18:01:49.000Z',
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
          uuid: '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
          name: 'AutoFeat Experiment',
          projectId: '70382be9-be20-4042-a351-31512376957b',
          pipelineIdTrain: null,
          pipelineIdDeploy: null,
          datasetId: null,
          headerId: null,
          targetColumnId: null,
          parameters: null,
          createdAt: '2019-09-19T18:01:49.000Z',
          position: 0,
        }),
      });

      experimentGetByIdVerify(null);
    });

    it('Resolves db query for invalid uuid', () => {
      stubKnexSelect.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().returnsThis(),
        first: sinon.stub().resolves(undefined),
      });

      experimentGetByIdVerify('Invalid UUID.');
    });

    it('Rejects db query', () => {
      stubKnexSelect.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().returnsThis(),
        first: sinon.stub().rejects(Error('Forced error.')),
      });

      experimentGetByIdVerify('Forced error.');
    });
  });

  describe('Test getAll Experiments method', () => {
    const experiemntGetAllVerify = () => {
      Experiment.getAllByProjectId()
        .then((result) => {
          expect(result).not.toBeNull();
          expect(result).toEqual([
            {
              uuid: '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
              name: 'AutoFeat Experiment',
              projectId: '70382be9-be20-4042-a351-31512376957b',
              pipelineIdTrain: null,
              pipelineIdDeploy: null,
              datasetId: null,
              headerId: null,
              targetColumnId: null,
              parameters: null,
              createdAt: '2019-09-19T18:01:49.000Z',
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
        whereNotNull: sinon.stub().returnsThis(),
        andWhere: sinon.stub().returnsThis(),
        orderBy: sinon.stub().resolves([
          {
            uuid: '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
            name: 'AutoFeat Experiment',
            projectId: '70382be9-be20-4042-a351-31512376957b',
            pipelineIdTrain: null,
            pipelineIdDeploy: null,
            datasetId: null,
            headerId: null,
            targetColumnId: null,
            parameters: null,
            createdAt: '2019-09-19T18:01:49.000Z',
            position: 0,
          },
        ]),
      });

      experiemntGetAllVerify();
    });

    it('Rejects db query', () => {
      stubKnexSelect.callsFake(() => {
        return {
          from: sinon.stub().returnsThis(),
          whereNotNull: sinon.stub().returnsThis(),
          andWhere: sinon.stub().returnsThis(),
          orderBy: sinon.stub().rejects(Error('Forced error')),
        };
      });

      experiemntGetAllVerify();
    });
  });

  describe('Test create Experiment method', () => {
    stubExperimentReorder.resolves();

    const experimentCreateVerify = () => {
      Experiment.create(
        '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
        'AutoFeat Experiment',
        '70382be9-be20-4042-a351-31512376957b',
        '2019-09-19 18:01:49'
      )
        .then((result) => {
          expect(result).not.toBeNull();
          expect(result).toEqual({
            uuid: '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
            name: 'AutoFeat Experiment',
            projectId: '70382be9-be20-4042-a351-31512376957b',
            createdAt: '2019-09-19 18:01:49',
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

      experimentCreateVerify();
    });

    it('Rejects db query', () => {
      stubKnexInsert.callsFake(() => {
        return {
          into: sinon.stub().rejects(Error('Forced error')),
        };
      });

      experimentCreateVerify();
    });
  });

  describe('Test update Experiment method', () => {
    stubExperimentReorder.resolves();

    const experimentUpdateVerify = () => {
      experimentMocked
        .update(
          'Auto-featuring Example',
          '67a9ac84-f444-4400-8c2b-c50d7d503b12',
          'fe5205f5-7f76-4f57-84ca-ea6dd62670e8',
          'baaabb83-3ce1-44b3-b2e6-e33182e7cd4b',
          '482b603f-23c1-4a10-9b79-8c5b91c6c0cb',
          'fda0cfd0-d708-4fd5-84a0-70a7530b4a69',
          '{ price: 6, auto-featuring: true }',
          1
        )
        .then((result) => {
          expect(result.name).toBe('Auto-featuring Example');
          expect(result.pipelineIdTrain).toBe(
            '67a9ac84-f444-4400-8c2b-c50d7d503b12'
          );
          expect(result.pipelineIdDeploy).toBe(
            'fe5205f5-7f76-4f57-84ca-ea6dd62670e8'
          );
          expect(result.datasetId).toBe('baaabb83-3ce1-44b3-b2e6-e33182e7cd4b');
          expect(result.headerId).toBe('482b603f-23c1-4a10-9b79-8c5b91c6c0cb');

          expect(result.targetColumnId).toBe(
            'fda0cfd0-d708-4fd5-84a0-70a7530b4a69'
          );
          expect(result.parameters).toBe('{ price: 6, auto-featuring: true }');
          expect(result.position).toBe(1);

          experimentMocked.update().then((result_) => {
            expect(result_.name).toBe('Auto-featuring Example');
            expect(result_.pipelineIdTrain).toBe(
              '67a9ac84-f444-4400-8c2b-c50d7d503b12'
            );
            expect(result_.pipelineIdDeploy).toBe(
              'fe5205f5-7f76-4f57-84ca-ea6dd62670e8'
            );
            expect(result_.datasetId).toBe(
              'baaabb83-3ce1-44b3-b2e6-e33182e7cd4b'
            );
            expect(result_.headerId).toBe(
              '482b603f-23c1-4a10-9b79-8c5b91c6c0cb'
            );
            expect(result_.targetColumnId).toBe(
              'fda0cfd0-d708-4fd5-84a0-70a7530b4a69'
            );
            expect(result_.parameters).toBe(
              '{ price: 6, auto-featuring: true }'
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

      experimentUpdateVerify();
    });

    it('Rejects db query', () => {
      stubKnexUpdate.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().rejects(Error('Forced error')),
      });

      experimentUpdateVerify();
    });
  });
});

describe('Test reorder Experiment method', () => {
  const experimentMocked = new Experiment(
    '33f56c0f-12f9-4cf0-889f-29b3b424fd4e',
    'Auto featuring experiment',
    'a214d8fc-639f-4088-a9fb-c30ba2a69146',
    '23266cfd-4ed6-43d6-b8a0-ca8440d251c6',
    '1042cbad-e021-4777-ac25-7b096d6023aa',
    '0a10c0ac-ff3b-42df-ab7a-dc2962a1750c',
    '482b603f-23c1-4a10-9b79-8c5b91c6c0cb',
    '3191a035-97a6-4e29-90d4-034cb1f87237',
    '{ price: 2, auto-featuring: true }',
    '2019-09-19T18:01:49.000Z',
    0
  );

  it('', () => {
    const stubExperimentGetAll = sinon.stub(Experiment, 'getAllByProjectId');
    const stubExperimentUpdate = sinon.stub(experimentMocked, 'update');
    stubExperimentGetAll.resolves([experimentMocked]);
    stubExperimentUpdate.resolves(experimentMocked);

    experimentMocked.reorder(0);
  });
});
