import sinon from 'sinon';

import { Knex } from '../../../config';
import { ExperimentModel as Experiment } from '../../../components/experiments';

describe('Test Experiment Model methods', () => {
  const stubKnexSelect = sinon.stub(Knex, 'select');
  const stubKnexInsert = sinon.stub(Knex, 'insert');

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
              pipelineId: null,
              datasetId: null,
              targetColumnId: null,
              parameters: null,
              createdAt: '2019-09-19T18:01:49.000Z',
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
        where: sinon.stub().resolves([
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
        ]),
      });

      experiemntGetAllVerify();
    });

    it('Rejects db query', () => {
      stubKnexSelect.callsFake(() => {
        return {
          from: sinon.stub().returnsThis(),
          where: sinon.stub().rejects(Error('Forced error')),
        };
      });

      experiemntGetAllVerify();
    });
  });

  describe('Test create Experiment method', () => {
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
});
