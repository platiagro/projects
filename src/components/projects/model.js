import { Knex } from '../../config';
import { ExperimentModel } from '../experiments';

class Project {
  constructor(uuid, name, createdAt) {
    this.uuid = uuid;
    this.name = name;
    this.createdAt = createdAt;
    this.experimentsList = [];
  }

  static async fromDBRecord(record) {
    const project = new this(record.uuid, record.name, record.createdAt);
    await project.experiments();
    return project;
  }

  static async getById(uuid) {
    return new Promise((resolve, reject) => {
      Knex.select('*')
        .from('projects')
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

  static async getAll() {
    return new Promise((resolve, reject) => {
      Knex.select('*')
        .from('projects')
        .orderBy('createdAt', 'desc')
        .then((rows) => {
          const projects = rows.map((r) => {
            return this.fromDBRecord(r);
          });
          Promise.all(projects).then((result) => {
            resolve(result);
          });
        })
        .catch((err) => {
          reject(err);
        });
    });
  }

  async experiments() {
    await ExperimentModel.getAllByProjectId(this.uuid).then((experiments) => {
      this.experimentsList = experiments;
    });
  }

  static async create(uuid, name, createdAt) {
    return new Promise((resolve, reject) => {
      Knex.insert({
        uuid,
        name,
        createdAt,
      })
        .into('projects')
        .then(() => {
          resolve(this.fromDBRecord({ uuid, name, createdAt }));
        })
        .catch((err) => {
          reject(err);
        });
    });
  }

  async update(newName) {
    const projectName = newName || this.name;

    return new Promise((resolve, reject) => {
      Knex.update({ name: projectName })
        .from('projects')
        .where('uuid', '=', this.uuid)
        .then(() => {
          this.name = projectName;
          resolve(this);
        })
        .catch((err) => {
          reject(err);
        });
    });
  }
}

export default Project;
