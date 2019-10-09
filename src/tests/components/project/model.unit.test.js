import sinon from 'sinon';
import { Knex } from '../../../config';

import { ProjectModel as Project } from '../../../components/projects';
import { ExperimentModel as Experiment } from '../../../components/experiments';

describe('Test Project Model methods', () => {
  const stubKnex = sinon.stub(Knex, 'select');
  const stubExperiments = sinon.stub(Experiment, 'getAllByProjectId');
  const mockedExperimentsList = [
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
  ];
  stubExperiments.resolves(mockedExperimentsList);

  describe('Test getById Project method', () => {
    const projectGetByIdVerify = (expectedError) => {
      Project.getById('70382be9-be20-4042-a351-31512376957b')
        .then((result) => {
          expect(result).not.toBeNull();
          expect(result).toEqual({
            uuid: '70382be9-be20-4042-a351-31512376957b',
            name: 'ML Example',
            createdAt: '2019-09-17 13:41:18',
            experimentsList: mockedExperimentsList,
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
          uuid: '70382be9-be20-4042-a351-31512376957b',
          name: 'ML Example',
          createdAt: '2019-09-17 13:41:18',
        }),
      });

      projectGetByIdVerify(null);
    });

    it('Resolves db query for invalid uuid', () => {
      stubKnex.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().returnsThis(),
        first: sinon.stub().resolves(undefined),
      });

      projectGetByIdVerify('Invalid UUID.');
    });

    it('Rejects db query', () => {
      stubKnex.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().returnsThis(),
        first: sinon.stub().rejects(Error('Forced error.')),
      });

      projectGetByIdVerify('Forced error.');
    });
  });

  describe('Test getAll Projects method', () => {
    const projectGetAllVerify = () => {
      Project.getAll()
        .then((result) => {
          expect(result).not.toBeNull();
          expect(result).toEqual([
            {
              uuid: '70382be9-be20-4042-a351-31512376957b',
              name: 'ML Example',
              createdAt: '2019-09-17 13:41:18',
              experimentsList: mockedExperimentsList,
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
            uuid: '70382be9-be20-4042-a351-31512376957b',
            name: 'ML Example',
            createdAt: '2019-09-17 13:41:18',
            experimentsList: mockedExperimentsList,
          },
        ]),
      });

      projectGetAllVerify();
    });

    it('Rejects db query', () => {
      stubKnex.returns({
        from: sinon.stub().returnsThis(),
        orderBy: sinon.stub().rejects(Error('Forced error')),
      });

      projectGetAllVerify();
    });
  });

  describe('Test Create Project method', () => {
    const stubKnexInsert = sinon.stub(Knex, 'insert');

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
      stubKnexInsert.callsFake(() => {
        return {
          into: sinon.stub().resolves([0]),
        };
      });

      projectCreateVerify();
    });

    it('Rejects db query', () => {
      stubKnexInsert.callsFake(() => {
        return {
          into: sinon.stub().rejects(Error('Forced error')),
        };
      });

      projectCreateVerify();
    });
  });

  describe('Test Update Project method', () => {
    const stubKnexUpdate = sinon.stub(Knex, 'update');

    const projectUpdateVerify = () => {
      const projectMocked = new Project(
        '70382be9-be20-4042-a351-31512376957b',
        'ML Example',
        '2019-09-17 13:41:18'
      );

      projectMocked
        .update('Auto featuring example')
        .then((result) => {
          expect(result.name).toBe('Auto featuring example');
          projectMocked.update().then((result_) => {
            expect(result_.name).toBe('Auto featuring example');
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

      projectUpdateVerify();
    });

    it('Rejects db query', () => {
      stubKnexUpdate.returns({
        from: sinon.stub().returnsThis(),
        where: sinon.stub().rejects(Error('Forced error')),
      });

      projectUpdateVerify();
    });
  });
});
