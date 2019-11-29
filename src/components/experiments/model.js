import { Knex } from '../../config';
import { ExperimentComponentsModel } from '../experiment-components';
import ExperimentComponents from '../experiment-components/model';

class Experiment {
  constructor(
    uuid,
    name,
    projectId,
    pipelineIdTrain,
    pipelineIdDeploy,
    datasetId,
    headerId,
    targetColumnId,
    parameters,
    createdAt,
    runId,
    runStatus,
    template,
    position,
    componentsList
  ) {
    this.uuid = uuid;
    this.name = name;
    this.projectId = projectId;
    this.pipelineIdTrain = pipelineIdTrain;
    this.pipelineIdDeploy = pipelineIdDeploy;
    this.datasetId = datasetId;
    this.headerId = headerId;
    this.targetColumnId = targetColumnId;
    this.parameters = parameters;
    this.createdAt = createdAt;
    this.runId = runId;
    this.runStatus = runStatus;
    this.template = template;
    this.position = position;
    this.componentsList = componentsList;
  }

  static fromDBRecord(record) {
    return new this(
      record.uuid,
      record.name,
      record.projectId,
      record.pipelineIdTrain,
      record.pipelineIdDeploy,
      record.datasetId,
      record.headerId,
      record.targetColumnId,
      record.parameters,
      record.createdAt,
      record.runId,
      record.runStatus,
      record.template,
      record.position,
      record.componentsList
    );
  }

  static async getById(uuid) {
    return new Promise((resolve, reject) => {
      Knex.select('*')
        .from('experiments')
        .where('uuid', '=', uuid)
        .first()
        .then(async (row) => {
          if (row) {
            const record = row;
            record.componentsList = await ExperimentComponentsModel.getAll(
              uuid
            );
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
          const experiments = rows.map(async (r) => {
            r.componentsList = await ExperimentComponents.getAll(r.uuid);
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
          return experiment.update(
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            index
          );
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
    newHeaderId,
    newTargetColumnId,
    newParameters,
    newRunId,
    newRunStatus,
    newTemplate,
    newPosition
  ) {
    const name = newName || this.name;
    const pipelineIdTrain =
      newPipelineIdTrain !== undefined
        ? newPipelineIdTrain
        : this.pipelineIdTrain;
    const pipelineIdDeploy =
      newPipelineIdDeploy !== undefined
        ? newPipelineIdDeploy
        : this.pipelineIdDeploy;
    const datasetId =
      newDatasetId !== undefined ? newDatasetId : this.datasetId;
    const headerId = newHeaderId !== undefined ? newHeaderId : this.headerId;
    const targetColumnId =
      newTargetColumnId !== undefined ? newTargetColumnId : this.targetColumnId;
    const parameters =
      newParameters !== undefined ? newParameters : this.parameters;
    const runId = newRunId !== undefined ? newRunId : this.runId;
    const runStatus =
      newRunStatus !== undefined ? newRunStatus : this.runStatus;
    const template = newTemplate !== undefined ? newTemplate : this.template;

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
        headerId,
        targetColumnId,
        parameters,
        runId,
        runStatus,
        template,
        position,
      })
        .from('experiments')
        .where('uuid', '=', this.uuid)
        .then(() => {
          this.name = name;
          this.pipelineIdTrain = pipelineIdTrain;
          this.pipelineIdDeploy = pipelineIdDeploy;
          this.datasetId = datasetId;
          this.headerId = headerId;
          this.targetColumnId = targetColumnId;
          this.parameters = parameters;
          this.runId = runId;
          this.runStatus = runStatus;
          this.template = template;
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
