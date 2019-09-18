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

  static async create(uuid, name, createdAt) {
    return new Promise((resolve, reject) => {
      Knex.insert({
        UUID: uuid,
        Name: name,
        CreatedAt: createdAt,
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
}

export default Project;
