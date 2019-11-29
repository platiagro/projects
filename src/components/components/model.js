import { Knex } from '../../config';
import config from '../../config/config';
import { MinioModel } from '../minio';

class Component {
  constructor(uuid, createdAt, updatedAt, name, parameters, file) {
    this.uuid = uuid;
    this.createdAt = createdAt;
    this.updatedAt = updatedAt;
    this.name = name;
    this.parameters = parameters;
    this.file = file;
  }

  static fromDBRecord(record) {
    let jsonParameters;
    if (record.parameters) {
      jsonParameters = JSON.parse(record.parameters);
    }

    return new this(
      record.uuid,
      record.createdAt,
      record.updatedAt,
      record.name,
      jsonParameters,
      record.file
    );
  }

  static async create(uuid, createdAt, name) {
    return new Promise((resolve, reject) => {
      Knex.insert({
        uuid,
        createdAt,
        name,
      })
        .into('components')
        .then(() => {
          resolve(
            this.fromDBRecord({
              uuid,
              createdAt,
              name,
            })
          );
        })
        .catch((err) => {
          reject(err);
        });
    });
  }

  async update(updatedAt, name, parameters) {
    let stringParamenters;
    if (this.parameters) {
      stringParamenters = JSON.stringify(this.parameters);
    }

    const componentUpdatedAt = updatedAt || this.updatedAt;
    const componentName = name || this.name;
    const componentParameters = parameters || stringParamenters;

    return new Promise((resolve, reject) => {
      Knex.update({
        updatedAt: componentUpdatedAt,
        name: componentName,
        parameters: componentParameters,
      })
        .from('components')
        .where('uuid', '=', this.uuid)
        .then(() => {
          this.updatedAt = componentUpdatedAt;
          this.name = componentName;
          this.parameters = componentParameters
            ? JSON.parse(componentParameters)
            : componentParameters;
          resolve(this);
        })
        .catch((err) => {
          reject(err);
        });
    });
  }

  static async deleteById(uuid) {
    return new Promise((resolve, reject) => {
      Knex('components')
        .where('uuid', '=', uuid)
        .del()
        .then((count) => {
          if (count) {
            resolve(count);
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
        .from('components')
        .orderBy('createdAt', 'desc')
        .then((rows) => {
          const component = rows.map(async (r) => {
            r.file = await this.getMinioFile(r);
            return this.fromDBRecord(r);
          });
          Promise.all(component).then((result) => {
            resolve(result);
          });
        })
        .catch((err) => {
          reject(err);
        });
    });
  }

  static async getById(uuid) {
    return new Promise((resolve, reject) => {
      Knex.select('*')
        .from('components')
        .where('uuid', '=', uuid)
        .first()
        .then(async (row) => {
          if (row) {
            row.file = await this.getMinioFile(row);
            resolve(this.fromDBRecord(row));
          }
          reject(Error('Invalid UUID.'));
        })
        .catch((err) => {
          reject(err);
        });
    });
  }

  static async getMinioFile(record) {
    const files = await MinioModel.getFiles(
      config.MINIO_BUCKET,
      `components/${record.uuid}`
    );

    if (files && files.length > 0) {
      return `s3://${config.MINIO_BUCKET}/${files[0].name}`;
    }
    return '';
  }
}

export default Component;
