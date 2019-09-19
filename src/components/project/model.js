import { Knex } from '../../config';

class Project {
  constructor(uuid, name, createdAt) {
    this.uuid = uuid;
    this.name = name;
    this.createdAt = createdAt;
  }

  static fromDBRecord(record) {
    return new this(record.uuid, record.name, record.createdAt);
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
        .then((rows) => {
          const projects = rows.map((r) => {
            return this.fromDBRecord(r);
          });
          resolve(projects);
        })
        .catch((err) => {
          reject(err);
        });
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
    return new Promise((resolve, reject) => {
      Knex.update({ name: newName })
        .from('projects')
        .where('uuid', '=', this.uuid)
        .then(() => {
          this.name = newName;
          resolve();
        })
        .catch((err) => {
          reject(err);
        });
    });
  }
}

export default Project;
