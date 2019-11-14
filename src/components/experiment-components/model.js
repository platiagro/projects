import { Knex } from '../../config';

class ExperimentComponents {
  constructor(uuid, createdAt, experimentId, componentId, position) {
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

  static async getById(uuid) {
    return new Promise((resolve, reject) => {
      Knex.select('*')
        .from('experiment_components')
        .where('uuid', '=', uuid)
        .first()
        .then(async (row) => {
          if (row) {
            resolve(this.fromDBRecord(row));
          }
          reject(Error('Invalid UUID.'));
        })
        .catch((err) => {
          reject(err);
        });
    });
  }

  static async getAll(experimentId) {
    return new Promise((resolve, reject) => {
      Knex.select('uuid', 'position')
        .from('experiment_components')
        .where('experimentId', '=', experimentId)
        .orderBy('position')
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

  static async create(uuid, experimentId, componentId, createdAt, position) {
    return new Promise((resolve, reject) => {
      Knex.insert({
        uuid,
        experimentId,
        componentId,
        createdAt,
        position,
      })
        .into('experiment_components')
        .then(() => {
          resolve(
            this.fromDBRecord({
              uuid,
              experimentId,
              componentId,
              createdAt,
              position,
            })
          );
        })
        .catch((err) => {
          reject(err);
        });
    });
  }

  async update(newExperimentId, newComponentId, newPosition) {
    const experimentId =
      newExperimentId !== undefined ? newExperimentId : this.experimentId;
    const componentId =
      newComponentId !== undefined ? newComponentId : this.componentId;
    const position = newPosition !== undefined ? newPosition : this.position;

    return new Promise((resolve, reject) => {
      Knex.update({
        experimentId,
        componentId,
        position,
      })
        .from('experiment_components')
        .where('uuid', '=', this.uuid)
        .then(() => {
          this.experimentId = experimentId;
          this.componentId = componentId;
          this.position = position;
          resolve(this);
        })
        .catch((err) => {
          reject(err);
        });
    });
  }

  async delete() {
    return new Promise((resolve, reject) => {
      Knex.delete()
        .from('experiment_components')
        .where('uuid', '=', this.uuid)
        .then(() => {
          resolve(true);
        })
        .catch((err) => {
          reject(err);
        });
    });
  }
}

export default ExperimentComponents;
