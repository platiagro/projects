import { Knex } from '../../config';

class Experiment {
  constructor(
    uuid,
    name,
    projectId,
    pipelineId,
    datasetId,
    targetColumnId,
    parameters,
    createdAt
  ) {
    this.uuid = uuid;
    this.name = name;
    this.projectId = projectId;
    this.pipelineId = pipelineId;
    this.datasetId = datasetId;
    this.targetColumnId = targetColumnId;
    this.parameters = parameters;
    this.createdAt = createdAt;
  }

  static fromDBRecord(record) {
    return new this(
      record.uuid,
      record.name,
      record.projectId,
      record.pipelineId,
      record.datasetId,
      record.targetColumnId,
      record.parameters,
      record.createdAt
    );
  }

  static async getById(uuid) {
    return new Promise((resolve, reject) => {
      Knex.select('*')
        .from('experiments')
        .where('uuid', '=', uuid)
        .first()
        .then((row) => {
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

  static async getAllByProjectId(projectId) {
    return new Promise((resolve, reject) => {
      Knex.select('*')
        .from('experiments')
        .where('projectId', '=', projectId)
        .then((rows) => {
          const experiments = rows.map((r) => {
            return this.fromDBRecord(r);
          });
          resolve(experiments);
        })
        .catch((err) => {
          reject(err);
        });
    });
  }

  static async create(uuid, name, projectId, createdAt) {
    return new Promise((resolve, reject) => {
      Knex.insert({
        uuid,
        name,
        projectId,
        createdAt,
      })
        .into('experiments')
        .then(() => {
          resolve(this.fromDBRecord({ uuid, name, projectId, createdAt }));
        })
        .catch((err) => {
          reject(err);
        });
    });
  }
}

export default Experiment;
