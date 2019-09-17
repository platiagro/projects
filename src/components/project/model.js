import { Knex } from '../../config';
import knex from '../../config/knex';

const createProjectStore = async (uuid, name, createdAt) => {
  return new Promise((resolve, reject) => {
    Knex('projects')
      .insert({
        UUID: uuid,
        Name: name,
        CreatedAt: createdAt,
      })
      .then(() => {
        resolve({ uuid, name, createdAt });
      })
      .catch((err) => {
        reject(err);
      })
      .finally(() => {
        knex.destroy();
      });
  });
};

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
    return createProjectStore(uuid, name, createdAt)
      .then((record) => {
        return this.fromDBRecord(record);
      })
      .catch((err) => {
        throw new Error(err);
      });
  }
}

export default Project;
