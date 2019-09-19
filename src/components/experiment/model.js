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
