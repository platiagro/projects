import sinon from 'sinon';

import { Knex } from '../../../config';
import { ComponentModel as Component } from '../../../components/experiments';
import Components from '../../../components/experiments/components_model';

describe('Test Components Model Methods', () => {
    const mockedCompentObject = new Component (
        '5aac8764-e77a-47cb-806b-2d6de6e4d521',
        '2019-09-19T18:01:49.000Z',
        '35eaa371-bfda-4a39-8817-a66684214d05',
        'ed89952d-eb18-47c8-9cac-6d0d7181f195',
        0
    );

    const stubKnexSelect = sinon.stub(Knex, 'select');

    describe('Test getComponents Method', () => {
        const getComponentsVerify = (expectedError) => {
            Components.getComponents('35eaa371-bfda-4a39-8817-a66684214d05')
            .then((result) => {
                expect(result).not.tobeNull();
                expect(result).toEqual({
                    uuid: '5aac8764-e77a-47cb-806b-2d6de6e4d521',
                    position: 0,
                });
            })
            .catch((err) => {
                expect(err).toStrictEqual(Error(expectedError));
            });
        }

        it('Test getComponents', () => {
            stubKnexSelect.returns({
                where: sinon.stub().returnsThis(),
                first: sinon.stub().resolves({
                    uuid: '5aac8764-e77a-47cb-806b-2d6de6e4d521',
                    position: 0,
                }),
            });
            getComponentsVerify(null);
        });
    });
});