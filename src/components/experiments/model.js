import { Knex } from '../../config';

class Experiment {
  constructor(
    uuid,
    name,
    projectId,
    pipelineIdTrain,
    pipelineIdDeploy,
    datasetId,
    targetColumnId,
    parameters,
    createdAt,
    position
  ) {
    this.uuid = uuid;
    this.name = name;
    this.projectId = projectId;
    this.pipelineIdTrain = pipelineIdTrain;
    this.pipelineIdDeploy = pipelineIdDeploy;
    this.datasetId = datasetId;
    this.targetColumnId = targetColumnId;
    this.parameters = parameters;
    this.createdAt = createdAt;
    this.position = position;
  }

  static fromDBRecord(record) {
    return new this(
      record.uuid,
      record.name,
      record.projectId,
      record.pipelineIdTrain,
      record.pipelineIdDeploy,
      record.datasetId,
      record.targetColumnId,
      record.parameters,
      record.createdAt,
      record.position
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
        .whereNotNull('position')
        .andWhere('projectId', '=', projectId)
        .orderBy('position')
        .then((rows) => {
          const experiments = rows.map((r) => {
            return this.fromDBRecord(r);
          });
          resolve(Promise.all(experiments));
        })
        .catch((err) => {
          reject(err);
        });
    });
  }

  async reorder(newPosition) {
    return new Promise((resolve) => {
      Experiment.getAllByProjectId(this.projectId).then((experiments) => {
        const experimentsFiltered = experiments.filter((e) => {
          return e.uuid !== this.uuid;
        });
        experimentsFiltered.splice(newPosition, 0, this);
        const result = experimentsFiltered.map((experiment, index) => {
          return experiment.update(null, null, null, null, null, index);
        });
        Promise.all(result).then(() => {
          resolve();
        });
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
          resolve(
            this.fromDBRecord({
              uuid,
              name,
              projectId,
              createdAt,
              position: 0,
            })
          );
        })
        .catch((err) => {
          reject(err);
        });
    });
  }

  async update(
    newName,
    newPipelineIdTrain,
    newPipelineIdDeploy,
    newDatasetId,
    newTargetColumnId,
    newParameters,
    newPosition
  ) {
    const name = newName || this.name;
    const pipelineIdTrain = newPipelineIdTrain || this.pipelineIdTrain;
    const pipelineIdDeploy = newPipelineIdDeploy || this.pipelineIdDeploy;
    const datasetId = newDatasetId || this.datasetId;
    const targetColumnId = newTargetColumnId || this.targetColumnId;
    const parameters = newParameters || this.parameters;
    let position;
    if (newPosition === undefined || newPosition === null) {
      position = this.position;
    } else {
      position = newPosition;
    }

    return new Promise((resolve, reject) => {
      Knex.update({
        name,
        pipelineIdTrain,
        pipelineIdDeploy,
        datasetId,
        targetColumnId,
        parameters,
        position,
      })
        .from('experiments')
        .where('uuid', '=', this.uuid)
        .then(() => {
          this.name = name;
          this.pipelineIdTrain = pipelineIdTrain;
          this.pipelineIdDeploy = pipelineIdDeploy;
          this.datasetId = datasetId;
          this.targetColumnId = targetColumnId;
          this.parameters = parameters;
          this.position = position;
          resolve(this);
        })
        .catch((err) => {
          reject(err);
        });
    });
  }
}

export default Experiment;
