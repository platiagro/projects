import { Knex } from '../../config';

class Components {
    constructor(
        uuid,
        createdAt,
        experimentId,
        componentId,
        position
    ){
        this.uuid = uuid;
        this.createdAt = createdAt;
        this.experimentId = experimentId;
        this.componentId = componentId;
        this.position = position;
    }

    static fromDBRecord(record) {
        return new this(
            record.uuid,
            record.createdAt,
            record.experimentId,
            record.componentId,
            record.position
        );
    }

    static async getComponents(uuid) {
        return new Promise((resolve, reject) => {
          Knex.select('componentId', 'position')
          .from('experiment_components')
          .where('experimentId', '=', uuid)
          .then((rows) => {
            const components = rows.map((r) => {
              return this.fromDBRecord(r);
            });
            resolve(Promise.all(components));
          })
          .catch((err) => {
            reject(err);
          });
        });
      }
}

export default Components;
