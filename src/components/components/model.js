import { Knex } from '../../config';

class Component {
  constructor(uuid, createdAt, updatedAt, name) {
    this.uuid = uuid;
    this.createdAt = createdAt;
    this.updatedAt = updatedAt;
    this.name = name;
  }

  static fromDBRecord(record) {
    return new this(
      record.uuid,
      record.createdAt,
      record.updatedAt,
      record.name
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

  async update(updatedAt, name) {
    const componentUpdatedAt = updatedAt || this.updatedAt;
    const componentName = name || this.name;

    return new Promise((resolve, reject) => {
      Knex.update({
        updatedAt: componentUpdatedAt,
        name: componentName,
      })
        .from('components')
        .where('uuid', '=', this.uuid)
        .then(() => {
          this.updatedAt = componentUpdatedAt;
          this.name = componentName;
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
          const component = rows.map((r) => {
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
            resolve(this.fromDBRecord(row));
          }
          reject(Error('Invalid UUID.'));
        })
        .catch((err) => {
          reject(err);
        });
    });
  }
}

export default Component;
