import sinon from 'sinon';
import { Knex } from '../../../config';

import { ProjectModel as Project } from '../../../components/project';

describe('Test Project Model methods', () => {
  describe('Test Create Project method', () => {
    const stubKnex = sinon.stub(Knex, 'insert');

    const projectCreateVerify = () => {
      Project.create(
        '70382be9-be20-4042-a351-31512376957b',
        'ML Example',
        '2019-09-17 13:41:18'
      )
        .then((result) => {
          expect(result).not.toBeNull();
          expect(result).toEqual({
            uuid: '70382be9-be20-4042-a351-31512376957b',
            name: 'ML Example',
            createdAt: '2019-09-17 13:41:18',
          });
        })
        .catch((err) => {
          expect(err).toStrictEqual(Error('Forced error'));
        });
    };

    it('Resolves db query', () => {
      stubKnex.callsFake(() => {
        return {
          into: sinon.stub().resolves([0]),
        };
      });

      projectCreateVerify();
    });

    it('Rejects db query', () => {
      stubKnex.callsFake(() => {
        return {
          into: sinon.stub().rejects(Error('Forced error')),
        };
      });

      projectCreateVerify();
    });
  });
});
