import sinon from 'sinon';

import { Knex } from '../../../config';
import { ExperimentModel as Experiment } from '../../../components/experiment';

describe('Test Experiment Model methods', () => {
  const stubKnexInsert = sinon.stub(Knex, 'insert');

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
